import plotly.express as px
import geopandas as gpd
import pandas as pd
from datetime import datetime as dt


# Define a function to get the first day of the ISO year and week
def get_first_day(row):
    return dt.fromisocalendar(row['iso_year'], row['iso_week'], 1)


# Load GeoJSON file into a GeoDataFrame
geojson = gpd.read_file("/home/stratega/Documents/code/analytics/covid/data/NUTS_RG_20M_2021_3035.geojson")
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
    'Östersund': 'Jämtlands län	',
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

# relative_copy_number
df.rename(columns={"SARS-CoV2/PMMoV x 1000": "value", }, inplace=True)

df['region'] = df['channel'].map(region_mapping) # add region map for geojson

# Merge GeoDataFrame with data
merged_gdf = geojson.merge(df, how='left', left_on='NUTS_NAME', right_on='region')

# Plot choropleth map using Plotly Express with Mapbox
fig = px.choropleth_mapbox(
    merged_gdf,
    geojson=merged_gdf.geometry,
    locations=merged_gdf.index,
    color='value',
    opacity=0.5,
    hover_name='NUTS_NAME',
    title='Covid-19 Sweden Wastewater Data',
    labels={'value':'Relative Copy Number'},
    color_continuous_scale="OrRd",  # Choose a color scale
    mapbox_style="carto-positron",  # You can choose other Mapbox styles
    center={"lat": 62, "lon": 18.1},  # Center on Sweden's apprx coordinates
    zoom=3,  # Adjust the zoom level as needed
)

# Show the plot
fig.show()
