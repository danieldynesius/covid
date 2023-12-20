import folium
from folium.plugins import TimeSliderChoropleth
import geopandas as gpd

# Assuming 'gdf' is your GeoDataFrame with the specified structure and data
gdf = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/denmark_wastewater.parquet')
gdf = gdf[gdf['region']=='midtjylland']
gdf = gdf.head(3)
gdf

# Convert 'first_day' to a string format for better compatibility with TimeSliderChoropleth
gdf['first_day'] = gdf['first_day'].astype(str)

# Create a Folium Map object
m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()], zoom_start=6)

# Create a TimeSliderChoropleth layer
time_slider = TimeSliderChoropleth(
    data=gdf,
    styledict={feature['id']: {str(date): {'color': 'red', 'opacity': 0.7} for date in gdf['first_day']} for feature in gdf.iterfeatures()},
    overlay=True,
    control=True,
    name='Normalized Value',
    show=False,
).add_to(m)

# Display the map
m
