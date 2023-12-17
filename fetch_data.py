from bs4 import BeautifulSoup
import requests

#url = 'https://www.thl.fi/episeuranta/jatevesi/wastewater_weekly_report.html' # FINLAND
url = 'https://www.rki.de/DE/Content/Institut/OrgEinheiten/Abt3/FG32/Abwassersurveillance/Bericht_Abwassersurveillance.html?__blob=publicationFile'

# user visit emulation
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

try:
    page = requests.get(url, headers=headers, timeout=8)

    # Check if the request was successful (status code 200)
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, 'html.parser')
        print(soup.prettify())
    else:
        print(f"Failed to retrieve the page. Status code: {page.status_code}")

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")


soup.p

import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the webpage
url = 'https://www.rki.de/DE/Content/Institut/OrgEinheiten/Abt3/FG32/Abwassersurveillance/Bericht_Abwassersurveillance.html?__blob=publicationFile'

# Make a GET request to the webpage
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract data based on HTML structure
    # Example: Get all text from <div class="example-class">
    data_elements = soup.find_all('div', class_='nav nav-tabs')

    # Process data and create a DataFrame
    data_list = [element.text for element in data_elements]
    df = pd.DataFrame(data_list, columns=['Column_Name'])

    # Display the DataFrame
    print(df)

else:
    print(f"Error: Unable to retrieve the webpage (Status Code: {response.status_code})")

script_tags = soup.find_all('script', type='application/json')

# Print the content of each script tag
for script_tag in script_tags:
    print(script_tag.text.strip())


# Extract the JSON data from the script tag
start_index = data_script.find('{')
end_index = data_script.rfind('}')
json_data = data_script[start_index:end_index + 1]

# Parse the JSON data
parsed_data = json.loads(json_data)

# Create a DataFrame from the parsed data
df = pd.DataFrame(parsed_data['map']).T.reset_index()
df.columns = ['city', 'id_list']

# Convert the id_list column to a list of integers
df['id_list'] = df['id_list'].apply(lambda x: json.loads(x))

# Display the DataFrame
print(df.head())



import json

# Parse JSON
data = json.loads(json_data)

# Convert to DataFrame
df = pd.DataFrame({
    'City': data['items']['value'],
    'Label': data['items']['label'],
    'IDs': [data['map'][city] for city in data['items']['value']]
})

# Display the DataFrame
print(df)



####
from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
from pandas import json_normalize

# URL of the webpage
url = 'https://www.rki.de/DE/Content/Institut/OrgEinheiten/Abt3/FG32/Abwassersurveillance/Bericht_Abwassersurveillance.html?__blob=publicationFile'

# Make a GET request to the webpage
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract JSON data from script tags
    script_tags = soup.find_all('script', type='application/json')

    df = json_normalize(script_tags['rows']) 


    # Display the DataFrame
    df

else:
    print(f"Error: Unable to retrieve the webpage (Status Code: {response.status_code})")

d = {"page":1,"rows":[{"id":"160128","cell":{"fund_id":"160128","bond_ratio":"132.04","report_dt":"2019-12-31","is_outdate":False,"maturity_dt_tips":""}},{"id":"160130","cell":{"fund_id":"160130","bond_ratio":"165.29","report_dt":"2019-12-31","is_outdate":False,"maturity_dt_tips":""}},{"id":"160131","cell":{"fund_id":"160131","bond_ratio":"94.93","report_dt":"2019-12-31","is_outdate":False,"maturity_dt_tips":""}}],"total":3}
type(d)
df = json_normalize(d['rows']) 
type(script_tags)
json_normalize(script_tags['map'])

