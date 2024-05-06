
# -------------------------------[ DATASET INFO ] -------------------------------
# https://www.poznan.pl/mim/wortals/wortal,285/news,9341/monitoring-sars-cov-2-w-sciekach,183099.html
# also has more datasets with variables
# 
#--------------------------------------------------------------------------------
import requests
import pandas as pd
import requests
import hashlib
import pyarrow.parquet as pq

# Download data (replace the URL with your actual data URL)

url_filename_dict = {'https://www.poznan.pl/mim/public/wortals/attachments.att?co=show&instance=9341&parent=183099&lang=pl&id=432849':
                    'poland_wastewater.parquet'}


# Use a dict to read URL, and associate file name with URL
for url, filename in url_filename_dict.items():
    # Read the CSV file into a Pandas DataFrame
    df_original = pd.read_csv(url, sep=';')

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
