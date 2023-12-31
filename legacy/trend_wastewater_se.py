import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime as dt
from datetime import timedelta
from plotly.io import write_image
import math
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

# Fill all missing weeks attempt. Set to false is more Concise. set to true is more Complete.
fill_missing_weeks = False

wastewater_data = pd.read_csv(
    "https://blobserver.dc.scilifelab.se/blob/SLU_wastewater_data.csv",
    sep=",",
)
#wastewater_data.to_csv('./SLU_wastewater_data.csv', index=False)

wastewater_data["year"] = (wastewater_data["week"].str[:4]).astype(int)
wastewater_data["week_no"] = wastewater_data["week"].str.replace(r"\*$", "", regex=True)
wastewater_data["week"] = wastewater_data["week"].str.replace(r"\*$", "", regex=True)

# Convert week to ISO year and week
wastewater_data[['iso_year', 'iso_week']] = wastewater_data['week'].str.split('-', expand=True)

# Convert ISO year and week to integers
wastewater_data['iso_year'] = wastewater_data['iso_year'].astype(int)
wastewater_data['iso_week'] = wastewater_data['iso_week'].astype(int)

# Define a function to get the first day of the ISO year and week
def get_first_day(row):
    return dt.fromisocalendar(row['iso_year'], row['iso_week'], 1)

# Apply the function to create a new column "first_day"
wastewater_data['date'] = wastewater_data.apply(get_first_day, axis=1)
#wastewater_data = wastewater_data[wastewater_data['channel']=='Östhammar']

# The below accomodates a change in the column title for the COVID data
wastewater_data.rename(
    columns={
        "SARS-CoV2/PMMoV x 1000": "relative_copy_number",
    },
    inplace=True,
)

#grouped = wastewater_data[['channel', 'date']].groupby('channel')
#grouped = grouped.max().reset_index()
fresh_data_cutoff = dt.today() - timedelta(days=365)
common_x_range_start = fresh_data_cutoff
#grouped = grouped[grouped['date'] > fresh_data_cutoff]
#wastewater_data = wastewater_data[wastewater_data.channel.isin(grouped.channel)]
wastewater_data['fresh_data_flg'] = 0
wastewater_data.loc[wastewater_data['date'] >= common_x_range_start, ['fresh_data_flg']] = 1


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
    result_df.loc[result_df.synthethic_datapoint_flg == 1, ['relative_copy_number']] = np.nan #-1 #np.nan

    # Fill NaN values in other columns if needed
    #result_df = result_df.fillna({'other_column': default_value})
    result_df['week'] = result_df['date'].dt.strftime('%Y-%V')


    # If you want to sort the resulting DataFrame by 'channel' and 'date', you can do:
    result_df = result_df.sort_values(by=['channel', 'date']).reset_index(drop=True)
    #df = result_df[['channel','week', 'relative_copy_number']]

    result_df = result_df.drop_duplicates()
    df = result_df
    # Now, result_df contains the DataFrame with missing dates filled for each channel
    # The 'flag' column indicates whether the datapoint is added or existed already

else:
    df = wastewater_data


df.dropna(subset=['channel'], inplace=True) # drop nan in channel value
unique_areas = list(df.channel.sort_values().unique())

n_unique_areas = len(unique_areas)
n_cols_for_output = 4 # user specified
n_rows_for_output = math.ceil(n_unique_areas/n_cols_for_output) # needed based on n areas in data

df = df[['week', 'channel', 'relative_copy_number', 'iso_week', 'date', 'fresh_data_flg']]

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
    area_x_series = df[df['channel'].str.lower() == area_lowercase].date
    area_y_series = df[df['channel'].str.lower() == area_lowercase].relative_copy_number

    area_x_series_last365 = df[(df['channel'].str.lower() == area_lowercase) & (df['fresh_data_flg'] == 1)].date
    area_y_series_last365 = df[(df['channel'].str.lower() == area_lowercase) & (df['fresh_data_flg'] == 1)].relative_copy_number

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
    title_text="Covid-19 Wastewater Sweden"
)
fig.update_xaxes(tickangle=45, tickfont=dict(family='Rockwell', color='black', size=14))


fig.show()
