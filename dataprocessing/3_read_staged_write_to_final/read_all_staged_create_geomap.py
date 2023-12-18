import pandas as pd
import pyarrow
import geopandas as gpd
from branca.colormap import linear
import folium
from folium import plugins
import os




# Read the Parquet file into a new Pandas DataFrame

g1 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/france_wastewater.parquet')
g2 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/sweden_wastewater.parquet')
list_gdf = [g1,g2]

gdf = gpd.GeoDataFrame( pd.concat( [g1, g2], ignore_index=True) )


#### Visualize Data
# Create a color scale - Dynamic
color_scale = linear.OrRd_04.scale(min(gdf['value']), max(gdf['value']))

# Create a color scale - Static
#color_scale = linear.OrRd_04.scale(0, 25)
#color_scale = 'YlOrRd'

# Create a GeoJSON object and features
geojson_features = []

for _, row in gdf.iterrows():
    feature = {
        'type': 'Feature',
        'geometry': row['geometry'].__geo_interface__,
        'properties': {
            'style': {
                'color': 'black',  # Set the color to black for borders
                'color': color_scale(row['value']),
                'fillcolor': color_scale(row['value']),
                'opacity': 0.7,
                'weight': 2,  # Adjust the weight for thicker borders
                'fillOpacity': 0.5,
            },
            'time': row['first_day'],
        }
    }
    geojson_features.append(feature)

geojson_data = {
    'type': 'FeatureCollection',
    'features': geojson_features,
}

# Create a Folium map centered around France
m = folium.Map(location=[46.6031, 1.8883], zoom_start=5)

# Use TimestampedGeoJson to add a timestamp slider
plugins.TimestampedGeoJson(
    geojson_data,
    period="P1W",
    duration="P1D",
    add_last_point=True,
    auto_play=True,
    loop=True,
    max_speed=1.5,
    loop_button=True,
    time_slider_drag_update=True,
    date_options='YYYY-MM-DD'
).add_to(m)

# Display the color scale in the map
color_scale.caption = 'Value'
color_scale.add_to(m)

# Display the map
m