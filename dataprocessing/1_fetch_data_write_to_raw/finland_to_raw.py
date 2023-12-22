# -------------------------------[ DATASET INFO ] -------------------------------
# Reading from:
# https://www.thl.fi/episeuranta/jatevesi/wastewater_weekly_report.html#data
# 
# Needs to traverse webpage to find link.
# Needs way to handle raw file normalization
#--------------------------------------------------------------------------------

import os
import hashlib
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyarrow.parquet as pq
from io import StringIO
import requests


dirpath = '~/code/analytics/covid/data/1_raw_data/'
filename_from_web = 'Coronavirus wastewater monitoring weekly report.csv'
filename_parquet = 'finland_wastewater.parquet'
file_path = f'{dirpath}{filename_from_web}'

def func_remove_finland_csv(file_to_remove=f'{file_path}'):
    # Expand the tilde (~) in the file path to the user's home directory
    rm_path = os.path.expanduser(file_path)

    # Check if the file exists before attempting to delete it
    if os.path.exists(rm_path):
        # Delete the file
        os.remove(rm_path)
        print(f"File '{filename_from_web}' has been deleted.")
    else:
        print(f"File '{filename_from_web}' does not exist.")

    return

func_remove_finland_csv() # run it!

# Set up Firefox options for incognito mode
firefox_options = Options()
firefox_options.add_argument("--private")

# Set up a Firefox profile
profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)  # 0: Desktop, 1: Downloads, 2: Custom Location
# Set additional preferences for handling file types if needed
profile.set_preference("browser.download.dir", f'{dirpath}')
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', f'{dirpath}')

# Set the profile in the options
firefox_options.profile = profile

# Initialize Firefox WebDriver with the custom profile
driver = webdriver.Firefox(options=firefox_options)

# Navigate to the webpage
driver.get("https://www.thl.fi/episeuranta/jatevesi/wastewater_weekly_report.html#data")

try:
    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'nav-tabs'))
    )

    # Find and click the fifth li inside the ul with class 'nav-tabs'
    fifth_li = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'ul.nav-tabs li:nth-child(5)'))
    )
    fifth_li.click()

    # Wait for the page to load again, if needed
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'htmlwidget-3e5899f7c051cb0662e0'))
    )

    # Find the button within the specified div
    csv_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#htmlwidget-3e5899f7c051cb0662e0 button.dt-button.buttons-csv.buttons-html5'))
    )

    # Click on the button to trigger the download
    csv_button.click()

finally:
    # Close the WebDriver
    driver.quit()

df_original = pd.read_csv(f'{dirpath}{filename_from_web}', sep=',')
df_original.to_parquet(f'{dirpath}{filename_parquet}', index=False)

# Read the Parquet file into a new Pandas DataFrame
df_from_parquet = pd.read_parquet(f'{dirpath}{filename_parquet}')

# Check data integrity by comparing the DataFrames
if df_original.equals(df_from_parquet):
    print(f'Data integrity maintained: {filename_parquet}')
else:
    print(f'Data integrity may be compromised: {filename_parquet}')

func_remove_finland_csv()