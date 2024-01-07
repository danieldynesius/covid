import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as offline
import math
from plotly.subplots import make_subplots
import numpy as np
import os
import configparser

config_file = '/home/stratega/code/analytics/covid/conf.ini'

# Read the Conf file
config = configparser.ConfigParser()
config.read(config_file)

# Data Params
staged_datapath = config.get('Paths', 'staged_datapath')
final_datapath = config.get('Paths', 'final_datapath')
save_trend_dir_gh = config.get('Paths', 'save_trend_dir_gh')
save_trend_filepath_gh = os.path.join(save_trend_dir_gh, 'country_trends.html')

save_trend_dir_bb = config.get('Paths', 'save_trend_dir_bb')
save_trend_filepath_bb = os.path.join(save_trend_dir_bb, 'country_trends.html')


#staged_datapath = '~/code/analytics/covid/data/2_staged_data/'
#final_datapath ='~/code/analytics/covid/data/3_finalized_data/'


# Fill all missing weeks attempt. Set to false is more Concise. set to true is more Complete.
fill_missing_weeks = False

d1 = pd.read_parquet(os.path.join(staged_datapath, 'france_wastewater.parquet'))
d2 = pd.read_parquet(os.path.join(staged_datapath, 'sweden_wastewater.parquet'))
d3 = pd.read_parquet(os.path.join(staged_datapath, 'netherlands_wastewater.parquet')) 
d4 = pd.read_parquet(os.path.join(staged_datapath, 'denmark_wastewater.parquet')) #fail 1 makes html huge. Due to geofile probably.
d5 = pd.read_parquet(os.path.join(staged_datapath, 'austria_wastewater.parquet'))
d6 = pd.read_parquet(os.path.join(staged_datapath, 'poland_wastewater.parquet')) # this is just Poznan County. Normaized Value must be
d7 = pd.read_parquet(os.path.join(staged_datapath, 'finland_wastewater.parquet'))
d8 = pd.read_parquet(os.path.join(staged_datapath, 'switzerland_wastewater.parquet'))
d9 = pd.read_parquet(os.path.join(staged_datapath, 'canada_wastewater.parquet'))
d10 =pd.read_parquet(os.path.join(staged_datapath, 'usa_wastewater.parquet'))
d11 =pd.read_parquet(os.path.join(staged_datapath, 'newzealand_wastewater.parquet'))
d12 =pd.read_parquet(os.path.join(staged_datapath, 'germany_wastewater.parquet'))

# Concatenate DataFrames
df = pd.DataFrame(pd.concat([d1, d2, d3, d4, d5, d6, d7, d8, d9, d10, d11, d12], ignore_index=True))
df = df[['first_day', 'region', 'cntr_code', 'cntr_nm','value', 'normalized_value', 'metric_nm']]

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

df.dropna(subset=['region'], inplace=True) # drop nan in region value
df.dropna(subset=['cntr_nm'], inplace=True) # drop nan in country 
df.sort_values(by=['cntr_nm','region', 'first_day'], inplace=True)


########################################################################
# Subplots. Old method (Too many regions)
########################################################################
def make_region_subplots(df):
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




########################################################################
# List of Trend Graphs 
########################################################################
country_list = list(df.cntr_nm.unique())
df['region'] = df.region.astype(str).str.title()

files_to_remove = [save_trend_filepath_bb, save_trend_filepath_gh]
for file in files_to_remove:
    trend_html_filepath = file

    try:
        os.remove(trend_html_filepath)
        print(trend_html_filepath, 'removed')
    except FileNotFoundError:
        print(trend_html_filepath, 'does not exist')
    except Exception as e:
        print(f"An error occurred: {e}")

for i, country in enumerate(country_list, start=1):
    print(i, ':', country.title())
    current_fig = px.line(df[df.cntr_nm == country], x="first_day", y="value", color='region', title=country.title()+' Wastewater Measurements')
    # Update the y-axis label
    current_fig.update_yaxes(title_text=df[df.cntr_nm == country].metric_nm.iloc[0])
    #current_fig.update_xaxes(title_text='first_day(of week)')
    current_fig.update_layout(coloraxis_colorbar_title='Region',
                            title_font=dict(size=28),
                            xaxis_title_font=dict(size=22),
                            yaxis_title_font=dict(size=26),
                            legend_title_font=dict(size=22),
                            xaxis_tickfont=dict(size=22),
                            yaxis_tickfont=dict(size=22),
                            legend_font=dict(size=22)
                            )

    # Set font size for everything in the hover tooltip to size 22
    current_fig.update_traces(
        textfont=dict(size=22),
        )
    

    ### put figs into 1 graph
    with open(trend_html_filepath, 'a') as f:
        f.write(current_fig.to_html(full_html=False, include_plotlyjs='cdn'))

    with open(save_trend_filepath_bb, 'a') as f:
        f.write(current_fig.to_html(full_html=False, include_plotlyjs='cdn'))        

