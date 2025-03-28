# -------------------------------[ DATASET INFO ] -------------------------------
# utilizing "accessURL" from:
# https://raw.githubusercontent.com/robert-koch-institut/Abwassersurveillance_AMELAG/main/amelag_einzelstandorte.tsv
#--------------------------------------------------------------------------------
import requests
import pandas as pd
import requests
import hashlib
import pyarrow.parquet as pq

# Download data (replace the URL with your actual data URL)

url_filename_dict = {'https://raw.githubusercontent.com/robert-koch-institut/Abwassersurveillance_AMELAG/main/amelag_einzelstandorte.tsv':
                    'germany_wastewater.parquet'}


# Use a dict to read URL, and associate file name with URL
for url, filename in url_filename_dict.items():
    # Read the CSV file into a Pandas DataFrame
    df_original = pd.read_csv(url, sep='\t')

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
