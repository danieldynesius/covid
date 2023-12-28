import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as offline
import math
from plotly.subplots import make_subplots
import numpy as np


datapath = '~/code/analytics/covid/data/2_staged_data/'
final_datapath ='~/code/analytics/covid/data/3_finalized_data/'


# Fill all missing weeks attempt. Set to false is more Concise. set to true is more Complete.
fill_missing_weeks = False

d1 = pd.read_parquet(os.path.join(datapath, 'france_wastewater.parquet'))
d2 = pd.read_parquet(os.path.join(datapath, 'sweden_wastewater.parquet'))
d3 = pd.read_parquet(os.path.join(datapath, 'netherlands_wastewater.parquet')) 
d4 = pd.read_parquet(os.path.join(datapath, 'denmark_wastewater.parquet')) #fail 1 makes html huge
d5 = pd.read_parquet(os.path.join(datapath, 'austria_wastewater.parquet'))
d6 = pd.read_parquet(os.path.join(datapath, 'poland_wastewater.parquet')) # this is just Poznan County. Normaized Value must be
d7 = pd.read_parquet(os.path.join(datapath, 'finland_wastewater.parquet'))
d8 = pd.read_parquet(os.path.join(datapath, 'switzerland_wastewater.parquet'))
d9 = pd.read_parquet(os.path.join(datapath, 'canada_wastewater.parquet'))


df = pd.concat([d1, d2, d3, d4, d5, d6, d7, d8, d9],ignore_index=True)
df = df[['first_day', 'region', 'cntr_code','value', 'normalized_value']]

df.groupby('cntr_code')['region'].agg('nunique')


if fill_missing_weeks == True:
    ## DD ADD ALL WEEKS
    # Assuming 'date' is the column containing dates
    date_min = df['date'].min()
    date_max = df['date'].max()

    # Create a DataFrame to represent all possible dates within the range
    all_dates = pd.date_range(start=date_min, end=date_max, freq='D')
    all_dates_df = pd.DataFrame({'date': all_dates})

    # Create a Cartesian product of 'region' and 'date'
    cartesian_product = pd.MultiIndex.from_product([df['region'].unique(), all_dates], names=['region', 'date'])
    result_df = pd.DataFrame(index=cartesian_product).reset_index()

    # Merge with the original DataFrame to fill in missing values
    result_df = result_df.merge(df, on=['region', 'date'], how='left')

    # Add a flag column indicating whether the datapoint is added (1) or existed already (0)
    result_df['synthethic_datapoint_flg'] = result_df['week'].isna().astype(int)
    #result_df[result_df['synthethic_datapoint_flg']==1].value = -1
    result_df.loc[result_df.synthethic_datapoint_flg == 1, ['value']] = np.nan #-1 #np.nan

    # Fill NaN values in other columns if needed
    #result_df = result_df.fillna({'other_column': default_value})
    result_df['week'] = result_df['date'].dt.strftime('%Y-%V')


    # If you want to sort the resulting DataFrame by 'region' and 'date', you can do:
    result_df = result_df.sort_values(by=['cntr_code','region', 'date']).reset_index(drop=True)
    #df = result_df[['region','week', 'value']]

    result_df = result_df.drop_duplicates()
    df = result_df
    # Now, result_df contains the DataFrame with missing dates filled for each region
    # The 'flag' column indicates whether the datapoint is added or existed already

else:
    df = df

def make_region_subplots(df):
    df.dropna(subset=['region'], inplace=True) # drop nan in region value
    df.sort_values(by=['cntr_code','region', 'first_day'], inplace=True)
    unique_areas = list(df.region.unique())

    plot_titles = list((df.cntr_code.str.upper() +' - '+ df.region.str.title()).unique())


    n_unique_areas = len(unique_areas)
    n_cols_for_output = 4 # user specified
    n_rows_for_output = math.ceil(n_unique_areas/n_cols_for_output) # needed based on n areas in data

    df = df[['first_day', 'region', 'cntr_code', 'value', 'normalized_value']]

    fig = make_subplots(
        rows=n_rows_for_output, cols=n_cols_for_output,
        y_title='Covid Transmission Value',
        subplot_titles=plot_titles
    )

    for i, area in enumerate(unique_areas, start=1):
        print(i,'....' ,area)
        area_lowercase = area.lower()

        row_num = (i - 1) // n_cols_for_output + 1
        col_num = (i - 1) % n_cols_for_output + 1
        print('Current area:', area, 'RC:',row_num, col_num)
        area_x_series = df[df['region'].str.lower() == area_lowercase].first_day
        area_y_series = df[df['region'].str.lower() == area_lowercase].value

        area_x_series_last365 = df[(df['region'].str.lower() == area_lowercase) ].first_day
        area_y_series_last365 = df[(df['region'].str.lower() == area_lowercase) ].value

        fig.add_trace(
            go.Scatter(
                x=area_x_series
                ,y=area_y_series
                #,y=test_list
                ,mode='lines+markers'
                ,connectgaps=True
                ,showlegend=False
            ),
            row=row_num, col=col_num
        )

    fig.update_layout(
        height=300 + (50*n_unique_areas), width=300*n_cols_for_output,  # Adjust width to accommodate all subplots
        title_text="Covid-19 Wastewater Measurements"
    )
    fig.update_xaxes(tickangle=45, tickfont=dict(family='Rockwell', color='black', size=14))

    return fig


fig = make_region_subplots(df)
fig.show()


#############################


fig1 = px.line(df[df.cntr_code=='CH'], x="first_day", y="value", color='region', title='Switzerland')
fig2 = px.line(df[df.cntr_code=='SE'], x="first_day", y="value", color='region', title='Sweden')

fig2.show()


html_filename = './your_plot.html'
offline.plot(fig1, filename=html_filename, auto_open=True)

"""
with open('./p_graph.html', 'a') as f:
    f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write(fig2.to_html(full_html=False, include_plotlyjs='cdn'))
"""    