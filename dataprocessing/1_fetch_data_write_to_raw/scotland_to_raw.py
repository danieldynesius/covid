from selenium import webdriver
from bs4 import BeautifulSoup

url = 'https://informatics.sepa.org.uk/spotfire/wp/analysis?file=Public/SEPA/Projects/Sewage%20Monitoring/RNAMonitoring_Public&waid=xqnJx0y6QECY99JuZwOV2-2703381a01mbPL&wavid=3'

# Create a new instance of the Chrome driver
driver = webdriver.Chrome()


# Navigate to the specified URL
driver.get(url)

# Get the page source
page_source = driver.page_source

soup = BeautifulSoup(page_source)

for tag in soup.find_all():
    print(tag.text)
soup


# Find all <div> elements with class="sf-root"
sf_root_divs = soup.find_all('div', class_='sf-root')

# Print the text content of each <div> with class="sf-root"
for i, div in enumerate(sf_root_divs, start=1):
    print(f"sf-root div {i} text: {div.text}")

# Find all nested <div> elements
nested_divs = soup.find_all('div', recursive=True)

# Print the text content of each nested <div>
for i, div in enumerate(nested_divs, start=1):
    print(f"Nested div {i} text: {div.text}")






import requests
from bs4 import BeautifulSoup

url = 'https://informatics.sepa.org.uk/spotfire/wp/analysis?file=Public/SEPA/Projects/Sewage%20Monitoring/RNAMonitoring_Public&waid=xqnJx0y6QECY99JuZwOV2-2703381a01mbPL&wavid=3'

# Make a request to the URL and get the HTML content
response = requests.get(url)
html_content = response.text

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Print the tag name and a portion of the content for each tag
for tag in soup.descendants:
    if tag.name:
        # Truncate the content to 50 characters for brevity
        content_preview = tag.text[:50] if tag.text else ""
        print(f"{tag.name}: {content_preview}")