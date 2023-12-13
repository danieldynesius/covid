import plotly.express as px
import geopandas as gpd
import pandas as pd
from datetime import datetime as dt
import matplotlib.pyplot as plt

from matplotlib.widgets import Slider
from matplotlib.dates import date2num



# Load GeoJSON file into a GeoDataFrame
#sweden_gdf = gpd.read_file("./analytics/covid/data/sweden-counties.geojson")
sweden_gdf = gpd.read_file("./analytics/covid/data/NUTS_RG_20M_2021_3035.geojson")
sweden_gdf = sweden_gdf[(sweden_gdf['CNTR_CODE'] == 'SE') & (sweden_gdf['LEVL_CODE'] == 3)]
sweden_gdf = sweden_gdf[['NUTS_NAME', 'geometry']]
# Filter data for Uppsala
#uppsala_gdf = sweden_gdf[sweden_gdf['NUTS_NAME'] == 'Uppsala']

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
df = df[['first_day','relative_copy_number', 'channel']]

df
df['geojson_region'] = df['channel'].map(region_mapping) # add region map for geojson
df = df.merge(sweden_gdf, left_on='geojson_region', right_on='NUTS_NAME', how='left' )


df['first_day_numeric'] = date2num(df['first_day'])

import plotly.express as px


# Assuming your DataFrame is named 'df' and contains the provided columns

# Convert 'relative_copy_number' to numeric if it's not already
df['relative_copy_number'] = pd.to_numeric(df['relative_copy_number'], errors='coerce')

# Convert the 'geometry' column to GeoJSON-like format
#df['geometry'] = df['geometry'].apply(lambda geom: json.loads(json.dumps(geom.__geo_interface__)) if geom else None)

fig = px.choropleth_mapbox(df, geojson='geometry', locations=df.index, color='relative_copy_number',
                           color_continuous_scale="Viridis",
                           range_color=(df['relative_copy_number'].min(), df['relative_copy_number'].max()),
                           mapbox_style="carto-positron",
                           zoom=3, center={"lat": 62.0902, "lon": 15.7129},
                           opacity=0.5,
                           labels={'relative_copy_number': 'Relative Copy Number'}
                           )

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()




import geopandas as gpd
from shapely.geometry import Polygon

# Assuming df is your DataFrame with 'geometry' as a Shapely geometry column
gdf = gpd.GeoDataFrame(df, geometry='geometry')

# Save to GeoJSON


fig = px.choropleth_mapbox(df,
                           geojson='geometry',
                           locations=df.index,
                           color="relative_copy_number",
                           center={"lat": 62.5517, "lon": 15.7073},
                           mapbox_style="carto-positron",
                           zoom=2.5)
fig.show()

## EXAMPLE
import plotly.express as px
import geopandas as gpd
import pandas as pd
import numpy as np

df = px.data.election()

dff = pd.DataFrame({'district': df['district'].tolist()*5,#np.repeat(df['district'],5),
                    'total': np.random.randint(5000,12000,len(df)*5),
                    'year': sum([[x]*len(df) for x in np.arange(2017, 2022,1)],[])
                   })

geojson = px.data.election_geojson()
gdf = gpd.GeoDataFrame.from_features(geojson,  crs='epsg:4326')

fig = px.choropleth(dff,
                    geojson=gdf.__geo_interface__,
                    color="total",
                    animation_frame='year',
                    locations="district",
                    featureidkey="properties.district",
                    projection="mercator",
                    color_continuous_scale="deep"
                   )
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(height=500,width=500)

fig.show()