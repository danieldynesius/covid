# Youtube Folium info video:
# https://www.youtube.com/watch?v=4VyyFr0klH8

# Cancelled.

import folium
import webbrowser

lon = 55
lat = 8.5

map_object = folium.Map(location=[lon,lat]
                        #,tiles='CartoDB dark_matter'
                        ,tiles='cartodbpositron'
                        ,zoom_control=True
                        ,zoom_start=4.5
                        ,control_scale=True
                        )


#icon_marker = folium.Icon(color='red', icon_color='white') # This allows the customizatio of the marker
# Can also use custom icon:
#folium.CustomIcon(r"path/to/ico.jfif",icon_size=(30,30))
icon_marker = folium.Icon(icon='glass',color='green', angle=20)
folium.Marker(location=[lon,lat]
                ,draggable=False
                ,popup="Here's a <b>marker!</b>"
                ,icon=icon_marker
                ).add_to(map_object)


map_object
#map_object.save('map.html')
#webbrowser.open('map.html')    




############# TEST 3
import pandas as pd
import geopandas as gpd
from folium import Map, Choropleth
from folium.plugins import TimestampedGeoJson

# Read the Parquet files into GeoDataFrames
g1 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/france_wastewater.parquet')
g2 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/sweden_wastewater.parquet')
g3 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/netherlands_wastewater.parquet')
g4 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/denmark_wastewater.parquet')
g5 = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/austria_wastewater.parquet')
gdf = gpd.GeoDataFrame(pd.concat([g1, g2, g3, g4, g5], ignore_index=True))


# Assuming you have a GeoDataFrame named 'gdf' with columns: cntr_code, region, value, normalized_value, geometry, first_day
#gdf = gpd.read_parquet('~/code/analytics/covid/data/2_staged_data/austria_wastewater.parquet')
gdf['first_day'] = pd.to_datetime(gdf['first_day'])
lon = 55
lat = 8.5

# Convert 'first_day' to string format
gdf['first_day_str'] = gdf['first_day'].dt.strftime('%Y-%m-%d')

# Create a Folium Map
m = Map(location=[lat, lon], zoom_start=3)

# Add Choropleth layer
Choropleth(
    geo_data=gdf.loc[:, gdf.columns.difference(['first_day'])],
    data=gdf.loc[:, gdf.columns.difference(['first_day'])],
    columns=['cntr_code', 'value'],
    key_on='feature.properties.cntr_code',
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Value'
).add_to(m)

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
    period='P1D',  # Period between frames
    add_last_point=True,  # Add last point as a marker
).add_to(m)

# Show the map
m
