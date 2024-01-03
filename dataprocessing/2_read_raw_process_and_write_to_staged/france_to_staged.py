# -------------------------------[ DATASET INFO ] -------------------------------
# utilizing "accessURL" from:
# https://data.europa.eu/data/datasets/651a82516edc589b4f6a0354?locale=fr
# but same data seems to also exist here:
# https://www.data.gouv.fr/fr/datasets/surveillance-du-sars-cov-2-dans-les-eaux-usees-sumeau/#/resources
#--------------------------------------------------------------------------------

import pandas as pd
import pyarrow.parquet as pq
from datetime import datetime as dt
from datetime import timedelta
import geopandas as gpd
from sklearn.preprocessing import MinMaxScaler
import configparser

# Get the first day of the ISO year and week
def get_first_day(row):
    return dt.fromisocalendar(row['iso_year'], row['iso_week'], 1)

#----------------------------------------------------------------------------------------------
# Step 0: Read Config file
#----------------------------------------------------------------------------------------------
config_file = '/home/stratega/code/analytics/covid/conf.ini'

# Read the Conf file
config = configparser.ConfigParser()
config.read(config_file)

# Data Params
data_stale_hours = config.getint('Data', 'data_stale_hours')
datafreshness = config.getint('Data', 'datafreshness')
n_days_back_to_include = config.getint('Data', 'n_days_back_to_include')
sufficient_updates_since_threshold = config.getint('Data', 'sufficient_updates_since_threshold')

# Data Inclusion Criteria
datafreshness = datafreshness # 15 means data to be included in dataset is 15 days
date_threshold = (dt.now() - timedelta(days=n_days_back_to_include)).date()
date_threshold = pd.Timestamp(date_threshold)
sufficient_updates_since_threshold = sufficient_updates_since_threshold # 22 in 365 days they should have atleast 22 data reports (assumes weekly reporting)


# READ DATA
metric_nm = 'viral concentration of SARS-CoV-2 (expressed in cg/L & quantification carried out from the E gene) & the nitrogen concentration ammoniacal (expressed in mg of N/L)'
country_name = 'france'
filename = f'{country_name}_wastewater.parquet'
df = pd.read_parquet(f'~/code/analytics/covid/data/1_raw_data/{filename}') # wastewater
df_metadata = pd.read_parquet(f'~/code/analytics/covid/data/1_raw_data/{country_name}_wastewater_metadata.parquet') # meta
df_metadata = df_metadata[['nom', 'commune', 'population']]
geojson = gpd.read_file("~/code/analytics/covid/data/NUTS_RG_20M_2021_3035.geojson") # geo
geojson = geojson.to_crs(epsg=4326)  # Convert to EPSG:4326
geojson.columns = geojson.columns.str.lower()
geojson = geojson[['cntr_code','nuts_name','geometry']]

# Mapping
# Dictionary mapping cities to regions
region_mapping = {
    'dijon': 'bourgogne',
    'grenoble': 'auvergne-rhône-alpes',
    'lille': 'hauts-de-france',
    'marseille': "provence-alpes-côte d'azur",
    'nancy': 'grand est',
    'nantes': 'pays de la loire',
    'orleans': 'centre — val de loire',
    'paris': 'ile-de-france',
    'pau': 'nouvelle-aquitaine',
    'rennes': 'bretagne',
    'rouen': 'normandie',
    'toulouse': 'occitanie'
}


# NORMALIZE DATA
# Rename
df.rename(columns={'semaine':'week'}, inplace=True)
#df_metadata.rename(columns={'commune':'region'}, inplace=True)

# Transform df format
df = df.melt(id_vars=['week'], 
        var_name="location", 
        value_name="value")

# Transform week e.g. '2022-S30' to year and week nr
df['week'] = df['week'].apply(lambda x: re.sub(r'S', '', x))
df[['iso_year', 'iso_week']] = df['week'].str.split('-', expand=True)

# Convert ISO year and week to integers
df['iso_year'] = df['iso_year'].astype(int)
df['iso_week'] = df['iso_week'].astype(int)

df['first_day'] = df.apply(get_first_day, axis=1) # Call function

# Transform to lower case for column merge
df['location'] = df['location'].str.lower()
df[df['location'] == 'national']
df_metadata['nom'] = df_metadata['nom'].str.lower()
df_metadata['commune'] = df_metadata['commune'].str.lower()
geojson['nuts_name'] = geojson['nuts_name'].str.lower()

df = df.merge(df_metadata, how='inner', left_on='location', right_on='nom')
df = df[['week','first_day', 'commune', 'population', 'value']]

# Filter based on data freshness
df = df[df['first_day'] > date_threshold] # must be more recent that than X
region_stats = df.groupby('commune')['first_day'].agg(['count','min','max']).reset_index()
sufficient_reporting_region = region_stats[region_stats['count'] >= sufficient_updates_since_threshold].commune
df = df[df['commune'].isin(sufficient_reporting_region)]
df['region'] = df['commune'].map(region_mapping) # add region map for geojson
df = df.sort_values(by=['first_day','region'])

# Merge GeoDataFrame with data
merged_gdf = geojson.merge(df, how='inner', left_on='nuts_name', right_on='region')
merged_gdf['first_day'] = pd.to_datetime(merged_gdf['first_day'])

# Sort the DataFrame by 'first_day' in ascending order
merged_gdf = merged_gdf.sort_values(by='first_day')
merged_gdf['first_day'] = merged_gdf.first_day.dt.date

merged_gdf['value'] = merged_gdf['value'].str.replace(',', '.').astype(float).fillna(0).astype(int)
df['value'] = df['value'].str.replace(',', '.').astype(float).fillna(0).astype(int)

# Reshape the input to a 2D array
values_2d = merged_gdf['value'].values.reshape(-1, 1)

# Create and fit the MinMaxScaler
scaler = MinMaxScaler()
merged_gdf.loc[:, 'normalized_value'] = scaler.fit_transform(values_2d)

merged_gdf.drop_duplicates(inplace=True)

# RECREATE above
merged_gdf = merged_gdf[['first_day', 'geometry','region','cntr_code','value','normalized_value']]
merged_gdf['first_day'] = merged_gdf['first_day'].astype(str)
merged_gdf['cntr_nm'] = country_name
merged_gdf['metric_nm'] = metric_nm

# EXPORT DATA TO STAGED

# Read the CSV file into a Pandas DataFrame
gdf_original = merged_gdf

# Save the DataFrame as a Parquet file
parquet_filename = f'~/code/analytics/covid/data/2_staged_data/{filename}'
gdf_original.to_parquet(parquet_filename, index=False)