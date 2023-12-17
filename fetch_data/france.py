
# -------------------------------[ DATASET INFO ] -------------------------------
# utilizing "accessURL" from:
# https://data.europa.eu/data/datasets/651a82516edc589b4f6a0354?locale=fr
# but same data seems to also exist here:
# https://www.data.gouv.fr/fr/datasets/surveillance-du-sars-cov-2-dans-les-eaux-usees-sumeau/#/resources
#--------------------------------------------------------------------------------
import requests
import pandas as pd
import requests
import hashlib
import pyarrow.parquet as pq

# Download data (replace the URL with your actual data URL)
url = 'https://www.data.gouv.fr/fr/datasets/r/2963ccb5-344d-4978-bdd3-08aaf9efe514'
response = requests.get(url)

# Read the CSV file into a Pandas DataFrame
df_original = pd.read_csv(url, sep=';')

# Save the DataFrame as a Parquet file
parquet_filename = './data/france/france_data.parquet'
df_original.to_parquet(parquet_filename, index=False)

# Read the Parquet file into a new Pandas DataFrame
df_from_parquet = pd.read_parquet(parquet_filename)

# Check data integrity by comparing the DataFrames
if df_original.equals(df_from_parquet):
    print("Data integrity maintained.")
else:
    print("Data integrity may be compromised.")
