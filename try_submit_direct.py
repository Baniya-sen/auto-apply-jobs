import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


PROFILE_PATH = os.path.abspath("selenium_profile")
if not os.path.exists(PROFILE_PATH):
    os.makedirs(PROFILE_PATH)


chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
driver.get("https://www.linkedin.com/jobs/view/3964547213")

apply_button = WebDriverWait(driver, 5).until(ec.element_to_be_clickable(
        (By.CLASS_NAME, 'jobs-apply-button--top-card')
    ))
apply_button.click()
time.sleep(2)

is_next = False

continue_button_paths = [
    '/html/body/div[3]/div/div/div[2]/div/div[2]/form/footer/div[2]/button',
    '/html/body/div[3]/div/div/div[2]/div/div/form/footer/div[2]/button',
    '/html/body/div[3]/div/div/div[2]/div/div/form/footer/div[3]/button',
    '/html/body/div[3]/div/div/div[2]/div/div/form/footer/div[3]/button/span'
]

for xpath in continue_button_paths:
    try:
        next_button_object = WebDriverWait(driver, 1).until(
            ec.element_to_be_clickable((By.XPATH, xpath))
        )
        print(xpath)
        is_next = True
        break
    except TimeoutException:
        print(f'TOE - {TimeoutException}')
        continue

if is_next:
    driver.execute_script("arguments[0].scrollIntoView(true);", next_button_object)
    text_item = next_button_object.text
    next_button_object.click()
    print(text_item)

input("Press Enter to close the browser...")
