import plotly.express as px
import geopandas as gpd
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
import configparser
import os

# Define a function to get the first day of the ISO year and week
def get_first_day(row):
    return dt.fromisocalendar(row['iso_year'], row['iso_week'], 1)


#----------------------------------------------------------------------------------------------
# Step 0: Read Config file
#----------------------------------------------------------------------------------------------
config_file = os.path.expanduser('~/code/analytics/covid/conf.ini')

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


# Load GeoJSON file into a GeoDataFrame
geojson = gpd.read_file("~/code/analytics/covid/data/NUTS_RG_20M_2021_3035.geojson")
geojson = geojson.to_crs(epsg=4326)  # Convert to EPSG:4326
geojson.columns = geojson.columns.str.lower()
geojson.rename(columns={"prov_name_en": "nuts_name"}, inplace=True)
geojson = geojson[['nuts_name', 'cntr_code', 'geometry']]
geojson['nuts_name'] = geojson['nuts_name'].astype(str)
geojson['nuts_name'] = geojson['nuts_name'].str.replace('[', '').str.replace(']', '')
geojson['nuts_name'] = geojson['nuts_name'].str.replace("'", '')
geojson['nuts_name'] = geojson['nuts_name'].str.lower()
region_mapping = {
    'aachen': 'nordrhein-westfalen',
    'aalen': 'baden-württemberg',
    'altötting': 'bayern',
    'andernach': 'rheinland-pfalz',
    'aschaffenburg': 'bayern',
    'augsburg stadt': 'bayern',
    'bad kreuznach': 'rheinland-pfalz',
    'bad mergentheim': 'baden-württemberg',
    'bad reichenhall': 'bayern',
    'bayreuth': 'bayern',
    'berchtesgaden': 'bayern',
    'berg': 'nordrhein-westfalen',
    'berlin': 'berlin',
    'bernburg': 'sachsen-anhalt',
    'bonn': 'nordrhein-westfalen',
    'bottrop': 'nordrhein-westfalen',
    'brandenburg a': 'brandenburg',
    'braunschweig': 'niedersachsen',
    'bremen': 'bremen',
    'büdingen': 'hessen',
    'celle': 'niedersachsen',
    'cottbus': 'brandenburg',
    'dessau': 'sachsen-anhalt',
    'dinslaken': 'nordrhein-westfalen',
    'döbeln': 'sachsen',
    'donaueschingen': 'baden-württemberg',
    'dortmund-deusen': 'nordrhein-westfalen',
    'dortmund-scharnhorst': 'nordrhein-westfalen',
    'dresden': 'sachsen',
    'duisburg alte emscher': 'nordrhein-westfalen',
    'düsseldorf (nord)': 'nordrhein-westfalen',
    'düsseldorf (süd)': 'nordrhein-westfalen',
    'ebersberg': 'bayern',
    'emschermündung': 'nordrhein-westfalen',
    'eriskirch': 'baden-württemberg',
    'erlangen': 'bayern',
    'eschweiler-weisweiler': 'nordrhein-westfalen',
    'flensburg': 'schleswig-holstein',
    'frankfurt-niederrad': 'hessen',
    'frankfurt-sindlingen': 'hessen',
    'frankfurt (oder)': 'brandenburg',
    'freilassing': 'bayern',
    'freising': 'bayern',
    'fulda': 'hessen',
    'germersheim': 'rheinland-pfalz',
    'gerwisch': 'sachsen-anhalt',
    'glonn': 'bayern',
    'göppingen': 'baden-württemberg',
    'görlitz': 'sachsen',
    'göttingen': 'niedersachsen',
    'grafing': 'bayern',
    'greifswald': 'mecklenburg-vorpommern',
    'grimma': 'sachsen',
    'halberstadt': 'sachsen-anhalt',
    'halle (saale)': 'sachsen-anhalt',
    'hamburg_01': 'hamburg',
    'hamburg_02': 'hamburg',
    'hanau': 'hessen',
    'hannover (gümmerwald)': 'niedersachsen',
    'hannover (herrenhausen)': 'niedersachsen',
    'heidelberg': 'baden-württemberg',
    'hetlingen': 'schleswig-holstein',
    'hildesheim': 'niedersachsen',
    'hof': 'bayern',
    'husum': 'schleswig-holstein',
    'ingolstadt': 'bayern',
    'jena': 'thüringen',
    'kaiserslautern': 'rheinland-pfalz',
    'kassel': 'hessen',
    'kellinghusen': 'schleswig-holstein',
    'kiel': 'schleswig-holstein',
    'koblenz': 'rheinland-pfalz',
    'köln': 'nordrhein-westfalen',
    'königsbach': 'baden-württemberg',
    'königsbrunn': 'bayern',
    'köthen': 'sachsen-anhalt',
    'landau in der pfalz': 'rheinland-pfalz',
    'leonberg': 'baden-württemberg',
    'lübeck': 'schleswig-holstein',
    'ludwigshafen (basf)': 'rheinland-pfalz',
    'mainz': 'rheinland-pfalz',
    'marburg (cappel)': 'hessen',
    'mönchengladbach': 'nordrhein-westfalen',
    'montabaur': 'rheinland-pfalz',
    'mühlacker-lomersheim': 'baden-württemberg',
    'münchen': 'bayern',
    'naumburg': 'sachsen-anhalt',
    'neu-ulm': 'bayern',
    'neubrandenburg': 'mecklenburg-vorpommern',
    'neustadt an der weinstraße': 'rheinland-pfalz',
    'nürnberg': 'bayern',
    'offenburg': 'baden-württemberg',
    'oldenburg': 'niedersachsen',
    'osnabrück': 'niedersachsen',
    'passau': 'bayern',
    'pforzheim': 'baden-württemberg',
    'piding': 'bayern',
    'pirmasens-blümelstal': 'rheinland-pfalz',
    'pirmasens-felsalbe': 'rheinland-pfalz',
    'potsdam': 'brandenburg',
    'ratzeburg': 'schleswig-holstein',
    'regensburg': 'bayern',
    'rollsdorf': 'sachsen-anhalt',
    'rostock': 'mecklenburg-vorpommern',
    'saarbrücken': 'saarland',
    'saarlouis': 'saarland',
    'schleswig': 'schleswig-holstein',
    'schönebeck': 'sachsen-anhalt',
    'schwäbisch hall': 'baden-württemberg',
    'schwabmünchen': 'bayern',
    'schweinfurt': 'bayern',
    'schwerin (süd)': 'mecklenburg-vorpommern',
    'speyer': 'rheinland-pfalz',
    'stadtbergen': 'bayern',
    'starnberg': 'bayern',
    'stendal': 'sachsen-anhalt',
    'straubing': 'bayern',
    'stuttgart': 'baden-württemberg',
    'teisendorf': 'bayern',
    'trier': 'rheinland-pfalz',
    'tübingen': 'baden-württemberg',
    'weiden': 'bayern',
    'weil am rhein': 'baden-württemberg',
    'weißenfels': 'sachsen-anhalt',
    'wellesweiler': 'saarland',
    'wernigerode-silstedt': 'sachsen-anhalt',
    'wiesbaden-biebrich': 'hessen',
    'wiesbaden-stadt': 'hessen',
    'wolfsburg': 'niedersachsen',
    'worms': 'rheinland-pfalz',
    'wuppertal-buchenhofen': 'nordrhein-westfalen',
    'wustweiler': 'saarland',
    'zeitz': 'sachsen-anhalt',
    'zusmarshausen': 'bayern'
}


# Pull data
country_name = 'germany'
filename = f'{country_name}_wastewater.parquet'
df = pd.read_parquet(f'~/code/analytics/covid/data/1_raw_data/{filename}') # wastewater
df.columns = df.columns.str.lower()
df.rename(columns={"datum": "date",
                    "viruslast": "value"
                    ,"standort":"channel"
                    ,"typ": "virus"
                    }, inplace=True)
df.virus = df.virus.str.lower()
#df = df.loc[df.virus == 'sars-cov-2']
df.virus.fillna('sars-cov-2', inplace=True) # assume missing is sars
metric_nm = 'viral_load'


df = df[['date','channel', 'value', 'virus']]
df['channel'] = df['channel'].str.lower()
df['date'] = pd.to_datetime(df['date'])

# Extract the week number using ISO week date system
df['week_no'] = df['date'].dt.strftime('%G-%V')

# Convert week to ISO year and week
df[['iso_year', 'iso_week']] = df['week_no'].str.split('-', expand=True)


# Convert ISO year and week to integers
df['iso_year'] = df['iso_year'].astype(int)
df['iso_week'] = df['iso_week'].astype(int)

# Apply the function to create a new column "first_day"
df['first_day'] = df.apply(get_first_day, axis=1)


df.dtypes
df = df[df['first_day'] > date_threshold] # must be more recent that than X

region_stats = df.groupby('channel')['first_day'].agg(['count','min','max']).reset_index()
sufficient_reporting_region = region_stats[region_stats['count'] >= sufficient_updates_since_threshold].channel
df = df[df['channel'].isin(sufficient_reporting_region)]


df['region'] = df['channel'].map(region_mapping) # add region map for geojson
df = df[['first_day','region', 'virus', 'value']]
df = df.groupby(['first_day','region', 'virus'])['value'].agg('mean').reset_index()
df['first_day'] = df.first_day.dt.date
df = df.sort_values(by=['first_day','region','virus'])


# Merge GeoDataFrame with data
merged_gdf = geojson.merge(df, how='inner', left_on='nuts_name', right_on='region')
merged_gdf['first_day'] = pd.to_datetime(merged_gdf['first_day'])

# Sort the DataFrame by 'first_day' in ascending order
merged_gdf = merged_gdf.sort_values(by='first_day')
merged_gdf['first_day'] = merged_gdf.first_day.dt.date


# Initialize the MinMaxScaler
scaler = MinMaxScaler()

# Create a new column for normalized values
merged_gdf['normalized_value'] = 0  # Initialize with zeros or NaN

# Get unique virus types
unique_viruses = merged_gdf['virus'].unique()

# Loop through each unique virus type
for virus in unique_viruses:
    # Filter the DataFrame for the current virus type
    group = merged_gdf[merged_gdf['virus'] == virus]
    
    # Fit and transform the scaler on the 'value' column of this group
    normalized_values = scaler.fit_transform(group[['value']])
    
    # Assign the normalized values back to the original DataFrame
    merged_gdf.loc[merged_gdf['virus'] == virus, 'normalized_value'] = normalized_values.flatten()

# Now merged_gdf contains a 'normalized_value' column with normalized values for each virus type
merged_gdf.drop_duplicates(inplace=True)

# RECREATE above
merged_gdf = merged_gdf[['first_day', 'geometry','region','virus','cntr_code','value','normalized_value']]
merged_gdf['first_day'] = merged_gdf['first_day'].astype(str)

# Fix dataformat -- messy fix this shit later. Its the wrong order to do things in
merged_gdf['value'] = merged_gdf['value'].astype(float).fillna(0).astype(int)
merged_gdf['cntr_nm'] = country_name
merged_gdf['metric_nm'] = metric_nm


# EXPORT DATA TO STAGED

# Read the CSV file into a Pandas DataFrame
gdf_original = merged_gdf

# Save the DataFrame as a Parquet file
parquet_filename = f'~/code/analytics/covid/data/2_staged_data/{filename}'
gdf_original.to_parquet(parquet_filename, index=False)
