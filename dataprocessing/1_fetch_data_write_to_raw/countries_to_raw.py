"""##
# Testing to write everything via 
##

import json
import pandas as pd


filename = country + '_wastewater.parquet'


url_filename_dict = {'https://abwassermonitoring.at/cbe1/dl_blverlauf.csv':
                    'austria_wastewater.parquet'}


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




df_source = pd.read_csv('/home/stratega/code/analytics/covid/dataprocessing/metadata/data_sources.csv', sep=',')
df_source

df_source['n_links'] = df_source.groupby('country')['link'].transform('count')
df_source

for i, country in enumerate(df_source['country']):
    print(country)
    filename = country + '_wastewater.parquet'
    data_read_type = df_source[df_source.country==country].data_read_type.iloc[0]
    n_links = df_source[df_source.country==country].n_links.iloc[0]
    link = df_source[df_source.country==country].link.iloc[0]
    print('Reading:',country,link,data_read_type,n_links )


    if (data_read_type == 'direct_link') and (n_links == 1):
        df_original = pd.read_csv(link, sep=';')

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







"""