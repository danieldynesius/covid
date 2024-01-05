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