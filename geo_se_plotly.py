import plotly.express as px
import geopandas as gpd
import pandas as pd

# Load GeoJSON file into a GeoDataFrame
sweden_gdf = gpd.read_file("./data/NUTS_RG_20M_2021_3035.geojson")
sweden_gdf = sweden_gdf.to_crs(epsg=4326)  # Convert to EPSG:4326

# Sample data with only Stockholm and Uppsala regions having values
data = {
    'NUTS_NAME': ['Stockholms län', 'Uppsala län'],
    'Value': [10, 20]  # Replace with your actual data
}

df = pd.DataFrame(data)

# Merge GeoDataFrame with data
merged_gdf = sweden_gdf.merge(df, how='left', on='NUTS_NAME')

# Plot choropleth map using Plotly Express with Mapbox
fig = px.choropleth_mapbox(
    merged_gdf,
    geojson=merged_gdf.geometry,
    locations=merged_gdf.index,
    color='Value',
    opacity=0.5,
    hover_name='NUTS_NAME',
    title='Choropleth Map of Sample Data',
    color_continuous_scale="Viridis",  # Choose a color scale
    mapbox_style="carto-positron",  # You can choose other Mapbox styles
    center={"lat": 62, "lon": 18.1},  # Center on Sweden's approximate coordinates
    zoom=4,  # Adjust the zoom level as needed
)

# Show the plot
fig.show()
