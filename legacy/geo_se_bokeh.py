from datetime import datetime as dt
import pandas as pd
import geopandas as gpd
from bokeh.io import output_notebook, show
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.plotting import figure
from bokeh.palettes import Viridis256
from bokeh.models.widgets import Slider
from bokeh.layouts import column, row


# Define a function to get the first day of the ISO year and week
def get_first_day(row):
    return dt.fromisocalendar(row['iso_year'], row['iso_week'], 1)

# Load GeoJSON file into a GeoDataFrame
sweden_gdf = gpd.read_file("./data/NUTS_RG_20M_2021_3035.geojson")
sweden_gdf = sweden_gdf[(sweden_gdf['CNTR_CODE'] == 'SE') & (sweden_gdf['LEVL_CODE'] == 3)]

# City -> Region Mapping
region_mapping = {
    'Uppsala': 'Uppsala län',
    'Knivsta': 'Uppsala län',
    # ... (other mappings)
}

# Pull data
df = pd.read_csv(
    "https://blobserver.dc.scilifelab.se/blob/SLU_wastewater_data.csv",
    sep=",",
)
df["year"] = df["week"].str[:4].astype(int)

# Assuming you've renamed the column to 'region' during processing
df['region'] = df['channel'].map(region_mapping)
df = df.merge(sweden_gdf, left_on='region', right_on='NUTS_NAME', how='left')
df["year"] = df["week"].str[:4].astype(int)
df["week_no"] = df["week"].str.replace(r"\*$", "", regex=True)
df["week"] = df["week"].str.replace(r"\*$", "", regex=True)
df[['iso_year', 'iso_week']] = df['week'].str.split('-', expand=True) # Convert week to ISO year and week
df['iso_year'] = df['iso_year'].astype(int) # Convert ISO year and week to integers
df['iso_week'] = df['iso_week'].astype(int)



# Apply the function to create a new column "first_day"
df['first_day'] = df.apply(get_first_day, axis=1)

# Accommodate a change in the column title for the COVID data
df.rename(
    columns={
        "SARS-CoV2/PMMoV x 1000": "relative_copy_number",
    },
    inplace=True,
)

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')

# Set up Bokeh
output_notebook()

# Assuming 'first_day' is the Timestamp column
gdf['first_day'] = gdf['first_day'].dt.strftime('%Y-%m-%d')

# Create a GeoJSONDataSource from the GeoDataFrame
geosource = GeoJSONDataSource(geojson=gdf.to_json())

# Create a color mapper
color_mapper = LinearColorMapper(palette=Viridis256, low=gdf['relative_copy_number'].min(), high=gdf['relative_copy_number'].max())

# Create the figure and plot the choropleth map
from bokeh.layouts import column, row

# ... (previous imports)

# Create the figure and plot the choropleth map
p = figure(title='Choropleth Map of Relative Copy Number', height=600, width=600)
p.patches('xs', 'ys', source=geosource, fill_color={'field': 'relative_copy_number', 'transform': color_mapper},
          line_color='black', line_width=0.25, fill_alpha=1)

# Add color bar
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                     location=(0, 0), orientation='horizontal')
p.add_layout(color_bar, 'below')

# Add slider for year selection
year_slider = Slider(title="Year", start=df['year'].min(), end=df['year'].max(),
                     value=df['year'].min(), step=1)

# Define callback function for slider
def update(attr, old, new):
    selected_year = year_slider.value
    new_data = gdf[gdf['year'] == selected_year].to_json()
    geosource.geojson = new_data

year_slider.on_change('value', update)

# Set up layout
layout = row(column(p, year_slider), color_bar)

# Show the plot
show(layout)




from bokeh.layouts import column

# ... (previous imports)

# Create the figure and plot the choropleth map
p = figure(title='Choropleth Map of Relative Copy Number', height=600, width=600)
p.patches('xs', 'ys', source=geosource, fill_color={'field': 'relative_copy_number', 'transform': color_mapper},
          line_color='black', line_width=0.25, fill_alpha=1)

# Add color bar
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20,
                     location=(0, 0), orientation='horizontal')
p.add_layout(color_bar, 'below')

# Add slider for year selection
year_slider = Slider(title="Year", start=df['year'].min(), end=df['year'].max(),
                     value=df['year'].min(), step=1)

# Define callback function for slider
def update(attr, old, new):
    selected_year = year_slider.value
    new_data = gdf[gdf['year'] == selected_year].to_json()
    geosource.geojson = new_data
    callback = CustomJS(args=dict(source=geosource), code=callback_code)
    year_slider.js_on_change('value', callback)

year_slider.on_change('value', update)

# Set up layout
layout = column(p, year_slider)

# Show the plot
show(layout)






