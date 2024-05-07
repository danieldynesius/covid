import os
import pandas as pd
import geopandas as gpd
from branca.colormap import linear
import folium
from folium import plugins
from folium.plugins import FloatImage
from datetime import datetime
import pandas as pd
import geopandas as gpd
from branca.colormap import linear
import folium
from folium import plugins
import os
import configparser
from datetime import datetime as dt


config_file = os.path.expanduser('~/code/analytics/covid/conf.ini')

# Read the Conf file
config = configparser.ConfigParser()
config.read(config_file)

# Paths
staged_datapath = config.get('Paths', 'staged_datapath')
final_datapath = config.get('Paths', 'final_datapath')
save_geomap_dir_gh = config.get('Paths', 'save_geomap_dir_gh')
save_geomap_filepath_gh =  os.path.join(save_geomap_dir_gh, 'geo_map.html')
save_geomap_dir_bb = config.get('Paths', 'save_geomap_dir_bb')
save_geomap_filepath_bb =  os.path.join(save_geomap_dir_bb, 'geo_map.html')

try:
    latest_dataload = pd.read_csv(final_datapath+'/latest_dataload.csv') # Get the Timestamp
except:
    print('Latest Dataload csv missing. Creating it with current time.')
    current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    df_ct = pd.DataFrame([current_time], columns=['latest_dataload'])
    df_ct.to_csv(final_datapath+'/latest_dataload.csv')
    latest_dataload = df_ct

latest_dataload = latest_dataload.at[0, 'latest_dataload']

g1 = gpd.read_parquet(os.path.join(staged_datapath, 'france_wastewater.parquet'))
g2 = gpd.read_parquet(os.path.join(staged_datapath, 'sweden_wastewater.parquet'))
g3 = gpd.read_parquet(os.path.join(staged_datapath, 'netherlands_wastewater.parquet')) 
g4 = gpd.read_parquet(os.path.join(staged_datapath, 'denmark_wastewater.parquet')) #fail 1 makes html huge
g5 = gpd.read_parquet(os.path.join(staged_datapath, 'austria_wastewater.parquet'))
#g6 = gpd.read_parquet(os.path.join(staged_datapath, 'poland_wastewater.parquet')) # this is just Poznan County. Normaized Value must be
g7 = gpd.read_parquet(os.path.join(staged_datapath, 'finland_wastewater.parquet'))
g8 = gpd.read_parquet(os.path.join(staged_datapath, 'switzerland_wastewater.parquet'))
g9 = gpd.read_parquet(os.path.join(staged_datapath, 'canada_wastewater.parquet'))
g10 =gpd.read_parquet(os.path.join(staged_datapath, 'usa_wastewater.parquet'))
#g11 =gpd.read_parquet(os.path.join(staged_datapath, 'newzealand_wastewater.parquet'))
#g12 =gpd.read_parquet(os.path.join(staged_datapath, 'germany_wastewater.parquet'))

# Concatenate GeoDataFrames
gdf = gpd.GeoDataFrame(pd.concat([g1, g2, g3, g4, g5,  g7, g8, g9, g10], ignore_index=True))
gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.05) # The higher the tolerance, the smaller file size (but less geo accurately drawn regions).

# Get latest data by country
last_datapoint_by_country = gdf.groupby('cntr_code')['first_day'].max()
last_datapoint_by_country = last_datapoint_by_country.sort_values(ascending=False)

gdf = gdf.to_crs(epsg=4326)
gdf.sort_values(by=['first_day','cntr_code'], inplace=True)

# Write out data for other to see what goes into geoplot
#gdf.to_csv('~/code/analytics/covid/data/3_finalized_data/final_wastewaterfile.csv', index=False)

# RESOLVE THIS BUG HERE TO WORK ON normalized_value instead of value!
# Create a color scale for each cntr_code

# Create default scales based on min-max of each country's value in time-range
color_scales = {}
gdf['type_of_colorscale'] = 'Country Relative Min-Max'
for cntr_code, cntr_code_df in gdf.groupby('cntr_code'):
    if cntr_code == 'SE':
        color_scales[cntr_code] = linear.OrRd_04.scale(0, 10) # Purple scale: PuRd_04 :)
        gdf.loc[gdf['cntr_code'] == 'SE', 'type_of_colorscale'] = 'Country Heuristic (Basic)'
    else:
        color_scales[cntr_code] = linear.OrRd_04.scale(min(cntr_code_df['value']), max(cntr_code_df['value']))



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
                'color': color_scales[cntr_code](row['value']),
                'fillcolor': color_scales[cntr_code](row['value']),
                'opacity': 0.7,
                'weight': 2,
                'fillOpacity': 0.5,
            },
            'time': row['first_day'],
            'popup': f"<b>Region:</b> {formatted_region}<br><b>Value:</b> {row['value']}<br><b>Normalized Value</b>: {row['normalized_value']}<br><b>Colorization Rule</b>: {row['type_of_colorscale']}"
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
    auto_play=True,
    loop=True,
    speed_slider=0.5, # initial speed
    max_speed=1.5,
    loop_button=True,
    time_slider_drag_update=True,
    date_options='YYYY-MM-DD'
).add_to(m)

# Display color scales for each cntr_code
"""
for cntr_code, color_scale in color_scales.items():
    color_scale.caption = f'Value - {cntr_code}'
    color_scale.add_to(m)
"""

# Display the map
#m
#m.save('../../docs/geo_map.html')



# Create a custom HTML content for the information section
#font_size = 22
info_html_content = f"""
    <div style="margin: 10px;">
        <h3>(Beta) Covid Wastewater Dashboard<h3>
        <h3>Latest Dataload</h3>
        <font size="2"><p>{latest_dataload}</p></font>  
        <h3>Info</h3>
        <font size="3">  
        <p><b>Sweden:</b> Red can be interpreted as <i>"high covid transmission"</i>.<br><br>
        <b>All Other Countries:</b> Red can be interpreted as <i>"relatively high transmission within the country"</i>. <br><br><b>CAUTION</b>: <i>Between country comparisons</i> should not be made without good understanding of each country's specific metric.
        White areas usually means that data is missing (will add more regions once I find data).
        
        </font>
        
        </p>
        <h4>More information on GitHub, here:<br><a href="https://github.com/danieldynesius/covid" target="_blank">https://github.com/danieldynesius/covid</a></h4>
        <h3>Latest Datapoint by Country</h3>
        <p>
"""

# Append each country and its last datapoint to the HTML content
for country, last_datapoint in last_datapoint_by_country.items():
    info_html_content += f"<b>{country}:</b> {last_datapoint}<br>"

# Close the HTML content
info_html_content += """
        </p>
    </div>
"""


# Create a custom menu bar
menu_html = """
    <div style="position: absolute; top: 10px; right: 10px; background-color: white; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
        <h3>Menu</h3>
        <button onclick="zoomIn()">Zoom In</button>
        <button onclick="zoomOut()">Zoom Out</button>
        <button onclick="showInfo()">Information</button>
    </div>
"""

# Add the custom HTML content to the map as a popup
popup = folium.Popup(info_html_content, max_width=500, min_width=300)
folium.Marker(
    location=[55, -12],  # Adjust the location as needed
    icon=folium.Icon(color='darkblue'),
    popup=popup
).add_to(m)

# Add Fullscreen button
#plugins.Fullscreen().add_to(m)

# Add the custom menu bar to the map
#folium.Element(menu_html).add_to(m)

# Display the map
m
m.save(save_geomap_filepath_gh)
m.save(save_geomap_filepath_bb)


file_path = save_geomap_filepath_bb
if os.path.exists(file_path):
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)  # Convert bytes to megabytes

    print(f'The file size of {file_path} is {file_size_bytes} bytes or {file_size_mb:.2f} MB.')
else:
    print(f'The file {file_path} does not exist.')
