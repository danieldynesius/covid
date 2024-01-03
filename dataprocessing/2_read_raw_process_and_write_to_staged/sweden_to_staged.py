import plotly.express as px
import geopandas as gpd
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
import configparser

# Define a function to get the first day of the ISO year and week
def get_first_day(row):
    return dt.fromisocalendar(row['iso_year'], row['iso_week'], 1)



#----------------------------------------------------------------------------------------------
# Step 0: Read Config file
#----------------------------------------------------------------------------------------------
config_file = '/home/stratega/code/analytics/covid/conf.ini'

# Read the Conf file
config = configparser.ConfigParser()
config.read(config_file)

# Data Params
data_stale_hours = config.getint('Data', 'data_stale_hours')
datafreshness = config.getint('Data', 'datafreshness')
n_days_back_to_include = config.getint('Data', 'n_days_back_to_include')
sufficient_updates_since_threshold = config.getint('Data', 'sufficient_updates_since_threshold')

# Data Inclusion Criteria
datafreshness = datafreshness # 15 means data to be included in dataset is 15 days
date_threshold = (dt.now() - timedelta(days=n_days_back_to_include)).date()
date_threshold = pd.Timestamp(date_threshold)
sufficient_updates_since_threshold = sufficient_updates_since_threshold # 22 in 365 days they should have atleast 22 data reports (assumes weekly reporting)

# Set the range of values for the color scale
color_range = [0, 10]


# Load GeoJSON file into a GeoDataFrame
geojson = gpd.read_file("~/code/analytics/covid/data/NUTS_RG_20M_2021_3035.geojson")
geojson = geojson.to_crs(epsg=4326)  # Convert to EPSG:4326
geojson.columns = geojson.columns.str.lower()
geojson
geojson = geojson[['nuts_name', 'cntr_code', 'geometry']]
geojson['nuts_name'] = geojson['nuts_name'].str.lower()
region_mapping = {
    'uppsala': 'uppsala län',
    'knivsta': 'uppsala län',
    'enköping': 'uppsala län',
    'älvkarleby': 'uppsala län',  # assuming älvkarleby is also in uppsala
    'östhammar': 'uppsala län',  # assuming östhammar is also in uppsala
    'ekerö': 'stockholms län',
    'tierp': 'uppsala län',
    'österåker': 'stockholms län',
    'vaxholm': 'stockholms län',
    'örebro': 'örebro län',
    'umeå': 'västerbottens län',
    'kalmar': 'kalmar län',
    'ekeby': 'skåne län',  # note: this is a guess; provide the correct mapping if ekeby is in a different region
    'jönköping': 'jönköpings län',
    'västerås': 'västmanlands län',
    'helsingborg': 'skåne län',
    'östersund': 'jämtlands län',
    'gävle': 'gävleborgs län',
    'göteborg': 'västra götalands län',
    'malmö': 'skåne län',
    'stockholm-käppala': 'stockholms län',
    'luleå': 'norrbottens län',
    'karlstad': 'värmlands län',
    'stockholm-grödinge': 'stockholms län',
    'linköping': 'östergötlands län',
    'stockholm-bromma': 'stockholms län',
    'stockholm-henriksdal': 'stockholms län'
}


# Pull data
country_name = 'sweden'
filename = f'{country_name}_wastewater.parquet'
df = pd.read_parquet(f'~/code/analytics/covid/data/1_raw_data/{filename}') # wastewater
df['channel'] = df['channel'].str.lower()
df["year"] = df["week"].str[:4].astype(int)
df["week_no"] = df["week"].str.replace(r"\*$", "", regex=True)
df["week"] = df["week"].str.replace(r"\*$", "", regex=True)

# Convert week to ISO year and week
df[['iso_year', 'iso_week']] = df['week'].str.split('-', expand=True)

# Convert ISO year and week to integers
df['iso_year'] = df['iso_year'].astype(int)
df['iso_week'] = df['iso_week'].astype(int)

# Apply the function to create a new column "first_day"
df['first_day'] = df.apply(get_first_day, axis=1)
metric_nm = "SARS-CoV2/PMMoV x 1000"
df.rename(columns={"SARS-CoV2/PMMoV x 1000": "value", }, inplace=True) # relative_copy_number
df = df[df['first_day'] > date_threshold] # must be more recent that than X

region_stats = df.groupby('channel')['first_day'].agg(['count','min','max']).reset_index()
sufficient_reporting_region = region_stats[region_stats['count'] >= sufficient_updates_since_threshold].channel
df = df[df['channel'].isin(sufficient_reporting_region)]
df['region'] = df['channel'].map(region_mapping) # add region map for geojson
df = df[['first_day','region', 'value']]
df = df.groupby(['first_day','region'])['value'].agg('mean').reset_index()
df['first_day'] = df.first_day.dt.date
df = df.sort_values(by=['first_day','region'])


# Merge GeoDataFrame with data
merged_gdf = geojson.merge(df, how='inner', left_on='nuts_name', right_on='region')
merged_gdf['first_day'] = pd.to_datetime(merged_gdf['first_day'])

# Sort the DataFrame by 'first_day' in ascending order
merged_gdf = merged_gdf.sort_values(by='first_day')
merged_gdf['first_day'] = merged_gdf.first_day.dt.date


# Reshape the input to a 2D array
values_2d = merged_gdf['value'].values.reshape(-1, 1)

# Create and fit the MinMaxScaler
scaler = MinMaxScaler()
merged_gdf.loc[:, 'normalized_value'] = scaler.fit_transform(values_2d)

merged_gdf.drop_duplicates(inplace=True)

# RECREATE above
merged_gdf = merged_gdf[['first_day', 'geometry','region','cntr_code','value','normalized_value']]
merged_gdf['first_day'] = merged_gdf['first_day'].astype(str)

# Fix dataformat -- messy fix this shit later. Its the wrong order to do things in
merged_gdf['value'] = merged_gdf['value'].astype(float).fillna(0).astype(int)
merged_gdf['cntr_nm'] = country_name
merged_gdf['metric_nm'] = metric_nm


# EXPORT DATA TO STAGED

# Read the CSV file into a Pandas DataFrame
gdf_original = merged_gdf

# Save the DataFrame as a Parquet file
parquet_filename = f'~/code/analytics/covid/data/2_staged_data/{filename}'
gdf_original.to_parquet(parquet_filename, index=False)

"""
# Plot choropleth map using Plotly Express with Mapbox
fig = px.choropleth_mapbox(
    merged_gdf,
    geojson=merged_gdf.geometry,
    locations=merged_gdf.index,
    color='value',
    opacity=0.5,
    template='ggplot2', 
    hover_name='region',
    title='Covid-19 Sweden Wastewater Data',
    labels={'value': 'Relative Copy Number', 'first_day': 'Date (Weekly)'},
    color_continuous_scale="OrRd",
    range_color=color_range,
    mapbox_style="carto-positron",
    center={"lat": 62, "lon": 18.1},
    zoom=2.9,
    animation_frame='first_day'
)

# Set the size of the graph
fig.update_layout(
    height=600,
    width=800,
)

# Show the plot
fig.show()
"""