import pandas as pd
import geopandas as gpd
from branca.colormap import linear
import folium
from folium import plugins

pd.set_option('display.max_rows', None)  

# Read the Parquet files into GeoDataFrames
# Read the Parquet files into GeoDataFrames
g1 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/france_wastewater.parquet')
g2 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/sweden_wastewater.parquet')
g3 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/netherlands_wastewater.parquet')
g4 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/denmark_wastewater.parquet')


# Concatenate GeoDataFrames
gdf = gpd.GeoDataFrame(pd.concat([g1,g2,g3,g4], ignore_index=True))

# Write out data for other to see what goes into geoplot
gdf.to_csv('~/code/analytics/covid/data/3_finalized_data/final_wastewaterfile.csv', index=False)

# Create a Folium map centered around the specified location
m = folium.Map(location=[56, 10.5], zoom_start=7)

# Add a choropleth layer to the map
folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=['region', 'normalized_value'],  # Adjust column names as needed
    key_on='feature.properties.region',
    fill_color='Reds',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Normalized Value',
    nan_fill_color='grey',  # Color for NaN values
    nan_fill_opacity=0.4  # Opacity for NaN values
).add_to(m)

# Display the map
m



import folium
from folium import plugins
import json
import pandas as pd

# Convert GeoDataFrame to GeoJson
gdf['first_day'] = pd.to_datetime(gdf['first_day']).dt.strftime('%Y-%m-%d')  # Convert to string format
gdf_json = gdf.to_crs(epsg='4326').to_json()

# Create a Folium map centered around the specified location
m = folium.Map(location=[56, 10.5], zoom_start=7)

# Add a TimestampedGeoJson layer to the map
plugins.TimestampedGeoJson(
    json.loads(gdf_json),
    period="P1W",  # Adjust the period as needed
    duration="P1D",
    add_last_point=True,
    auto_play=True,
    loop=True,
    max_speed=1.5,
    loop_button=True,
    time_slider_drag_update=True,
    date_options='YYYY-MM-DD',
    transition_time=300,  # Adjust the transition time as needed
).add_to(m)

# Display the map
m










import folium
from folium.plugins import TimeSliderChoropleth

# Assuming gdf is a GeoDataFrame with a 'first_day' column representing dates

# Create a Folium Map object
m = folium.Map(location=[latitude, longitude], zoom_start=10)

# Create a TimeSliderChoropleth layer
time_slider = TimeSliderChoropleth(
    data=gdf.to_json(),
    styledict={},
    name='Normalized Value',
    overlay=True,
    control=True,
    show=False,
).add_to(m)

# Add the GeoJSON layer with the default date
folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=['region', 'normalized_value'],
    fill_color='Reds',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Normalized Value',
    nan_fill_color='grey',
    nan_fill_opacity=0.4,
).add_to(time_slider)

# Display the map
m


