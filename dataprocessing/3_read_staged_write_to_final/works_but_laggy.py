
############# TEST 3
# CANCELLED
import pandas as pd
import geopandas as gpd
from folium import Map, Choropleth
from folium.plugins import TimestampedGeoJson
import os

# Read the Parquet files into GeoDataFrames
datapath = '~/code/analytics/covid/data/2_staged_data/'


gdf = gpd.read_parquet(os.path.join(datapath, 'france_wastewater.parquet'))
g2 = gpd.read_parquet(os.path.join(datapath, 'sweden_wastewater.parquet'))
g3 = gpd.read_parquet(os.path.join(datapath, 'netherlands_wastewater.parquet'))
g4 = gpd.read_parquet(os.path.join(datapath, 'denmark_wastewater.parquet'))
g5 = gpd.read_parquet(os.path.join(datapath, 'austria_wastewater.parquet'))
#gdf = gpd.GeoDataFrame(pd.concat([g1, g2, g3, g4, g5], ignore_index=True))


# Assuming you have a GeoDataFrame named 'gdf' with columns: cntr_code, region, value, normalized_value, geometry, first_day
#gdf = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/austria_wastewater.parquet')
gdf['first_day'] = pd.to_datetime(gdf['first_day'])
gdf.sort_values(by=['first_day','cntr_code'], inplace=True)
lon = 55
lat = 8.5

color_scales = {}
"""for cntr_code, cntr_code_df in gdf.groupby('cntr_code'):
    color_scales[cntr_code] = linear.OrRd_04.scale(min(cntr_code_df['value']), max(cntr_code_df['value']))
"""


# Convert 'first_day' to string format
gdf['first_day_str'] = gdf['first_day'].dt.strftime('%Y-%m-%d')

# Create a Folium Map
m = Map(location=[lat, lon], zoom_start=3)

gdf_wo_dt = gdf.loc[:, gdf.columns.difference(['first_day'])]
# Add Choropleth layer
"""Choropleth(
    geo_data=gdf_wo_dt,
    data=gdf_wo_dt,
    columns=['cntr_code', 'value'],
    key_on='feature.properties.cntr_code',
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Value'
).add_to(m)
"""
# Prepare data for TimestampedGeoJson
features = []
for _, row in gdf.iterrows():
    feature = {
        'type': 'Feature',
        'geometry': row['geometry'].__geo_interface__,
        'properties': {
            'time': row['first_day_str'],
            'popup': f"<b>Region:</b> {row['region']}<br><b>Value:</b> {row['value']}",
            'style': {
                'color': 'blue',
                'weight': 2,
                'fillOpacity': 0.5,
            }
        },
    }
    features.append(feature)

# Add TimeSliderChoropleth layer
TimestampedGeoJson(
    {'type': 'FeatureCollection', 'features': features},
    period='P1W',  # Period between frames
    add_last_point=True,  # Add last point as a marker
    duration="P1D",
    auto_play=False,
    loop=True,
    max_speed=1.5,
    loop_button=True,
    date_options='YYYY-MM-DD'    
).add_to(m)

# Show the map
m
