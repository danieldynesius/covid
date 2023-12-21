import pandas as pd
import geopandas as gpd
from branca.colormap import linear
import folium
from folium import plugins

# Read the Parquet files into GeoDataFrames
#g1 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/france_wastewater.parquet')
#g2 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/sweden_wastewater.parquet')
#g3 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/netherlands_wastewater.parquet')
gdf = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/denmark_wastewater.parquet')
#g5 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/austria_wastewater.parquet')
#gdf = gdf[gdf['region'] == 'region of southern denmark']

# Concatenate GeoDataFrames
#gdf = gpd.GeoDataFrame(pd.concat([g1, g2, g3, g4, g5], ignore_index=True))
#gdf = gdf.to_crs(epsg=4326)
#gdf = gdf.to_crs('EPSG:3857')  # Convert to Web Mercator
gdf = gdf.to_crs('EPSG:3395')
gdf.sort_values(by=['first_day','cntr_code'], inplace=True)

# Write out data for other to see what goes into geoplot
#gdf.to_csv('~/code/analytics/covid/data/3_finalized_data/final_wastewaterfile.csv', index=False)

# RESOLVE THIS BUG HERE TO WORK ON normalized_value instead of value!
# Create a color scale for each cntr_code
color_scales = {}
"""for cntr_code, cntr_code_df in gdf.groupby('cntr_code'):
    color_scales[cntr_code] = linear.OrRd_04.scale(min(cntr_code_df['value']), max(cntr_code_df['value']))
"""
# Visualize Data
geojson_features = []
for _, row in gdf.iterrows():
    cntr_code = row['cntr_code']
    formatted_region = row['region'].replace("-", " ").title()
    feature = {
        'type': 'Feature',
        'geometry': row['geometry'].__geo_interface__,
        'properties': {
            'style': {
                'color': 'green',
                'fillcolor': 'red',
                'opacity': 0.7,
                'weight': 2,
                'fillOpacity': 0.5,
            },
            'time': row['first_day'],
            'popup': f"<b>Region:</b> {formatted_region}<br><b>Value:</b> {row['value']}<br><b>Normalized Value</b>: {row['normalized_value']}"
        },
    }
    geojson_features.append(feature)

geojson_data = {
    'type': 'FeatureCollection',
    'features': geojson_features,
}

# Create a Folium map centered around France
m = folium.Map(location=[55, 8], zoom_start=3.5)

# Use TimestampedGeoJson to add a timestamp slider
plugins.TimestampedGeoJson(
    geojson_data,
    period="P1W",
    duration="P1D",
    add_last_point=True,
    auto_play=False,
    loop=True,
    max_speed=1.5,
    loop_button=True,
    time_slider_drag_update=True,
    date_options='YYYY-MM-DD'
).add_to(m)

# Display color scales for each cntr_code
for cntr_code, color_scale in color_scales.items():
    color_scale.caption = f'Value - {cntr_code}'
    color_scale.add_to(m)

# Display the map
m
