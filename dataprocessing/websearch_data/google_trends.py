from pytrends.request import TrendReq
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Set up the pytrends object
pytrends = TrendReq(hl='en-US', tz=360)

# Define your search term and location
search_term = 'covid'
location = 'SE'

# Build the payload for the last 365 days
pytrends.build_payload(kw_list=[search_term], timeframe='today 365-d', geo=location)

# Get the interest over time data
interest_over_time_df = pytrends.interest_over_time()

# Print the data for reference
print(interest_over_time_df)

# Plot the data
plt.figure(figsize=(10, 6))
interest_over_time_df[search_term].plot(title=f'Google Search Trend for "{search_term}" in {location} (Last 365 Days)')
plt.xlabel('Date')
plt.ylabel('Search Interest')
plt.show()


pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)
###


### GETS RATE LIMITED AFTER 3-4

#Setup and Import Required Libraries
import pandas as pd
from pytrends.request import TrendReq


# Define your search term and location
search_term = 'covid'
location = 'SE'

pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25), geo=location)


# build payload

kw_list = ["covid"] # list of keywords to get data 
pytrends.build_payload(kw_list, cat=0, timeframe='today 1-y') 
#1 Interest over Time
data = pytrends.interest_over_time() 
data = data.reset_index() 

import plotly.express as px
fig = px.line(data, x="date", y=['covid'], title='Keyword Web Search Interest Over Time')
fig.show() 



########################## ADD PROXIES?
import pandas as pd
from pytrends.request import TrendReq

# Set up pytrends without proxies initially
pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))

# Define a list of proxies
proxies_list = [
    'http://2.189.59.3',
    'http://66.225.254.16',
    'http://123.30.154.171:7777',
    'http://162.223.94.164:80',
    'http://66.225.254.16:80',
]

# Function to change proxy for each request
def change_proxy():
    proxy = proxies_list.pop(0)
    proxies = {'https': proxy}
    pytrends.requests_args.update({'proxies': proxies})
    proxies_list.append(proxy)

# Example: Query Google Trends API with proxy rotation
kw_list = ["covid"]
change_proxy()  # Change the proxy before the first request

try:
    pytrends.build_payload(kw_list, cat=0, timeframe='today 1-y')
    interest_over_time_df = pytrends.interest_over_time()
    print(interest_over_time_df)
except Exception as e:
    print(f"Error: {e}")
finally:
    change_proxy()  # Rotate to the next proxy after the request

# Continue making requests or handle retries as needed
