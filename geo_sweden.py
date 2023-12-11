import plotly.express as px
import geopandas as gpd
import pandas as pd
from datetime import datetime as dt

# Load GeoJSON file into a GeoDataFrame
sweden_gdf = gpd.read_file("./data/sweden-counties.geojson")

# Filter data for Uppsala
uppsala_gdf = sweden_gdf[sweden_gdf['name'] == 'Uppsala']

# City -> Region Mapping
region_mapping = {
    'Uppsala': 'Uppsala',
    'Knivsta': 'Uppsala',
    'Enköping': 'Uppsala',
    'Älvkarleby': 'Uppsala',  # Assuming Älvkarleby is also in Uppsala
    'Östhammar': 'Uppsala',  # Assuming Östhammar is also in Uppsala
    'Ekerö': 'Stockholm',
    'Tierp': 'Uppsala',
    'Österåker': 'Stockholm',
    'Vaxholm': 'Stockholm',
    'Örebro': 'Örebro',
    'Umeå': 'Västerbotten',
    'Kalmar': 'Kalmar',
    'Ekeby': 'Skåne',  # Note: This is a guess; provide the correct mapping if Ekeby is in a different region
    'Jönköping': 'Jönköping',
    'Västerås': 'Västmanland',
    'Helsingborg': 'Skåne',
    'Östersund': 'Jämtland',
    'Gävle': 'Gävleborg',
    'Göteborg': 'Västra Götaland',
    'Malmö': 'Skåne',
    'Stockholm-Käppala': 'Stockholm',
    'Luleå': 'Norrbotten',
    'Karlstad': 'Värmland',
    'Stockholm-Grödinge': 'Stockholm',
    'Linköping': 'Östergötland',
    'Stockholm-Bromma': 'Stockholm',
    'Stockholm-Henriksdal': 'Stockholm'
}


# Pull data
wastewater_data = pd.read_csv(
    "https://blobserver.dc.scilifelab.se/blob/SLU_wastewater_data.csv",
    sep=",",
)
wastewater_data["year"] = wastewater_data["week"].str[:4].astype(int)

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
wastewater_data['first_day'] = wastewater_data.apply(get_first_day, axis=1)


# Accommodate a change in the column title for the COVID data
wastewater_data.rename(
    columns={
        "SARS-CoV2/PMMoV x 1000": "relative_copy_number",
    },
    inplace=True,
)

df = wastewater_data

df['geojson_region'] = df['channel'].map(region_mapping) # add region map for geojson

# Create a choropleth map using Plotly Express
fig = px.choropleth_mapbox(
    df,
    geojson=uppsala_gdf.geometry,
    locations=uppsala_gdf.index,
    color="relative_copy_number",  # Change 'name' to 'relative_copy_number' if you want to color by that column
    mapbox_style="carto-positron",
    center={"lat": uppsala_gdf.bounds.mean().maxy.mean(), "lon": uppsala_gdf.bounds.mean().maxx.mean()},  # Corrected center
    zoom=5,
)

# Show the plot
fig.show()



# Create choropleth maps for each region
for region_name, region_gdf in sweden_gdf.groupby('name'):
    print('region_name:', region_name)
    region_wastewater_data = df[df['geojson_region'] == region_name]

    # Create a choropleth map using Plotly Express for the current region
    fig = px.choropleth_mapbox(
        region_wastewater_data,
        geojson=region_gdf.geometry,
        locations=region_wastewater_data.index,  # Use the DataFrame index as locations
        color="relative_copy_number",
        mapbox_style="carto-positron",
        center={"lat": region_gdf.bounds.mean().maxy.mean(), "lon": region_gdf.bounds.mean().maxx.mean()},
        zoom=5,
        title=f'Choropleth Map for {region_name}'
    )

    # Show the plot for the current region
    fig.show()

