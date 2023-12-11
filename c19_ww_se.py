import pandas as pd
import datetime
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime as dt
from plotly.io import write_image
import math
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

# # Knivsta, Vaxholm and Österåker.
# Göteborg, Malmö and Stockholm-Käppala
#/home/stratega/Documents/code/data/timeseries/covid/COVID-19_rioolwaterdata.csv
wastewater_data = pd.read_csv(
    "https://blobserver.dc.scilifelab.se/blob/SLU_wastewater_data.csv",
    sep=",",
)
wastewater_data["year"] = (wastewater_data["week"].str[:4]).astype(int)
wastewater_data["week_no"] = wastewater_data["week"].str[-3:]
wastewater_data["week_no"] = wastewater_data["week_no"].str.replace("*", "", regex=False)
wastewater_data["week_no"] = (wastewater_data["week_no"].str.replace("-", "", regex=False)).astype(int)
wastewater_data["week"] = (wastewater_data["week"].str.replace("*", "", regex=False)) #DD


# set the date to the start of the week (Monday)
wastewater_data["day"] = 1
wastewater_data["date"] = wastewater_data.apply(
    lambda row: dt.fromisocalendar(row["year"], row["week_no"], row["day"]), axis=1
)
# The below accomodates a change in the column title for the COVID data
wastewater_data.rename(
    columns={
        "SARS-CoV2/PMMoV x 1000": "relative_copy_number",
    },
    inplace=True,
)

# Fill all missing weeks attempt
fill_missing_weeks = False

if fill_missing_weeks == True:
    ## DD ADD ALL WEEKS
    # Assuming 'date' is the column containing dates
    date_min = wastewater_data['date'].min()
    date_max = wastewater_data['date'].max()

    # Create a DataFrame to represent all possible dates within the range
    all_dates = pd.date_range(start=date_min, end=date_max, freq='D')
    all_dates_df = pd.DataFrame({'date': all_dates})

    # Create a Cartesian product of 'channel' and 'date'
    cartesian_product = pd.MultiIndex.from_product([wastewater_data['channel'].unique(), all_dates], names=['channel', 'date'])
    result_df = pd.DataFrame(index=cartesian_product).reset_index()

    # Merge with the original DataFrame to fill in missing values
    result_df = result_df.merge(wastewater_data, on=['channel', 'date'], how='left')

    # Add a flag column indicating whether the datapoint is added (1) or existed already (0)
    result_df['synthethic_datapoint_flg'] = result_df['week'].isna().astype(int)
    #result_df[result_df['synthethic_datapoint_flg']==1].relative_copy_number = -1
    result_df.loc[result_df.synthethic_datapoint_flg == 1, ['relative_copy_number']] = -1

    # Fill NaN values in other columns if needed
    #result_df = result_df.fillna({'other_column': default_value})
    result_df['week'] = result_df['date'].dt.strftime('%Y-%V')


    # If you want to sort the resulting DataFrame by 'channel' and 'date', you can do:
    result_df = result_df.sort_values(by=['channel', 'date']).reset_index(drop=True)
    #df = result_df[['channel','week', 'relative_copy_number']]
    df = result_df

else:
    df = wastewater_data
# Now, result_df contains the DataFrame with missing dates filled for each channel
# The 'flag' column indicates whether the datapoint is added or existed already



## DD TEST
"""
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

app = Dash(__name__)


app.layout = html.Div([
    html.H4('Polotical candidate voting pool analysis'),
    html.P("Select a candidate:"),
    dcc.RadioItems(
        id='candidate', 
        options=["Joly", "Coderre", "Bergeron"],
        value="Coderre",
        inline=True
    ),
    dcc.Graph(id="graph"),
])


@app.callback(
    Output("graph", "figure"), 
    Input("candidate", "value"))
def display_choropleth(candidate):
    df = px.data.election() # replace with your own data source
    geojson = px.data.election_geojson()
    fig = px.choropleth(
        df, geojson=geojson, color=candidate,
        locations="district", featureidkey="properties.district",
        projection="mercator", range_color=[0, 6500])
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig


app.run_server(debug=True)
"""

df.dropna(subset=['channel'], inplace=True)
unique_areas = list(df.channel.unique())


n_unique_areas = len(unique_areas)
n_cols_for_output = 4 # user specified
n_rows_for_output = math.ceil(n_unique_areas/n_cols_for_output) # needed based on n areas in data

fig = make_subplots(
    rows=n_rows_for_output, cols=n_cols_for_output,
    y_title='Relative Copy Number',
    subplot_titles=unique_areas
)

for i, area in enumerate(unique_areas, start=1):
    print(i,'....' ,area)
    area_lowercase = area.lower()

    row_num = (i - 1) // n_cols_for_output + 1
    col_num = (i - 1) % n_cols_for_output + 1
    print('Current area:', area, 'RC:',row_num, col_num)

    #test_list = list(df[df['channel'].str.lower() == area_lowercase].relative_copy_number)
    fig.add_trace(
        go.Scatter(
            x=df[df['channel'].str.lower() == area_lowercase].week
            ,y=df[df['channel'].str.lower() == area_lowercase].relative_copy_number
            #,y=test_list
            ,mode='lines+markers'
            ,connectgaps=True
            ,showlegend=False
        ),
        row=row_num, col=col_num
    )

#df['week'] = pd.to_datetime(df['week'] + '-1', format='%Y-%U-%w')
#ticktext = df['week'].dt.strftime('%Y-%U')  # Format as year-weeknumber

#fig.update_xaxes(ticktext=ticktext)
#fig.update_traces(connectgaps=False)


fig.update_layout(
    height=50*n_unique_areas, width=1200,  # Adjust width to accommodate all subplots
    title_text="Covid-19 Wastewater Sweden"
)

fig.show()                  


"""
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=x,
    y=[10, 20, None, 15, 10, 5, 15, None, 20, 10, 10, 15, 25, 20, 10],
    name = '<b>No</b> Gaps', # Style name/legend entry with html tags
    connectgaps=True # override default to connect the gaps
))
fig.add_trace(go.Scatter(
    x=x,
    y=[5, 15, None, 10, 5, 0, 10, None, 15, 5, 5, 10, 20, 15, 5],
    name='Gaps',
))

fig.show()

import plotly.express as px
import geopandas as gpd

# Load GeoJSON file into a GeoDataFrame
sweden_gdf = gpd.read_file("/home/stratega/Documents/code/data/geo/sweden-counties.geojson")

# Filter data for Uppsala
#uppsala_gdf = sweden_gdf[sweden_gdf['name'] == 'Uppsala']

# Create a choropleth map using Plotly Express
fig = px.choropleth_mapbox(
    df,
    sweden_gdf,
    geojson=sweden_gdf.geometry,
    locations=sweden_gdf.index,
    color="name",
    mapbox_style="carto-positron",
    center={"lat": sweden_gdf.bounds.mean().maxy.mean(), "lon": sweden_gdf.bounds.mean().maxx.mean()},  # Center on Sweden
    zoom=5,
)

# Show the plot
fig.show()

"""