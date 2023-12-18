import pandas as pd
import geopandas as gpd
from branca.colormap import linear
import folium
from folium import plugins

# Read the Parquet files into GeoDataFrames
g1 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/france_wastewater.parquet')
g2 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/sweden_wastewater.parquet')

# Concatenate GeoDataFrames
gdf = gpd.GeoDataFrame(pd.concat([g1, g2], ignore_index=True))

# Create a color scale for each cntr_code
color_scales = {}
for cntr_code, cntr_code_df in gdf.groupby('cntr_code'):
    color_scales[cntr_code] = linear.OrRd_04.scale(min(cntr_code_df['value']), max(cntr_code_df['value']))

# Visualize Data
geojson_features = []
for _, row in gdf.iterrows():
    cntr_code = row['cntr_code']
    feature = {
        'type': 'Feature',
        'geometry': row['geometry'].__geo_interface__,
        'properties': {
            'style': {
                'color': 'black',
                'color': color_scales[cntr_code](row['value']),
                'fillcolor': color_scales[cntr_code](row['value']),
                'opacity': 0.7,
                'weight': 2,
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
m = folium.Map(location=[46.6031, 5], zoom_start=3.5)

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

# Display color scales for each cntr_code
#for cntr_code, color_scale in color_scales.items():
#    color_scale.caption = f'Value - {cntr_code}'
#    color_scale.add_to(m)

# Display the map
m
