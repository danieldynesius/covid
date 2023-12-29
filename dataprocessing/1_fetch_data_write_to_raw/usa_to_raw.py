# -------------------------------[ DATASET INFO ] -------------------------------
# utilizing "accessURL" from:
# https://data.europa.eu/data/datasets/651a82516edc589b4f6a0354?locale=fr
# but same data seems to also exist here:
# https://www.data.gouv.fr/fr/datasets/surveillance-du-sars-cov-2-dans-les-eaux-usees-sumeau/#/resources
#--------------------------------------------------------------------------------
import requests
import pandas as pd


filename = 'usa_wastewater.parquet'



# Replace 'YOUR_API_KEY' with the actual API key
api_key = 'YOUR_API_KEY'
api_url = 'https://data.cdc.gov/resource/g653-rqe2.csv'

headers = {
    'X-App-Token': api_key,
}

response = requests.get(api_url, headers=headers)
d1 = pd.read_csv(pd.compat.StringIO(response.text), sep=',')

d1 = pd.read_csv('https://data.cdc.gov/resource/g653-rqe2.csv', sep=',')
d2 = pd.read_csv('https://data.cdc.gov/resource/2ew6-ywp6.csv', sep=',')

d1.key_plot_id = d1.key_plot_id.str.lower()
d2.key_plot_id = d2.key_plot_id.str.lower()

d1.key_plot_id.unique()
d2.key_plot_id.unique()

d1.merge(d2, how='inner', on='key_plot_id')
d1
d2

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