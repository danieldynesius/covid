from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up the Selenium WebDriver (make sure you have the appropriate driver installed)
driver = webdriver.Chrome()

# Navigate to the webpage
driver.get("https://www.thl.fi/episeuranta/jatevesi/wastewater_weekly_report.html#data")

try:
    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))
    )

    # Step 1: Click on the fifth li inside the first ul
    fifth_li = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'ul:first-child li:nth-child(5) a[role="tab"][data-toggle="tab"]'))
    )
    fifth_li.click()

    # Step 2: Click the button with the specified class
    csv_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.dt-button.buttons-csv.buttons-html5'))
    )
    csv_button.click()

    # Wait for the download to complete if needed

finally:
    # Close the WebDriver
    driver.quit()
https://www.thl.fi/episeuranta/jatevesi/wastewater_weekly_report.html#data
https://www.thl.fi/episeuranta/jatevesi/wastewater_weekly_report.html#data