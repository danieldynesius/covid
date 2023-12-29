# -------------------------------[ DATASET INFO ] -------------------------------
# utilizing "accessURL" from:
# https://data.europa.eu/data/datasets/651a82516edc589b4f6a0354?locale=fr
# but same data seems to also exist here:
# https://www.data.gouv.fr/fr/datasets/surveillance-du-sars-cov-2-dans-les-eaux-usees-sumeau/#/resources
#--------------------------------------------------------------------------------
import requests
import pandas as pd
import json.decoder
from urllib.error import HTTPError

query = (
    "https://data.cdc.gov/resource/2ew6-ywp6.json?"
    "$order=first_sample_date%20DESC"  # replace blankspace with %20
    "&$limit=5"
)
query1 = (
    "https://data.cdc.gov/resource/2ew6-ywp6.json?"
    "$select=wwtp_jurisdiction,reporting_jurisdiction,key_plot_id,county_names,first_sample_date"
    "&$order=first_sample_date%20DESC"  # replace blankspace with %20
    "&$limit=5"
)

# OK?
query2 = (
    "https://data.cdc.gov/resource/g653-rqe2.json?"
    "$order=date%20DESC"  # replace blankspace with %20
    "&$where=date<'2023-01-01'"

)

# cant
query2 = (
    "https://data.cdc.gov/resource/g653-rqe2.json?"
    #"$select=date,key_plot_id,normalization,pcr_conc_smoothed"
    "$order=date%20DESC"  # replace blankspace with %20
    "&$limit=50000"
    #"&$where=date>='2020-01-01'"
)

d2 = pd.read_json(query2)
d2
d2.date.min()

#d1 = pd.read_json(query1)
d2 = pd.read_json(query2)
d2
d2.date.min()
except json.decoder.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")
except HTTPError as e:
    print(f"HTTP Error: {e}")

raw_data.first_sample_date.min()



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