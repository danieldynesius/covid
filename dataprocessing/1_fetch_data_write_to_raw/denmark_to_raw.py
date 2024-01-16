import requests
from bs4 import BeautifulSoup
import os
import tempfile
import zipfile
import pandas as pd

# Denmark Data
url = 'https://www.ssi.dk/sygdomme-beredskab-og-forskning/sygdomsovervaagning/c/covid-19---spildevandsovervaagning'
filename = 'denmark_wastewater.parquet'

# Send an HTTP request to download the ZIP file
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all <div> elements with class "accordion-body"
    accordion_body_divs = soup.find_all('div', class_='accordion-body')

    # Check if at least two "accordion-body" divs were found
    if len(accordion_body_divs) >= 2:
        # Find the second <div> with class "accordion-body"
        second_accordion_body_div = accordion_body_divs[1]

        # Find the first <ul> element within the second <div>
        first_ul_in_accordion = second_accordion_body_div.find('ul')

        # Check if a <ul> element was found
        if first_ul_in_accordion:
            # Find the first <a> element (anchor) within the first <ul>
            first_a_in_ul = first_ul_in_accordion.find('a')

            # Check if an <a> element was found
            if first_a_in_ul:
                # Get the value of the 'href' attribute
                latest_datalink = first_a_in_ul.get('href')

                # Check if 'latest_datalink' is not empty
                if latest_datalink:
                    print("Link found:")
                    print(latest_datalink)

                    # Specify the target directory
                    target_directory = os.path.expanduser("~/code/analytics/covid/data/1_raw_data")

                    # Create the target directory if it doesn't exist
                    os.makedirs(target_directory, exist_ok=True)

                    # Download the ZIP file directly to the target directory
                    zip_file_path = os.path.join(target_directory, 'denmark_raw_zip')
                    zip_response = requests.get(latest_datalink)

                    # Check if the ZIP file download was successful (status code 200)
                    if zip_response.status_code == 200:
                        with open(zip_file_path, 'wb') as zip_file:
                            zip_file.write(zip_response.content)

                        print(f"ZIP file downloaded to: {zip_file_path}")

                        # Open the ZIP file using BytesIO
                        with zipfile.ZipFile(zip_file_path) as zipped_file:
                            # Initialize the target CSV file name
                            target_csv_name = None

                            # Iterate through the files in the ZIP file
                            for file_name in zipped_file.namelist():
                                # Check if the file matches the specified pattern
                                if file_name.endswith("_region_wastewater_data.csv"):
                                    target_csv_name = file_name

                                    # Read the CSV file into a DataFrame
                                    df = pd.read_csv(zipped_file.open(target_csv_name))

                                    # Print or process the DataFrame as needed
                                    print(f"CSV file found and loaded:\n{df.head(2)}")

                            # If a target CSV file was found, delete other files in the ZIP file
                            if target_csv_name:
                                print(f"CSV file '{target_csv_name}' extracted and other files discarded.")
                            else:
                                print("No CSV file found within the ZIP file.")
                    else:
                        print('Failed to read link!')

# Save the DataFrame as a Parquet file
parquet_filename = f'~/code/analytics/covid/data/1_raw_data/{filename}'
df.to_parquet(parquet_filename, index=False)