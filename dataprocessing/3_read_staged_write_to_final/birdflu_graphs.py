import pandas as pd
import plotly.express as px
import os
import configparser
from datetime import datetime, timedelta 

# Read the configuration file
config_file = os.path.expanduser('~/code/analytics/covid/conf.ini')
config = configparser.ConfigParser()
config.read(config_file)

# Data Params
datapath = config.get('Paths', 'datapath')
staged_datapath = config.get('Paths', 'staged_datapath')
save_trend_dir_gh = config.get('Paths', 'save_trend_dir_gh')
save_trend_filepath_gh = os.path.join(save_trend_dir_gh, 'country_trends_birdflu.html')
save_trend_dir_bb = config.get('Paths', 'save_trend_dir_bb')
save_trend_filepath_bb = os.path.join(save_trend_dir_bb, 'country_trends_birdflu.html')


# Get today's date
today = datetime.today().date()

# Calculate start_date (today - 91 days) and end_date (today - 1 day)
start_date = (today - timedelta(days=91)).strftime('%Y-%m-%d')
end_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')

# Read existing data from Parquet file
existing_df = pd.read_parquet(f'{datapath}/1_raw_birdflu/raw_birdflu.parquet')

# Construct URL for API call
url = f"https://europe-west1-fao-empresi.cloudfunctions.net/getLatestEventsByDate?animal_type=all&diagnosis_status=all&disease=avian_influenza&end_date={end_date}&start_date={start_date}"

# Fetch new data from API
new_df = pd.read_csv(url, sep=',')

# Combine existing and new data
combined_df = pd.concat([existing_df, new_df])

# Remove duplicates, keeping the latest version of each unique record
deduped_df = combined_df.sort_values('observation_date').drop_duplicates(subset=['id_event'], keep='last')

# Save updated data back to Parquet file
deduped_df.to_parquet(f'{datapath}/1_raw_birdflu/raw_birdflu.parquet', index=False)

print('Nr of new rows added:', len(deduped_df) - len(existing_df))

# Update the working DataFrame
df = deduped_df

df = df[['disease','country','observation_date','diagnosis_status','humans_affected', 'humans_deaths']]
df = df[df.disease=='Influenza - Avian']
df.drop('disease', axis=1, inplace=True)

country_dict = {
    'Russian Federation': 'Russia', 'Viet Nam': 'Vietnam', 'Iran  (Islamic Republic of)': 'Iran',
    'Moldova, Republic of': 'Moldova',    
    "Lao People's Democratic Republic": 'Laos',
    'U.K. of Great Britain and Northern Ireland': 'UK',
    'Republic of Korea': 'South Korea',
    'Bosnia and Herzegovina': 'Bosnia & Herze', 'Hong Kong, SAR': 'HKG', 'United States of America': 'USA',
    'Taiwan (Province of China)': 'Taiwan',
    'Svalbard and Jan Mayen Islands': 'Svalbad',
    'South Georgia and the South Sandwich Islands': 'South Georgia',
    'Falkland Islands (Malvinas)': 'Falkland Islands'
}

# Overwrite the 'country' column with the short names
df['country'] = df['country'].map(country_dict).fillna(df['country'])

# Print out any countries that weren't in the dictionary
missing_countries = df[~df['country'].isin(country_dict.values())]['country'].unique()
if len(missing_countries) > 0:
    print("Countries not converted to short names:", missing_countries, '\n')

df['observation_date'] = pd.to_datetime(df['observation_date'], format='%Y-%m-%d').dt.date

grouped_df = df.groupby(by=['country', 'observation_date', 'diagnosis_status']).size().reset_index(name='count')
grouped_df['observation_date'] = pd.to_datetime(grouped_df['observation_date'])
grouped_df['year'] = grouped_df['observation_date'].dt.year

# Create line chart with country selector

def create_line_chart(grouped_df):
    # Ensure observation_date is datetime
    grouped_df['observation_date'] = pd.to_datetime(grouped_df['observation_date'])
    
    # Create the line chart
    fig = px.line(grouped_df, x='observation_date', y='count', color='country', 
                  title='Reported Cases by Country & Observation Date',
                  hover_data={'observation_date': ':%Y-%m-%d'})

    # Update layout for x-axis
    fig.update_xaxes(
        dtick="M3",
        tickformat="%b",
        ticklabelmode="period",
    )

    # Add year annotations
    years = grouped_df['observation_date'].dt.year.unique()
    for year in years:
        fig.add_annotation(x=f"{year}-07-01", y=-0.15, text=str(year), 
                           showarrow=False, xref="x", yref="paper")

    # Update layout for overall appearance
    fig.update_layout(
        height=500, width=900
        ,xaxis_title="" # "Date"
        ,yaxis_title="Number of Cases",
    )
    
    return fig


# Use the function to create the line chart
fig1 = create_line_chart(grouped_df)
#fig1.show()

# Function to create bar chart
def update_graph(selected_year):
    if selected_year == 'All Years':
        filtered_df = grouped_df
    else:
        filtered_df = grouped_df[grouped_df['year'] == selected_year]
    
    country_totals = filtered_df.groupby('country')['count'].sum().reset_index()
    country_totals = country_totals.sort_values('count', ascending=False)
    
    fig = px.bar(country_totals, x='country', y='count', 
                 title=f'Total Reported Cases by Country ({selected_year})',
                 labels={'count': 'Number of Cases', 'country': 'Country'},
                 color='count',
                 color_continuous_scale='YlOrRd')
    
    fig.update_layout(
        xaxis_title="Country",
        yaxis_title="Number of Cases",
        xaxis_tickangle=-45,
        height=500,
        width=900
    )
    
    return fig

# Create initial bar chart
years = ['All Years'] + sorted(grouped_df['year'].unique().tolist(), reverse=True)
fig2 = update_graph('All Years')
#fig2.show()

# Add dropdown for year selection
fig2.update_layout(
    updatemenus=[
        dict(
            buttons=[
                dict(label=str(year),
                     method='update',
                     args=[{'x': [update_graph(year).data[0].x],
                            'y': [update_graph(year).data[0].y]},
                           {'title': f'Total Reported Cases by Country ({year})'}])
                for year in years
            ],
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.1,
            xanchor="left",
            y=1.15,
            yanchor="top"
        ),
    ]
)

# Save both figures to a single HTML file
with open(save_trend_filepath_gh, "w") as f:
    f.write("<html><head><title>Bird Flu Cases Analysis</title></head><body>")
    f.write("<h1>Bird Flu Cases Analysis</h1>")
    f.write("<div style='max-height: 500px; min-height: 300px;'>")
    f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write("</div>")
    f.write("<div style='max-height: 500px; min-height: 300px;'>")
    f.write(fig2.to_html(full_html=False, include_plotlyjs=False))
    f.write("</div>")
    f.write("</body></html>")

print(f"HTML file '{save_trend_filepath_gh}' has been created.")

with open(save_trend_filepath_bb, "w") as f:
    f.write("<html><head><title>Bird Flu Cases Analysis</title></head><body>")
    f.write("<h1>Bird Flu Cases Analysis</h1>")
    f.write("<div style='max-height: 500px; min-height: 300px;'>")
    f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write("</div>")
    f.write("<div style='max-height: 500px; min-height: 300px;'>")
    f.write(fig2.to_html(full_html=False, include_plotlyjs=False))
    f.write("</div>")
    f.write("</body></html>")


print(f"HTML file '{save_trend_filepath_bb}' has been created.")
