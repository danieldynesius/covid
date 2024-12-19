import plotly.express as px
import geopandas as gpd
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
import configparser
import os

# Define a function to get the first day of the ISO year and week
def get_first_day(row):
    return dt.fromisocalendar(row['iso_year'], row['iso_week'], 1)



#----------------------------------------------------------------------------------------------
# Step 0: Read Config file
#----------------------------------------------------------------------------------------------
config_file = os.path.expanduser('~/code/analytics/covid/conf.ini')

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

# Set the range of values for the color scale. Originally 10 was red value (high vave one).
# New metric copies_l.the equivalent value is 660000
#color_range = [0, 10] # old
color_range = [0, 660000]


# Load GeoJSON file into a GeoDataFrame
geojson = gpd.read_file("~/code/analytics/covid/data/NUTS_RG_20M_2021_3035.geojson")
geojson = geojson.to_crs(epsg=4326)  # Convert to EPSG:4326
geojson.columns = geojson.columns.str.lower()
geojson
geojson = geojson[['nuts_name', 'cntr_code', 'geometry']]
geojson['nuts_name'] = geojson['nuts_name'].str.lower()
region_mapping = {
    'gavle': 'gävleborgs län',
    'goteborg': 'västra götalands län',    
    'uppsala': 'uppsala län',
    'knivsta': 'uppsala län',
    'enkoping': 'uppsala län',
    'alvkarleby': 'uppsala län',  # assuming älvkarleby is also in uppsala
    'ekero': 'stockholms län',
    'tierp': 'uppsala län',
    'osteråker': 'stockholms län',
    'vaxholm': 'stockholms län',
    'orebro': 'örebro län',
    'kalmar': 'kalmar län',
    'ekeby': 'skåne län',  # note: this is a guess; provide the correct mapping if ekeby is in a different region
    'jonkoping': 'jönköpings län',
    'vasteras': 'västmanlands län',
    'helsingborg': 'skåne län',
    'ostersund': 'jämtlands län',
    'malmo': 'skåne län',
    'stockholm-kappala': 'stockholms län',
    'lulea': 'norrbottens län',
    'karlstad': 'värmlands län',
    'stockholm-grödinge': 'stockholms län',
    'linkoping': 'östergötlands län',
    'stockholm-bromma': 'stockholms län',
    'stockholm-henriksdal': 'stockholms län',
    'umea': "västerbottens län",
    'osthammar': 'uppsala län'  # assuming östhammar is also in uppsala
}


# Pull data
country_name = 'sweden'
filename = f'{country_name}_wastewater.parquet'
df = pd.read_parquet(f'~/code/analytics/covid/data/1_raw_data/{filename}') # wastewater

# name standardization
df.rename(columns={"copies_l": "value"
                   ,"target": "virus"
                   ,"city": "channel"
                   }, inplace=True) # relative_copy_number
df.virus = df.virus.str.lower()
df.virus.fillna('sars-cov-2', inplace=True)
df['virus'] = df['virus'].replace('sars cov-2', 'sars-cov-2') # assume missing is sars

#df = df.loc[df['virus'] == 'sars cov-2']


df['channel'] = df['channel'].str.lower()
df['sampling_date'] = pd.to_datetime(df.sampling_date)

df["week"]   = (df['sampling_date'].dt.isocalendar().week).astype(str)
df["week_no"]= (df['sampling_date'].dt.isocalendar().week).astype(str)

df['sampling_date'] = df['sampling_date'].astype(str)

df["year"] = df["sampling_date"].str[:4].astype(int)


df['week'] = df['year'].astype(str) + '-' + df['week_no']

# Convert week to ISO year and week
df[['iso_year', 'iso_week']] = df['week'].str.split('-', expand=True)

# Convert ISO year and week to integers
df['iso_year'] = df['iso_year'].astype(int)
df['iso_week'] = df['iso_week'].astype(int)

# Apply the function to create a new column "first_day"
df['first_day'] = df.apply(get_first_day, axis=1)
metric_nm = "copies_l"
df = df[df['first_day'] > date_threshold] # must be more recent that than X

region_stats = df.groupby('channel')['first_day'].agg(['count','min','max']).reset_index()
sufficient_reporting_region = region_stats[region_stats['count'] >= sufficient_updates_since_threshold].channel
df = df[df['channel'].isin(sufficient_reporting_region)]
df['region'] = df['channel'].map(region_mapping) # add region map for geojson
df = df[['first_day', 'virus', 'region', 'value']]
df = df.groupby(['first_day', 'virus','region'])['value'].agg('mean').reset_index()
df['first_day'] = df.first_day.dt.date
df = df.sort_values(by=['first_day','region', 'virus'])


# Merge GeoDataFrame with data
merged_gdf = geojson.merge(df, how='inner', left_on='nuts_name', right_on='region')
merged_gdf['first_day'] = pd.to_datetime(merged_gdf['first_day'])

# Sort the DataFrame by 'first_day' in ascending order
merged_gdf = merged_gdf.sort_values(by='first_day')
merged_gdf['first_day'] = merged_gdf.first_day.dt.date


# Initialize the MinMaxScaler
scaler = MinMaxScaler()

# Create a new column for normalized values
merged_gdf['normalized_value'] = 0  # Initialize with zeros or NaN

# Get unique virus types
unique_viruses = merged_gdf['virus'].unique()

# Loop through each unique virus type
for virus in unique_viruses:
    # Filter the DataFrame for the current virus type
    group = merged_gdf[merged_gdf['virus'] == virus]
    
    # Fit and transform the scaler on the 'value' column of this group
    normalized_values = scaler.fit_transform(group[['value']])
    
    # Assign the normalized values back to the original DataFrame
    merged_gdf.loc[merged_gdf['virus'] == virus, 'normalized_value'] = normalized_values.flatten()

# Now merged_gdf contains a 'normalized_value' column with normalized values for each virus type
merged_gdf.drop_duplicates(inplace=True)

# RECREATE above
merged_gdf = merged_gdf[['first_day', 'geometry', 'virus','region','cntr_code','value','normalized_value']]
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
gdf_original.to_parquet(parquet_filename, index=False) #note this now contains multiple viruses, not just sars2


# Plot choropleth map using Plotly Express with Mapbox
"""
merged_gdf[merged_gdf.virus == 'sars-cov-2']

fig = px.choropleth_mapbox(
    merged_gdf,
    geojson=merged_gdf.geometry,
    locations=merged_gdf.index,
    color='value',
    opacity=0.5,
    template='ggplot2', 
    hover_name='region',
    title='Covid-19 Sweden Wastewater Data - SARS-CoV-2',
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