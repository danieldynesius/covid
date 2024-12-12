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


# Load shapefile into a GeoDataFrame
gf_shp = gpd.read_file("~/code/analytics/covid/data/new-zealand-with-regions_.geojson")

gf_shp = gf_shp.to_crs(epsg=4326)  # Convert to EPSG:4326
gf_shp.columns = gf_shp.columns.str.lower()
gf_shp['cntr_code'] = 'NZ'
gf_shp.rename(columns={"name": "nuts_name"}, inplace=True)
gf_shp = gf_shp[['nuts_name', 'cntr_code', 'geometry']]
gf_shp['nuts_name'] = gf_shp['nuts_name'].astype(str)
gf_shp['nuts_name'] = gf_shp['nuts_name'].str.replace('[', '').str.replace(']', '')
gf_shp['nuts_name'] = gf_shp['nuts_name'].str.replace("'", '')
gf_shp['nuts_name'] = gf_shp['nuts_name'].str.title()
region_mapping = {
'au_armybay': 'Auckland',
'au_beachlands': 'Auckland',
'au_clarksbeach': 'Auckland',
'au_eastern': 'Auckland',
'au_helensville': 'Auckland',
'au_kawakawabay': 'Auckland',
'au_kingseat': 'Auckland',
'au_mangere': 'Auckland',
'au_omaha': 'Auckland',
'au_pukekohe': 'Auckland',
'au_rosedale': 'Auckland',
'au_snellsalgies': 'Auckland',
'au_southwestern': 'Auckland',
'au_waiuku': 'Auckland',
'au_warkworth': 'Auckland',
'au_wellsford': 'Auckland',
'au_western': 'Auckland',

'bp_katikati': 'Bay of Plenty',
'bp_kawerau': 'Bay of Plenty',
'bp_maketu': 'Bay of Plenty',
'bp_opotiki': 'Bay of Plenty',
'bp_rotorua': 'Bay of Plenty',
'bp_tauranga': 'Bay of Plenty',
'bp_temaunga': 'Bay of Plenty',
'bp_tepuke': 'Bay of Plenty',
'bp_waihibeach': 'Bay of Plenty',
'bp_whakatane': 'Bay of Plenty',

'ca_amberley': 'Canterbury',
'ca_ashburton': 'Canterbury',
'ca_christchurch': 'Canterbury',
'ca_hanmersprings': 'Canterbury',
'ca_kaiapoi': 'Canterbury',
'ca_kaikoura': 'Canterbury',
'ca_leeston': 'Canterbury',
'ca_rangiora': 'Canterbury',
'ca_rolleston': 'Canterbury',
'ca_timaru': 'Canterbury',
'ca_woodend': 'Canterbury',

'gi_gisborne': 'Gisborne',

'hb_hastings': "Hawke's Bay",
'hb_mahia': "Hawke's Bay",
'hb_napier': "Hawke's Bay",
'hb_otane': "Hawke's Bay",
'hb_porangahau': "Hawke's Bay",
'hb_takapau': "Hawke's Bay",
'hb_tepaerahi': "Hawke's Bay",
'hb_waipawa': "Hawke's Bay",
'hb_waipukurau': "Hawke's Bay",
'hb_wairoa': "Hawke's Bay",

'ma_blenheim': 'Marlborough', 
'ma_picton': 'Marlborough',

'mw_dannevirke':'Manawatu-Wanganui', 
'mw_eketahuna':'Manawatu-Wanganui', 
'mw_feilding':'Manawatu-Wanganui', 
'mw_levin':'Manawatu-Wanganui', 
'mw_pahiatua':'Manawatu-Wanganui', 
'mw_palmerstonnorth':'Manawatu-Wanganui', 
'mw_taumarunui':'Manawatu-Wanganui', 
'mw_whanganui':'Manawatu-Wanganui', 
'mw_woodville':'Manawatu-Wanganui',

'ne_bellisland':'Nelson', 
'ne_nelson':'Nelson',

'no_ahipara':'Northland', 
'no_dargaville':'Northland', 
'no_hikurangi':'Northland', 
'no_kaeo':'Northland', 
'no_kaikohe':'Northland', 
'no_kaitaia':'Northland', 
'no_kaiwaka':'Northland', 
'no_kawakawa':'Northland', 
'no_kerikeri':'Northland', 
'no_kohukohu':'Northland', 
'no_mangawhai':'Northland', 
'no_maungaturoto':'Northland', 
'no_opononi':'Northland', 
'no_paihia':'Northland', 
'no_rawene':'Northland', 
'no_ruakaka':'Northland', 
'no_russell':'Northland', 
'no_taipa':'Northland', 
'no_whangarei':'Northland', 
"no_whatuwhiwhi": "Northland",

"ot_alexandra": "Otago", 
"ot_balclutha": "Otago", 
"ot_cromwell": "Otago", 
"ot_dunedintahuna": "Otago", 
"ot_greenisland": "Otago", 
"ot_mosgiel": "Otago", 
"ot_oamaru": "Otago", 
"ot_queenstown": "Otago", 
"ot_wanaka": "Otago",

"so_bluff": "Southland", 
"so_gore": "Southland", 
"so_invercargill": "Southland",

"tk_eltham": "Taranaki",  
"tk_hawera": "Taranaki",  
"tk_kaponga": "Taranaki",  
"tk_manaia": "Taranaki",  
"tk_newplymouth": "Taranaki",  
"tk_opunake": "Taranaki",  
"tk_patea": "Taranaki",  
"tk_stratford": "Taranaki",  
"tk_waverley": "Taranaki",

"ts_motueka": "Tasman",

"wc_greymouth": "West Coast",  
"wc_hokitika": "West Coast",  
"wc_reefton": "West Coast",  
"wc_westport": "West Coast",

"wg_carterton": "Wellington",  
"wg_featherston": "Wellington",  
"wg_greytown": "Wellington",  
"wg_karori": "Wellington",  
"wg_martinborough": "Wellington",  
"wg_masterton": "Wellington",  
"wg_moapoint": "Wellington",  
"wg_otaki": "Wellington",  
"wg_paraparaumu": "Wellington",  
"wg_porirua": "Wellington",  
"wg_seaview": "Wellington",

"wk_cambridge": "Waikato",  
"wk_hamilton": "Waikato",  
"wk_matamata": "Waikato",  
"wk_morrinsville": "Waikato",  
"wk_ngatea": "Waikato",  
"wk_otorohanga": "Waikato",  
"wk_paeroa": "Waikato",  
"wk_taupo": "Waikato",  
"wk_teawamutu": "Waikato",  
"wk_tekuiti": "Waikato",  
"wk_thames": "Waikato",
"wk_tokoroa": "Waikato",
"wk_turangi": "Waikato",
"wk_whangamata": "Waikato",
"wk_whitianga": "Waikato"
}


# Pull data
country_name = 'newzealand'
filename = f'{country_name}_wastewater.parquet'
df = pd.read_parquet(f'~/code/analytics/covid/data/1_raw_data/{filename}') # wastewater
df.columns = df.columns.str.lower()
metric_nm = 'sars_gcl'
df.rename(columns={"sars_gcl": "value"
                    ,"samplelocation":"channel"
                    ,"collected":'date' 
                    }, inplace=True)

df = df[['date','channel', 'value']]
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
df = df[['first_day','region', 'value']]
df = df.groupby(['first_day','region'])['value'].agg('mean').reset_index()
df['first_day'] = df.first_day.dt.date
df = df.sort_values(by=['first_day','region'])


# Merge GeoDataFrame with data
merged_gdf = gf_shp.merge(df, how='inner', left_on='nuts_name', right_on='region')
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
