##
# Testing to write everything via 
##
"""

import pandas as pd
import subprocess





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
        df_original.head(2)

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


    elif (country == 'finland'):
        script_path = '/home/stratega/code/analytics/covid/dataprocessing/1_fetch_data_write_to_raw/finland_to_raw.py'
        try:
            subprocess.run(['python3', script_path])
        except Exception as e:
            print(f"Error: {e}")

    elif (country == 'denmark'):
        script_path = '/home/stratega/code/analytics/covid/dataprocessing/1_fetch_data_write_to_raw/denmark_to_raw.py'
        try:
            subprocess.run(['python3', script_path])
        except Exception as e:
            print(f"Error: {e}")

    elif (country == 'scotland'):
        script_path = '/home/stratega/code/analytics/covid/dataprocessing/1_fetch_data_write_to_raw/scotland_to_raw.py'
        try:
            subprocess.run(['python3', script_path])
        except Exception as e:
            print(f"Error: {e}")

    elif (country == 'switzerland'):
        script_path = '/home/stratega/code/analytics/covid/dataprocessing/1_fetch_data_write_to_raw/switzerland_to_raw.py'
        try:
            subprocess.run(['python3', script_path])
        except Exception as e:
            print(f"Error: {e}")


    elif (country == 'usa'):
        script_path = '/home/stratega/code/analytics/covid/dataprocessing/1_fetch_data_write_to_raw/usa_to_raw.py'
        try:
            subprocess.run(['python3', script_path])
        except Exception as e:
            print(f"Error: {e}")





"""

df = pd.DataFrame(data)

# Convert DataFrame to HTML
html_table = df.to_html(index=False)

# Save the HTML to a file
with open('output.html', 'w') as f:
    f.write(html_table)