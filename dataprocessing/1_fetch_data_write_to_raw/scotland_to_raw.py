import os
import time  # Import the time module
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

dirpath = '~/code/analytics/covid/data/1_raw_data/'
filename_from_web = 'RNAMonitoring_Public - Result Description - N1 Gene, Reported Value - N1 Gene (gc-l), Days Since.csv'
filename_parquet = 'scotland_wastewater.parquet'
file_path = f'{dirpath}{filename_from_web}'

def func_remove_finland_csv(file_to_remove=f'{file_path}'):
    rm_path = os.path.expanduser(file_path)
    if os.path.exists(rm_path):
        os.remove(rm_path)
        print(f"File '{filename_from_web}' has been deleted.")
    else:
        print(f"File '{filename_from_web}' does not exist.")
    return

# func_remove_finland_csv()

firefox_options = Options()
firefox_options.add_argument("--private")

profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.dir", f'{dirpath}')
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

firefox_options.profile = profile

driver = webdriver.Firefox(options=firefox_options)

# Navigate to the webpage
driver.get("https://informatics.sepa.org.uk/RNAmonitoring/")

try:
    # Wait for the element with ID 'sepa_rnamonitoringId' to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'sepa_rnamonitoringId'))
    )
    print("Before waiting for ID 'id36'")
    div_with_id = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'id36'))
    )
    print("After waiting for ID 'id36'")
    # Find the first div with class "HtmlTextArea" after the div with ID "id36"
    first_div_after_id36 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="id36"]/following-sibling::div[contains(@class, "HtmlTextArea")]'))
    )
    
    WebDriverWait(driver, 10).until(
        lambda driver: driver.execute_script('return document.readyState') == 'complete'
    )    

# Perform some action on the found div, for example, print its text
    print(first_div_after_id36.text)
    # Click on the 7th p element
    seventh_p_center.click()

    # Find the body element with class "sfx_body_190"
    body_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'sfx_body_190'))
    )

    # Find the div with class "sfx_root_191" (or adjust the class name accordingly)
    target_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'sfx_root_191'))
    )
    # Perform some action on the found div, for example, print its text
    print(target_div.text)

finally:
    driver.quit()
