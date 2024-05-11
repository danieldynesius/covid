import requests
from bs4 import BeautifulSoup
import json
import configparser
import os
import pandas as pd


config_file = os.path.expanduser('~/code/analytics/covid/conf.ini')

# Read the Conf file
config = configparser.ConfigParser()
config.read(config_file)

# Paths
article_data = config.get('Paths', 'article_data')

# parse with df
df = pd.read_json(article_data)
already_existing_articles_list = list(df.article_url)

# keep in json
f = open(article_data)
article_data = json.load(f)


# Note, this is the last 30 days in order of Relevabce
url = "https://www.nature.com/search?q=covid-19%20sars-cov-2&date_range=last_30_days&order=relevance"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all links to articles within the specified section
article_links = soup.select('#search-article-list a')
# Iterate through the article links and scrape the text

stem = 'https://www.nature.com'


# Original Prototype (Slow but understandable as backup)

# Initialize an empty list to store article information
already_existing_articles_df = pd.DataFrame(already_existing_articles_list, columns=['href'])


article_list = []
article_nr = 0
for article_link in article_links:
    article_nr += 1
    """
    if article_nr > 1:
        print('breaking out of loop')
        break
    """
    article_url = stem + article_link['href']


    if article_url in already_existing_articles_df['href'].values:
        print('article',article_nr, 'url:', article_url, 'href already exists in list. Skipping to next article')
        continue
    else:
        print('article',article_nr, 'url:', article_url, 'href does NOT exists in list. Opening Link & Parsing it.')
    """
    for existing_link in already_existing_articles_list:
        if existing_link == article_url:
            
            # Do something if the href already exists
            print('article',article_nr, 'url:', article_url, 'href already exists in list')

            # If it already exist we skip this article
            # to only read new articles
            break
    else:
        # Do something if the href does not exist
        print('article',article_nr, 'url:', article_url, 'href does NOT exists in list')

    """
    # Navigate to the article URL
    article_response = requests.get(article_url)
    article_soup = BeautifulSoup(article_response.text, 'html.parser')
    article_header = article_soup.find('h1', class_='c-article-title')

    # Assuming you have the BeautifulSoup object 'article_soup'
    try: 
        article_publicationdate = article_soup.select_one('.c-article-identifiers__item time')
        if article_publicationdate:
            publication_date = article_publicationdate['datetime']
        else:
            publication_date = "No time element found."

    except Exception as e:
        print(f"An error occurred: {e}")
        publication_date = "Error occurred while extracting publication date."



    # Assuming you have the BeautifulSoup object 'soup'
    abs1_section_div = article_soup.find('div', id='Abs1-section')

    # Check if the div is found
    if abs1_section_div:
        # Find all paragraphs within the div
        paragraphs = abs1_section_div.find_all('p')

        # Extract the text from each paragraph
        paragraph_text = [paragraph.get_text(strip=True) for paragraph in paragraphs]
    else:
        paragraph_text = ["No div with ID 'Abs1-section' found."]

    # Initialize a dictionary to store article information
    article_info = {
        "article_title": article_header.get_text() if article_header else "No title found.",
        "publication_date": publication_date,
        "abstract": paragraph_text,
        "article_url": article_url,
        "needs_ai_processing": 1
    }

    # Append the dictionary to the list
    article_list.append(article_info)

# Convert the list to JSON
json_data = json.dumps(article_list, ensure_ascii=False, indent=2)

# Print or save the JSON data
#print(json_data)

json_data
article_data
"""
article_data = json.dumps(article_data)
article_data = json.loads(article_data)
"""
json_data = json.loads(json_data)

new_and_old_articles = article_data + json_data
print(new_and_old_articles)

# Save the JSON data to a file
with open("article_data.json", "w", encoding="utf-8") as json_file:
    json.dump(new_and_old_articles, json_file, ensure_ascii=False, indent=2)

   

#df = pd.read_json("article_data.json", orient="records")
#df.article_title[0]
#df.abstract[0]




# Fast but witchcraft (ok to use until it breaks)
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json

async def fetch_article(session, article_url):
    async with session.get(article_url) as response:
        return await response.text()

async def process_article(article_link):
    article_url = stem + article_link['href']
    print('article url:', article_url)

    async with aiohttp.ClientSession() as session:
        article_html = await fetch_article(session, article_url)

    article_soup = BeautifulSoup(article_html, 'html.parser')
    article_header = article_soup.find('h1', class_='c-article-title')
    # Assuming you have the BeautifulSoup object 'article_soup'
    try: 
        #article_publicationdate = article_soup.select_one('a[href="#article-info"] time')
        article_publicationdate = article_soup.select_one('.c-article-identifiers__item time')
        
        if article_publicationdate:
            publication_date = article_publicationdate['datetime']
        else:
            publication_date = "No time element found."

    except Exception as e:
        print(f"An error occurred: {e}")
        publication_date = "Error occurred while extracting publication date."
    # Assuming you have the BeautifulSoup object 'soup'
    abs1_section_div = article_soup.find('div', id='Abs1-section')

    # Check if the div is found
    if abs1_section_div:
        # Find all paragraphs within the div
        paragraphs = abs1_section_div.find_all('p')

        # Extract the text from each paragraph
        paragraph_text = ' '.join(paragraph.get_text(strip=True) for paragraph in paragraphs)
    else:
        paragraph_text = "No div with ID 'Abs1-section' found."
    # ... (rest of the processing)

    return {
        "article_title": article_header.get_text() if article_header else "No title found.",
        "publication_date": publication_date,
        "abstract": paragraph_text,
        "article_url": article_url,
        "layman_title": "",
        "layman_abstract": "",
        "needs_ai_processing": 0
    }

async def main():
    tasks = [process_article(article_link) for article_link in article_links]

    # Gather and process articles concurrently
    articles = await asyncio.gather(*tasks)

    # Convert the list to JSON
    json_data = json.dumps(articles, ensure_ascii=False, indent=2)

    # Print or save the JSON data
    print(json_data)

    # Optionally, save the JSON data to a file
    with open(new_research_dump, "w", encoding="utf-8") as json_file:
        json.dump(articles, json_file, ensure_ascii=False, indent=2)
"""
# For running through console etc

"""
if __name__ == "__main__":
    if hasattr(__builtins__, '__IPYTHON__') and __IPYTHON__:
        # Running in an IPython (Jupyter) environment
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.run(main())
    else:
        # Running in a non-interactive environment
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
"""



# ATTEMPT
"""
print('Checking for New Articles to append')
# Load existing data from the JSON file
existing_articles = []

if os.path.isfile(existing_research_articles):
    with open(existing_research_articles, 'r') as file:
        try:
            existing_articles = json.load(file)
        except json.JSONDecodeError as e:
            print("Error decoding existing JSON file:", e)

# Compare existing articles with the new articles based on article_url
new_articles = []

async def process_and_append(article_link):
    article_url = stem + article_link['href']
    if not any(article['article_url'] == article_url for article in existing_articles):
        new_article = await process_article(article_link)
        
        # Set "needs_ai_processing" to 1 to process for new articles in the next script
        new_article["needs_ai_processing"] = 1
        new_articles.append(new_article)

# Run the article processing asynchronously
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(*(process_and_append(article_link) for article_link in article_links)))

# Append new articles to existing data
existing_articles.extend(new_articles)

# Convert the list to JSON
json_data = json.dumps(existing_articles, ensure_ascii=False, indent=2)

# Print or save the JSON data
print(json_data)

# Save the updated JSON data to the file
with open(existing_research_articles, "w", encoding="utf-8") as json_file:
    json.dump(existing_articles, json_file, ensure_ascii=False, indent=2)
"""

print('Nature Articles Downloaded!')