import geopandas as gpd
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
import configparser

# Define a function to get the first day of the ISO year and week
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

#geojson[(geojson['cntr_code']=='NL')&(geojson['levl_code']==2)].nuts_name.unique()
# Load GeoJSON file into a GeoDataFrame
geojson = gpd.read_file("~/code/analytics/covid/data/NUTS_RG_20M_2021_3035.geojson")
geojson = geojson.to_crs(epsg=4326)  # Convert to EPSG:4326
geojson.columns = geojson.columns.str.lower()
geojson
geojson = geojson[['nuts_name', 'cntr_code', 'geometry']]
geojson['nuts_name'] = geojson['nuts_name'].str.lower()
region_mapping = {
    'aalten': 'gelderland',
    'aarle-rixtel': 'noord-brabant',
    'akkrum': 'friesland (nl)',
    'alblasserdam': 'zuid-holland',
    'alkmaar': 'noord-holland',
    'almelo-sumpel': 'overijssel',
    'almelo-vissedijk': 'overijssel',
    'almere': 'flevoland',
    'alphen kerk en zanen': 'zuid-holland',
    'alphen noord': 'zuid-holland',
    'ameland': 'friesland (nl)',
    'amersfoort': 'utrecht',
    'ammerstol': 'zuid-holland',
    'amstelveen': 'noord-holland',
    'amsterdam west': 'noord-holland',
    'apeldoorn': 'gelderland',
    'arnhem': 'gelderland',
    'asperen': 'gelderland',
    'assen': 'drenthe',
    'asten': 'noord-brabant',
    'baarle-nassau': 'noord-brabant',
    'barendrecht': 'zuid-holland',
    'bath': 'zeeland',
    'beemster': 'noord-holland',
    'beesd': 'gelderland',
    'beilen': 'drenthe',
    'bellingwolde': 'groningen',
    'bennekom': 'gelderland',
    'bergambacht': 'zuid-holland',
    'bergharen': 'gelderland',
    'berkenwoude': 'zuid-holland',
    'beverwijk': 'noord-holland',
    'biest-houtakker': 'noord-brabant',
    'birdaard': 'friesland (nl)',
    'blaricum': 'noord-holland',
    'bodegraven': 'zuid-holland',
    'bolsward': 'friesland (nl)',
    'bosscherveld': 'limburg (nl)',
    'boxtel': 'noord-brabant',
    'breskens': 'zeeland',
    'breukelen': 'utrecht',
    'brummen': 'gelderland',
    'bunnik': 'utrecht',
    'burgum': 'friesland (nl)',
    'camperlandpolder': 'zeeland',
    'chaam': 'noord-brabant',
    'coevorden': 'drenthe',
    'culemborg': 'gelderland',
    'dalfsen': 'overijssel',
    'damwoude': 'friesland (nl)',
    'de bilt': 'utrecht',
    'de groote lucht': 'noord-holland',
    'de groote zaag': 'noord-holland',
    'de meern': 'utrecht',
    'de verseput': 'zeeland',
    'dedemsvaart': 'overijssel',
    'delfzijl': 'groningen',
    'den bommel': 'zeeland',
    'den ham': 'overijssel',
    'den helder': 'noord-holland',
    'denekamp': 'overijssel',
    'deventer': 'overijssel',
    'dieverbrug': 'drenthe',
    'dinteloord': 'noord-brabant',
    'dinther': 'noord-brabant',
    'dinxperlo': 'gelderland',
    'dodewaard': 'gelderland',
    'dokhaven': 'zuid-holland',
    'dokkum': 'friesland (nl)',
    'dongemond': 'noord-brabant',
    'dordrecht': 'zuid-holland',
    'drachten': 'friesland (nl)',
    'dreumel': 'gelderland',
    'driebergen': 'utrecht',
    'dronten': 'flevoland',
    'druten': 'gelderland',
    'echten': 'drenthe',
    'ede': 'gelderland',
    'eelde': 'drenthe',
    'eindhoven': 'noord-brabant',
    'elburg': 'gelderland',
    'emmen': 'drenthe',
    'enschede': 'overijssel',
    'epe': 'gelderland',
    'etten': 'noord-brabant',
    'everstekoog': 'noord-holland',
    'feerwerd': 'groningen',
    'foxhol': 'groningen',
    'franeker': 'friesland (nl)',
    'gaarkeuken': 'groningen',
    'garmerwolde': 'groningen',
    'geestmerambacht': 'noord-holland',
    'geldermalsen': 'gelderland',
    'gendt': 'gelderland',
    'genemuiden': 'overijssel',
    'gennep': 'limburg (nl)',
    'gieten': 'drenthe',
    'glanerbrug': 'overijssel',
    'goedereede': 'zuid-holland',
    'goor': 'overijssel',
    'gorinchem': 'zuid-holland',
    'gorredijk': 'friesland (nl)',
    'gouda': 'zuid-holland',
    'groenedijk': 'zuid-holland',
    'groesbeek': 'gelderland',
    'groot-ammers': 'zuid-holland',
    'grouw': 'friesland (nl)',
    'haaften': 'gelderland',
    'haaksbergen': 'overijssel',
    'haaren': 'noord-brabant',
    'haarlem schalkwijk': 'noord-holland',
    'haarlem waarderpolder': 'noord-holland',
    'haarlo': 'gelderland',
    'haastrecht': 'zuid-holland',
    'halsteren': 'noord-brabant',
    'hapert': 'noord-brabant',
    'hardenberg': 'overijssel',
    'harderwijk': 'gelderland',
    'hardinxveld-giessendam': 'zuid-holland',
    'harlingen': 'friesland (nl)',
    'harnaschpolder': 'zuid-holland',
    'hattem': 'gelderland',
    'heemstede': 'noord-holland',
    'heenvliet': 'zuid-holland',
    'heerde': 'gelderland',
    'heerenveen': 'friesland (nl)',
    'heiloo': 'noord-holland',
    'heino': 'overijssel',
    'hellevoetsluis': 'zuid-holland',
    'hengelo': 'overijssel',
    'hessenpoort': 'overijssel',
    'heugem': 'limburg (nl)',
    'hilversum': 'noord-holland',
    'hoensbroek': 'limburg (nl)',
    'holten': 'overijssel',
    'hoogezand': 'groningen',
    'hoogvliet': 'zuid-holland',
    'horstermeer': 'noord-holland',
    'houten': 'utrecht',

    'houtrust': 'zuid-holland',
    'huizen': 'noord-holland',
    'hulst': 'zeeland',
    'joure': 'friesland (nl)',
    'kaatsheuvel': 'noord-brabant',
    'kampen': 'overijssel',
    'katwijk': 'zuid-holland',
    'katwoude': 'noord-holland',
    'kerkrade': 'limburg (nl)',
    'kloosterzande': 'zeeland',
    'kootstertille': 'friesland (nl)',
    'kortenoord': 'groningen',
    'kralingseveer': 'zuid-holland',
    'lage zwaluwe': 'noord-brabant',
    'land van cuijk': 'noord-brabant',
    'leek': 'groningen',
    'leerdam': 'zuid-holland',
    'leeuwarden': 'friesland (nl)',
    'leiden noord': 'zuid-holland',
    'leiden zuid-west': 'zuid-holland',
    'leidsche rijn': 'utrecht',
    'leimuiden': 'zuid-holland',
    'lelystad': 'flevoland',
    'lemmer': 'friesland (nl)',
    'lichtenvoorde': 'gelderland',
    'limmel': 'groningen',
    'lisse': 'zuid-holland',
    'loenen': 'gelderland',
    'lopik': 'utrecht',
    'losser': 'overijssel',
    'maasbommel': 'gelderland',
    'marum': 'groningen',
    'mastgat': 'zeeland',
    'meijel': 'limburg (nl)',
    'meppel': 'drenthe',
    'middelharnis': 'zuid-holland',
    'millingen aan de rijn': 'gelderland',
    'montfoort': 'utrecht',
    'nieuw-vossemeer': 'noord-brabant',
    'nieuwe waterweg': 'zuid-holland',
    'nieuwe wetering': 'zuid-holland',
    'nieuwegein': 'utrecht',
    'nieuwgraaf': 'gelderland',
    'nieuwveen': 'zuid-holland',
    'nieuwveer': 'noord-brabant',
    'nijkerk': 'gelderland',
    'nijmegen': 'gelderland',
    'nijverdal': 'overijssel',
    'noordwijk': 'zuid-holland',
    'numansdorp': 'zuid-holland',
    'oijen': 'noord-brabant',
    'olburgen': 'gelderland',
    'oldenzaal': 'overijssel',
    'olst': 'overijssel',
    'ommen': 'overijssel',
    'onderdendam': 'groningen',
    'ooltgensplaat': 'zuid-holland',
    'oostburg': 'zeeland',
    'oosterwolde': 'friesland (nl)',
    'oosthuizen': 'noord-holland',

   'oostvoorne': 'zuid-holland',
    'ootmarsum': 'overijssel',
    'ossendrecht': 'noord-brabant',
    'oud-beijerland': 'zuid-holland',
    'oude pekela': 'groningen',
    'oude tonge': 'zuid-holland',
    'oudewater': 'utrecht',
    'overasselt': 'gelderland',
    'panheel': 'limburg (nl)',
    'papendrecht': 'zuid-holland',
    'piershil': 'zuid-holland',
    'putte': 'noord-brabant',
    'raalte': 'overijssel',
    'renkum': 'gelderland',
    'retranchement': 'zeeland',
    'rhenen': 'utrecht',
    'ridderkerk': 'zuid-holland',
    'riel': 'noord-brabant',
    'rijen': 'noord-brabant',
    'rijssen': 'overijssel',
    'rimburg': 'limburg (nl)',
    'roermond': 'limburg (nl)',
    'ronde venen': 'utrecht',
    'rozenburg': 'zuid-holland',
    'ruurlo': 'gelderland',
    's hertogenbosch': 'noord-brabant',
    'scheemda': 'groningen',
    'schelluinen': 'zuid-holland',
    'scheve klap': 'groningen',
    'schiermonnikoog': 'friesland (nl)',
    'simpelveld': 'limburg (nl)',
    'sint annaparochie': 'friesland (nl)',
    'sint maartensdijk': 'zeeland',
    'sint-oedenrode': 'noord-brabant',
    'sleen': 'drenthe',
    'sleeuwijk': 'noord-brabant',
    'sliedrecht': 'zuid-holland',
    'sloten': 'friesland (nl)',
    'smilde': 'drenthe',
    'sneek': 'friesland (nl)',
    'soerendonk': 'noord-brabant',
    'soest': 'utrecht',
    'spijkenisse': 'zuid-holland',
    'stadskanaal': 'groningen',
    'steenwijk': 'overijssel',
    'stein': 'limburg (nl)',
    'stolpen': 'noord-holland',
    'stolwijk': 'zuid-holland',
    'strijen': 'zuid-holland',
    'susteren': 'limburg (nl)',
    'ter apel': 'groningen',
    'terneuzen': 'zeeland',
    'terschelling': 'friesland (nl)',
    'terwolde': 'gelderland',
    'tholen': 'zeeland',
    'tiel': 'gelderland',
    'tilburg': 'noord-brabant',
    'tollebeek': 'flevoland',
    'tubbergen': 'overijssel',
    'tweede exloermond': 'drenthe',
    'uithoorn': 'noord-holland',
    'uithuizermeeden': 'groningen',
    'ulrum': 'groningen',
    'ursem': 'noord-holland',
    'utrecht': 'utrecht',
    'varsseveld': 'gelderland',
    'veendam': 'groningen',
    'veenendaal': 'utrecht',
    'velsen': 'noord-holland',
    'venlo': 'limburg (nl)',
    'venray': 'limburg (nl)',
    'vianen': 'utrecht',
    'vinkel': 'noord-brabant',
    'vlieland': 'friesland (nl)',
    'vollenhove': 'overijssel',
    'vriescheloo': 'groningen',
    'vriezenveen': 'overijssel',
    'vroomshoop': 'overijssel',
    'waalwijk': 'noord-brabant',
    'waarde': 'zeeland',
    'waddinxveen-randenburg': 'zuid-holland',
    'walcheren': 'zeeland',
    'warns': 'friesland (nl)',
    'waspik': 'noord-brabant',
    'weert': 'limburg (nl)',
    'weesp': 'noord-holland',
    'wehe den hoorn': 'groningen',
    'wehl': 'gelderland',
    'wervershoof': 'noord-holland',
    'westerschouwen': 'zeeland',
    'westpoort': 'noord-holland',
    'wieringen': 'noord-holland',
    'wieringermeer': 'noord-holland',
    'wijk bij duurstede': 'utrecht',
    'wijlre': 'limburg (nl)',
    'willem annapolder': 'zeeland',
    'willemstad': 'noord-brabant',
    'winsum': 'groningen',
    'winterswijk': 'gelderland',
    'woerden': 'utrecht',
    'wolvega': 'friesland (nl)',
    'workum': 'friesland (nl)',
    'woudenberg': 'utrecht',
    'zaandam-oost': 'noord-holland',
    'zaltbommel': 'gelderland',
    'zeewolde': 'flevoland',
    'zeist': 'utrecht',
    'zetten': 'gelderland',
    'zuidhorn': 'groningen',
    'zutphen': 'gelderland',
    'zwaanshoek': 'noord-holland',
    'zwanenburg': 'noord-holland',
    'zwijndrecht': 'zuid-holland',
    'zwolle': 'overijssel'
}


# Pull data
country_name = 'netherlands'
filename = f'{country_name}_wastewater.parquet'
df = pd.read_parquet(f'~/code/analytics/covid/data/1_raw_data/{filename}') # wastewater
df.columns = df.columns.str.lower()
metric_nm = 'RNA_flow_per_100000'
df['rwzi_awzi_name'] = df['rwzi_awzi_name'].str.lower()
df = df[['date_measurement','rwzi_awzi_name','rna_flow_per_100000']]

df.rename(columns={"rna_flow_per_100000": "value"}, inplace=True) 

df['date_measurement'] = pd.to_datetime(df['date_measurement'], format='%Y-%m-%d')


df["week_no"] = df['date_measurement'].dt.strftime('%G-%V')

# Convert week to ISO year and week
df[['iso_year', 'iso_week']] = df['week_no'].str.split('-', expand=True)

# Convert ISO year and week to integers
df['iso_year'] = df['iso_year'].astype(int)
df['iso_week'] = df['iso_week'].astype(int)

# Apply the function to create a new column "first_day"
df['first_day'] = df.apply(get_first_day, axis=1)


df = df[df['first_day'] > date_threshold] # must be more recent that than X

region_stats = df.groupby('rwzi_awzi_name')['first_day'].agg(['count','min','max']).reset_index()
sufficient_reporting_region = region_stats[region_stats['count'] >= sufficient_updates_since_threshold].rwzi_awzi_name
df = df[df['rwzi_awzi_name'].isin(sufficient_reporting_region)]
df['region'] = df['rwzi_awzi_name'].map(region_mapping) # add region map for geojson
df = df[['first_day','region', 'value']]
df = df.groupby(['first_day','region'])['value'].agg('mean').reset_index()
df['first_day'] = df.first_day.dt.date
df = df.sort_values(by=['first_day','region'])


# Merge GeoDataFrame with data
merged_gdf = geojson.merge(df, how='inner', left_on='nuts_name', right_on='region')
merged_gdf['first_day'] = pd.to_datetime(merged_gdf['first_day'])

# Sort the DataFrame by 'first_day' in ascending order
merged_gdf = merged_gdf.sort_values(by='first_day')
merged_gdf['first_day'] = merged_gdf.first_day.dt.date


# Reshape the input to a 2D array
values_2d = merged_gdf['value'].values.reshape(-1, 1)

# Create and fit the MinMaxScaler
scaler = MinMaxScaler()
merged_gdf.loc[:, 'normalized_value'] = scaler.fit_transform(values_2d)
merged_gdf.drop_duplicates(inplace=True)

# RECREATE above
merged_gdf = merged_gdf[['first_day', 'geometry','region','cntr_code','value','normalized_value']]
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