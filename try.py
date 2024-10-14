import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException, InvalidSelectorException

from config import PROFILE_PATH


def apply_button_click() -> None:
    """Clicks on apply button and checks for suspicious activity dialog-box"""
    try:
        job_description_tab = WebDriverWait(driver, 5).until(
            ec.presence_of_element_located(
                (By.CLASS_NAME, 'scaffold-layout__detail')
            ))
    except TimeoutException:
        job_description_tab = driver

    WebDriverWait(job_description_tab, 5).until(
        ec.element_to_be_clickable(
            (By.CLASS_NAME, 'jobs-apply-button--top-card')
        )).click()

    try:
        WebDriverWait(driver, 1).until(ec.presence_of_element_located(
            (By.XPATH,
             '/html/body/div[3]/div/div/div[1]/h2'
             '[@id="header" and text()="Job search safety reminder"]')
        ))
        single_button_click_xpath(
            '/html/body/div[3]/div/div/div[3]/div/div/button',
            1)
    except TimeoutException:
        print(f"LinkedIn suspicious activity dialog-box not found!")


def single_button_click_xpath(self, xpath, timeout=5) -> bool:
    """Single click on a button using Xpath and a timeout to wait for it to appear"""
    try:
        WebDriverWait(self.driver, timeout).until(ec.element_to_be_clickable(
            (By.XPATH, xpath)
        )).click()
        return True
    except TimeoutException:
        print("Sbc", TimeoutException)
        return False


chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

driver.get("https://www.linkedin.com/jobs/view/4046505776")
apply_button_click()

job_apply_dialog = driver.find_element(
    By.XPATH,
    '//div[@role="dialog" and @aria-labelledby="jobs-apply-header"'
    ' and contains(@class, "artdeco-modal")]'
)
submitted = False

for _ in range(8):
    if job_apply_dialog.is_displayed():
        if not submitted:
            button_element = job_apply_dialog.find_element(
                By.CSS_SELECTOR,
                'button.artdeco-button.artdeco-button--2.artdeco-button--primary'
            )
            print(button_element.text)

            if button_element.text == "Review":
                time.sleep(5)

            if button_element.text == "Submit application":
                submitted = True

            print(len(button_element.text))
            button_element.click()
    else:
        print("No dialog box!")

input()
