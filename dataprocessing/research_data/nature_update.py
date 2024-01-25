import requests
from bs4 import BeautifulSoup
import json

# Note, this is the last 30 days in order of Relevabce
url = "https://www.nature.com/search?q=covid-19%20sars-cov-2&date_range=last_30_days&order=relevance"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all links to articles within the specified section
article_links = soup.select('#search-article-list a')
# Iterate through the article links and scrape the text

stem = 'https://www.nature.com'


# Original Prototype (Slow but understandable as backup)
"""
# Initialize an empty list to store article information
article_list = []

for article_link in article_links:
    article_url = stem + article_link['href']
    print('article url:', article_url)

    # Navigate to the article URL
    article_response = requests.get(article_url)
    article_soup = BeautifulSoup(article_response.text, 'html.parser')
    article_header = article_soup.find('h1', class_='c-article-title')

    # Assuming you have the BeautifulSoup object 'article_soup'
    article_publicationdate = article_soup.find('a', href='#article-info').find('time')

    # Check if the time element is found
    if article_publicationdate:
        # Extract the datetime attribute
        publication_date = article_publicationdate['datetime']
    else:
        publication_date = "No time element found."

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
        "paragraphs": paragraph_text,
        "article_url": article_url
    }

    # Append the dictionary to the list
    article_list.append(article_info)

# Convert the list to JSON
json_data = json.dumps(article_list, ensure_ascii=False, indent=2)

# Print or save the JSON data
print(json_data)

# Optionally, save the JSON data to a file
with open("article_data.json", "w", encoding="utf-8") as json_file:
    json.dump(article_list, json_file, ensure_ascii=False, indent=2)
"""
"""
import pandas as pd
df = pd.read_json("article_data.json", orient="records")
df.article_title[0]
df.paragraphs[0]
paragraphs_string = ''.join(df.paragraphs[0])
"""

# Fast but witchcraft (ok to use until it breaks)
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
    article_publicationdate = article_soup.find('a', href='#article-info').find('time')

    # Check if the time element is found
    if article_publicationdate:
        # Extract the datetime attribute
        publication_date = article_publicationdate['datetime']
    else:
        publication_date = "No time element found."

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
    # ... (rest of the processing)

    return {
        "article_title": article_header.get_text() if article_header else "No title found.",
        "publication_date": publication_date,
        "paragraphs": paragraph_text,
        "article_url": article_url
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
    with open("article_data.json", "w", encoding="utf-8") as json_file:
        json.dump(articles, json_file, ensure_ascii=False, indent=2)

# For running through console etc
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

# For running in interactive mode
"""
if __name__ == "__main__":
    await main()
"""
