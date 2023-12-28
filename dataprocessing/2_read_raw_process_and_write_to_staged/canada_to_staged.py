import plotly.express as px
import geopandas as gpd
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler

# Define a function to get the first day of the ISO year and week
def get_first_day(row):
    return dt.fromisocalendar(row['iso_year'], row['iso_week'], 1)


# Data Inclusion Criteria
datafreshness = 15 # 15 means data to be included in dataset is 15 days
date_threshold = dt.now() - timedelta(days=365)
sufficient_updates_since_threshold = 22 # 22 in 365 days they should have atleast 22 data reports (assumes weekly reporting)


# Load GeoJSON file into a GeoDataFrame
geojson = gpd.read_file("~/code/analytics/covid/data/georef-canada-province@public.geojson")
geojson = geojson.to_crs(epsg=4326)  # Convert to EPSG:4326
geojson.columns = geojson.columns.str.lower()
geojson['cntr_code'] = 'CA'
geojson.rename(columns={"prov_name_en": "nuts_name"}, inplace=True)
geojson = geojson[['nuts_name', 'cntr_code', 'geometry']]
geojson['nuts_name'] = geojson['nuts_name'].astype(str)
geojson['nuts_name'] = geojson['nuts_name'].str.replace('[', '').str.replace(']', '')
geojson['nuts_name'] = geojson['nuts_name'].str.replace("'", '')
geojson['nuts_name'] = geojson['nuts_name'].str.lower()
region_mapping = {
    'trenton': 'ontario',
    'vancouver': 'british columbia',
    'winnipeg': 'manitoba',
    'regina': 'saskatchewan',
    'souris': 'prince edward island',
    "st. john's": 'newfoundland and labrador',
    'summerside': 'prince edward island',
    'toronto': 'ontario',
    'halifax': 'nova scotia',
    'miramichi (nml historical data)': 'new brunswick',
    'moncton (nml historical data)': 'new brunswick',
    'montague': 'prince edward island',
    'montreal': 'quebec',
    'yarmouth': 'nova scotia',
    'assiniboia': 'saskatchewan',
    'battleford': 'saskatchewan',
    'birch hills': 'saskatchewan',
    'canora': 'saskatchewan',
    'estevan': 'saskatchewan',
    'île-à-la-crosse': 'saskatchewan',
    'la ronge': 'saskatchewan',
    'lumsden': 'saskatchewan',
    'maple creek': 'saskatchewan',
    'meadow lake': 'saskatchewan',
    'melville': 'saskatchewan',
    'moose jaw': 'saskatchewan',
    'north battleford': 'saskatchewan',
    'pasqua': 'saskatchewan',
    'prince albert': 'saskatchewan',
    'saskatoon': 'saskatchewan',
    'southey': 'saskatchewan',
    'swift current': 'saskatchewan',
    'unity': 'saskatchewan',
    'watrous': 'saskatchewan',
    'weyburn': 'saskatchewan',
    'yorkton': 'saskatchewan',
    'bathurst': 'new brunswick',
    'campbellton': 'new brunswick',
    'edmundston': 'new brunswick',
    'fredericton': 'new brunswick',
    'miramichi': 'new brunswick',
    'moncton': 'new brunswick',
    'saint john': 'new brunswick',
    'edmonton': 'alberta',
    'fredericton (nml historical data)': 'new brunswick',
    'haines junction': 'yukon',
    'bathurst (nml historical data)': 'new brunswick',
    'battery point': 'new brunswick',
    'brandon': 'manitoba',
    'bridgewater': 'nova scotia',
    'campbellton (nml historical data)': 'new brunswick',
    'central colchester': 'nova scotia',
    'city of charlottetown & town of stratford': 'prince edward island',
    'dominion-bridgeport': 'nova scotia',
    'alberton': 'prince edward island'
}


# Pull data
country_name = 'canada'
filename = f'{country_name}_wastewater.parquet'
df = pd.read_parquet(f'~/code/analytics/covid/data/1_raw_data/{filename}') # wastewater
df.columns = df.columns.str.lower()
metric_nm = 'viral_load'
df.rename(columns={"viral_load": "value"
                    ,"region":"channel" 
                    }, inplace=True)

df = df[['date','channel', 'value']]
df['channel'] = df['channel'].str.lower()
df['date'] = pd.to_datetime(df['date'])

# Extract the week number using ISO week date system
df['week_no'] = df['date'].dt.strftime('%G-%V')

# Convert week to ISO year and week
df[['iso_year', 'iso_week']] = df['week_no'].str.split('-', expand=True)


# Convert ISO year and week to integers
df['iso_year'] = df['iso_year'].astype(int)
df['iso_week'] = df['iso_week'].astype(int)

# Apply the function to create a new column "first_day"
df['first_day'] = df.apply(get_first_day, axis=1)

df
df = df[df['first_day'] > date_threshold] # must be more recent that than X

region_stats = df.groupby('channel')['first_day'].agg(['count','min','max']).reset_index()
sufficient_reporting_region = region_stats[region_stats['count'] >= sufficient_updates_since_threshold].channel
df = df[df['channel'].isin(sufficient_reporting_region)]

geojson
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
