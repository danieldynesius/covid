# -------------------------------[ DATASET INFO ] -------------------------------
# Source Data:
# https://data.cdc.gov/Public-Health-Surveillance/NWSS-Public-SARS-CoV-2-Concentration-in-Wastewater/g653-rqe2/about_data
# https://data.cdc.gov/Public-Health-Surveillance/NWSS-Public-SARS-CoV-2-Wastewater-Metric-Data/2ew6-ywp6/about_data
#--------------------------------------------------------------------------------

import pandas as pd
from datetime import datetime as dt
from datetime import timedelta

date_threshold = (dt.now() - timedelta(days=365)).date()
date_threshold_str = date_threshold.strftime('%Y-%m-%d')
filename = 'usa_wastewater.parquet'

wastewaterdata_query = (
    "https://data.cdc.gov/resource/g653-rqe2.json?"
    "$order=date%20DESC"  # replace blankspace with %20
    f"&$where=date>='{date_threshold_str}'"
    "&$limit=500000"
    )

wastewatermetadata_query = (
    "https://data.cdc.gov/resource/2ew6-ywp6.json?"
    "$select=wwtp_jurisdiction,reporting_jurisdiction,key_plot_id,county_names,first_sample_date,date_start"
    "&$order=first_sample_date%20DESC"  # replace blankspace with %20
    f"&$where=first_sample_date>='{date_threshold_str}'"
    "&$limit=500000"
    )

# TODO: CHECK FIRST SAMPLE DATE!! IS IT CORRECTLY USED BY ME??

d1 = pd.read_json(wastewaterdata_query)
d2 = pd.read_json(wastewatermetadata_query)
d2.first_sample_date = pd.to_datetime(d2.first_sample_date)
d2.date_start = pd.to_datetime(d2.date_start)

df_original = d1.merge(d2, how='inner', left_on=['key_plot_id'], right_on=['key_plot_id'])

try:
    # Check if 'pcr_conc_smoothed' column exists
    if 'pcr_conc_lin' in df_original.columns:
        df_original.dropna(subset=['pcr_conc_smoothed'], inplace=True)
    else:
        print("WARNING: 'pcr_conc_lin' column not found in the DataFrame. TROUBLE RUNNING DATA UPDATE!")

except Exception as e:
    print(f"An error occurred while processing 'pcr_conc_smoothed': {e}")

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