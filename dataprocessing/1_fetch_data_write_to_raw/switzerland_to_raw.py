# -------------------------------[ DATASET INFO ] -------------------------------
# Swiss Data resides in multiple files from here
# https://sensors-eawag.ch/sars/overview.html
#--------------------------------------------------------------------------------
import requests
import pandas as pd
import requests
import hashlib
import pyarrow.parquet as pq


filename = 'switzerland_wastewater.parquet'

d1 = pd.read_csv('https://sensors-eawag.ch/sars/__data__/processed_normed_data_zurich_v2.csv', sep=';')
d1['channel'] = 'zurich'
d2 = pd.read_csv('https://sensors-eawag.ch/sars/__data__/processed_normed_data_lugano_v2.csv', sep=';')
d2['channel'] = 'lugano'
d3 = pd.read_csv('https://sensors-eawag.ch/sars/__data__/processed_normed_data_altenrhein_v2.csv', sep=';')
d3['channel'] = 'altenrhein'
d4 = pd.read_csv('https://sensors-eawag.ch/sars/__data__/processed_normed_data_chur_v2.csv', sep=';')
d4['channel'] = 'chur'
d5 = pd.read_csv('https://sensors-eawag.ch/sars/__data__/processed_normed_data_geneve_v2.csv', sep=';')
d5['channel'] = 'geneve'
d6 = pd.read_csv('https://sensors-eawag.ch/sars/__data__/processed_normed_data_laupen_v2.csv', sep=';')
d6['channel'] = 'laupen'

df_original = pd.DataFrame(pd.concat([d1, d2, d3, d4, d5, d6], ignore_index=True))

# Save the DataFrame as a Parquet file
parquet_filename = f'~/code/analytics/covid/data/1_raw_data/{filename}'
df_original.to_parquet(parquet_filename, index=False)

# Read the Parquet file into a new Pandas DataFrame
df_from_parquet = pd.read_parquet(parquet_filename)

# Check data integrity by comparing the DataFrames
if df_original.equals(df_from_parquet):
    print(f'Data integrity maintained: {filename}')
else:
    print(f'Data integrity may be compromised: {filename}')