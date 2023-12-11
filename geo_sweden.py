import plotly.express as px
import geopandas as gpd

# Load GeoJSON file into a GeoDataFrame
sweden_gdf = gpd.read_file("/home/stratega/Documents/code/data/geo/sweden-counties.geojson")

# Filter data for Uppsala
uppsala_gdf = sweden_gdf[sweden_gdf['name'] == 'Uppsala']

# Create a choropleth map using Plotly Express
fig = px.choropleth_mapbox(
    df,
    uppsala_gdf,
    geojson=uppsala_gdf.geometry,
    locations=uppsala_gdf.index,
    color="name",
    mapbox_style="carto-positron",
    center={"lat": sweden_gdf.bounds.mean().maxy.mean(), "lon": sweden_gdf.bounds.mean().maxx.mean()},  # Center on Sweden
    zoom=5,
)

# Show the plot
fig.show()

