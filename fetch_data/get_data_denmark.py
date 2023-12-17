import requests
from bs4 import BeautifulSoup

url = "https://files.ssi.dk/covid19/spildevandEN/data/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Find the most recent file link
latest_file_link = url + soup.find("a", href=lambda href: href and href.startswith("data"))["href"]

# Download the most recent file
response = requests.get(latest_file_link)
with open(latest_file_link.split("/")[-1], "wb") as file:
    file.write(response.content)
