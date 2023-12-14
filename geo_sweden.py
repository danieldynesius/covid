import plotly.express as px
import geopandas as gpd
import pandas as pd
from datetime import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.dates import date2num
import geopandas as gpd
import pandas as pd


# Load GeoJSON file into a GeoDataFrame
sweden_gdf = gpd.read_file("./analytics/covid/data/NUTS_RG_20M_2021_3035.geojson")
sweden_gdf = sweden_gdf[(sweden_gdf['CNTR_CODE'] == 'SE') & (sweden_gdf['LEVL_CODE'] == 3)]

# City -> Region Mapping
region_mapping = {
    'Uppsala': 'Uppsala län',
    'Knivsta': 'Uppsala län',
    'Enköping': 'Uppsala län',
    'Älvkarleby': 'Uppsala län',  # Assuming Älvkarleby is also in Uppsala
    'Östhammar': 'Uppsala län',  # Assuming Östhammar is also in Uppsala
    'Ekerö': 'Stockholms län',
    'Tierp': 'Uppsala län',
    'Österåker': 'Stockholms län',
    'Vaxholm': 'Stockholms län',
    'Örebro': 'Örebro län',
    'Umeå': 'Västerbottens län',
    'Kalmar': 'Kalmar län',
    'Ekeby': 'Skåne län',  # Note: This is a guess; provide the correct mapping if Ekeby is in a different region
    'Jönköping': 'Jönköpings län',
    'Västerås': 'Västmanlands län',
    'Helsingborg': 'Skåne län',
    'Östersund': 'Jämtlands län	',
    'Gävle': 'Gävleborgs län',
    'Göteborg': 'Västra Götalands län',
    'Malmö': 'Skåne län',
    'Stockholm-Käppala': 'Stockholms län',
    'Luleå': 'Norrbottens län',
    'Karlstad': 'Värmlands län',
    'Stockholm-Grödinge': 'Stockholms län',
    'Linköping': 'Östergötlands län',
    'Stockholm-Bromma': 'Stockholms län',
    'Stockholm-Henriksdal': 'Stockholms län'
}
# Pull data
wastewater_data = pd.read_csv(
    "https://blobserver.dc.scilifelab.se/blob/SLU_wastewater_data.csv",
    sep=",",
)
wastewater_data["year"] = wastewater_data["week"].str[:4].astype(int)

wastewater_data["week_no"] = wastewater_data["week"].str.replace(r"\*$", "", regex=True)
wastewater_data["week"] = wastewater_data["week"].str.replace(r"\*$", "", regex=True)

# Convert week to ISO year and week
wastewater_data[['iso_year', 'iso_week']] = wastewater_data['week'].str.split('-', expand=True)

# Convert ISO year and week to integers
wastewater_data['iso_year'] = wastewater_data['iso_year'].astype(int)
wastewater_data['iso_week'] = wastewater_data['iso_week'].astype(int)

# Define a function to get the first day of the ISO year and week
def get_first_day(row):
    return dt.fromisocalendar(row['iso_year'], row['iso_week'], 1)

# Apply the function to create a new column "first_day"
wastewater_data['first_day'] = wastewater_data.apply(get_first_day, axis=1)

# Accommodate a change in the column title for the COVID data
wastewater_data.rename(
    columns={
        "SARS-CoV2/PMMoV x 1000": "relative_copy_number",
    },
    inplace=True,
)
df = wastewater_data

df['geojson_region'] = df['channel'].map(region_mapping) # add region map for geojson
df = df.merge(sweden_gdf, left_on='geojson_region', right_on='NUTS_NAME', how='left' )
#df = df.iloc[:6]
df = df[['NUTS_NAME','relative_copy_number','geometry', 'first_day']]

# Drop rows with missing geometry
df = df.dropna(subset=['geometry'])
df = df.dropna(subset=['relative_copy_number'])


## CONVERT TO DD DF
#world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')

# GEO PANDAS
# Plotting the choropleth map
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
gdf.plot(column='relative_copy_number', cmap='viridis', ax=ax, legend=True)
ax.set_title('Choropleth Map of Relative Copy Number')
plt.show()


# Merge sweden_gdf with wastewater_data using 'geojson_region'
gdf = sweden_gdf.merge(wastewater_data, left_on='NUTS_NAME', right_on='geojson_region', how='left')

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(gdf, geometry='geometry', crs='EPSG:4326')

# Plotting the choropleth map
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
gdf.plot(column='relative_copy_number', cmap='viridis', ax=ax, legend=True, missing_kwds={'color': 'lightgrey'})
ax.set_title('Choropleth Map of Relative Copy Number')
plt.show()
