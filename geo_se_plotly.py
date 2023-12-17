import plotly.express as px
import geopandas as gpd
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta

# Define a function to get the first day of the ISO year and week
def get_first_day(row):
    return dt.fromisocalendar(row['iso_year'], row['iso_week'], 1)


# Data Inclusion Criteria
datafreshness = 15 # 15 means data to be included in dataset is 15 days
date_threshold = dt.now() - timedelta(days=365)
sufficient_updates_since_threshold = 22 # 22 in 365 days they should have atleast 22 data reports (assumes weekly reporting)

# Set the range of values for the color scale
color_range = [0, 10]


# Load GeoJSON file into a GeoDataFrame
geojson = gpd.read_file("~/code/analytics/covid/data/NUTS_RG_20M_2021_3035.geojson")
geojson = geojson.to_crs(epsg=4326)  # Convert to EPSG:4326

region_mapping = {
    'Uppsala': 'Uppsala län',
    'Knivsta': 'Uppsala län',
    'Enköping': 'Uppsala län',
    'Älvkarleby': 'Uppsala län',  # Assuming Älvkarleby is also in Uppsala
    'Östhammar': 'Uppsala län',  # Assuming Östhammar is also in Uppsala
    'Ekerö': 'Stockholms län',
    'Tierp': 'Uppsala län',
    'Österåker': 'Stockholms län',
    'Vaxholm': 'Stockholms län',
    'Örebro': 'Örebro län',
    'Umeå': 'Västerbottens län',
    'Kalmar': 'Kalmar län',
    'Ekeby': 'Skåne län',  # Note: This is a guess; provide the correct mapping if Ekeby is in a different region
    'Jönköping': 'Jönköpings län',
    'Västerås': 'Västmanlands län',
    'Helsingborg': 'Skåne län',
    'Östersund': 'Jämtlands län',
    'Gävle': 'Gävleborgs län',
    'Göteborg': 'Västra Götalands län',
    'Malmö': 'Skåne län',
    'Stockholm-Käppala': 'Stockholms län',
    'Luleå': 'Norrbottens län',
    'Karlstad': 'Värmlands län',
    'Stockholm-Grödinge': 'Stockholms län',
    'Linköping': 'Östergötlands län',
    'Stockholm-Bromma': 'Stockholms län',
    'Stockholm-Henriksdal': 'Stockholms län'
}


# Pull data
df = pd.read_csv("https://blobserver.dc.scilifelab.se/blob/SLU_wastewater_data.csv",sep=",")
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
merged_gdf = geojson.merge(df, how='inner', left_on='NUTS_NAME', right_on='region')
merged_gdf['first_day'] = pd.to_datetime(merged_gdf['first_day'])

# Sort the DataFrame by 'first_day' in ascending order
merged_gdf = merged_gdf.sort_values(by='first_day')
merged_gdf['first_day'] = merged_gdf.first_day.dt.date

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