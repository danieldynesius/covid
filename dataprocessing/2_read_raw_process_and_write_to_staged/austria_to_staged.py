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
date_threshold = (dt.now() - timedelta(days=365)).date()

sufficient_updates_since_threshold = 22 # 22 in 365 days they should have atleast 22 data reports (assumes weekly reporting)

# Set the range of values for the color scale
color_range = [0, 10]


# Load GeoJSON file into a GeoDataFrame
geojson = gpd.read_file("~/code/analytics/covid/data/NUTS_RG_20M_2021_3035.geojson")
geojson = geojson.to_crs(epsg=4326)  # Convert to EPSG:4326
geojson.columns = geojson.columns.str.lower()
geojson
geojson = geojson[['nuts_name', 'cntr_code', 'geometry']]
geojson['nuts_name'] = geojson['nuts_name'].str.lower()



# Pull data
filename = 'austria_wastewater.parquet'
df = pd.read_parquet(f'~/code/analytics/covid/data/1_raw_data/{filename}') # wastewater
df.columns = df.columns.str.lower()
df['gruppe'] = df['gruppe'].str.lower()

df.rename(columns={"genkopien pro ew / tag * 10^6": "value", 'datum':'first_day', 'gruppe':'region'}, inplace=True) # relative_copy_number
df['first_day'] = pd.to_datetime(df['first_day']).dt.date
df = df[df['first_day'] > date_threshold] # must be more recent that than X

region_stats = df.groupby('region')['first_day'].agg(['count','min','max']).reset_index()
sufficient_reporting_region = region_stats[region_stats['count'] >= sufficient_updates_since_threshold].region
df = df[df['region'].isin(sufficient_reporting_region)]

#df['region'] = df['gruppe'].map(region_mapping) # add region map for geojson
df = df[['first_day','region', 'value']]
df = df.groupby(['first_day','region'])['value'].agg('mean').reset_index()

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
df['value'] = df['value'].astype(float).fillna(0).astype(int)


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