import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

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


def single_button_click_xpath(xpath, timeout=5) -> bool:
    """Single click on a button using Xpath and a timeout to wait for it to appear"""
    try:
        WebDriverWait(driver, timeout).until(ec.element_to_be_clickable(
            (By.XPATH, xpath)
        )).click()
        return True
    except TimeoutException:
        print("Sbc", TimeoutException)
        return False


def close_submit_dialog_box() -> None:
    """Clicks on the close button on box that appears after submitting application"""
    close_submit_button_paths = [
        '/html/body/div[3]/div/div/div[3]/button',
        '/html/body/div[3]/div/div/button',
        '/html/body/div[3]/div/div/button/svg',
    ]
    for xpath in close_submit_button_paths:
        try:
            close_button = WebDriverWait(driver, 1).until(
                ec.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script(
                "arguments[0].scrollIntoView(true);",
                close_button
            )
            close_button.click()
        except TimeoutException:
            continue


def get_prompt_reference(apply_box_dialog) -> bool:
    """Extracts text from form headline to identify if the form requires
       additional questions to fill, or it is basic requirements"""
    info_text = ""
    prompts_paths = ['h3.t-16.t-bold', 'h3.t-16.mb2']

    for xpath in prompts_paths:
        try:
            info_text = WebDriverWait(apply_box_dialog, 1).until(
                ec.presence_of_element_located(
                    (By.CSS_SELECTOR, xpath)
                )).text
            break
        except TimeoutException:
            print("No prompt found!")

    if info_text in {"Resume", "Education"}:
        return False
    elif info_text == "Work experience":
        work_exp_cancel_xpath = (
            '/html/body/div[3]/div/div/div[2]/div/'
            'div[2]/form/div[1]/div/div[2]/button[1]'
        )
        return not single_button_click_xpath(work_exp_cancel_xpath, 1)

        # apply_box_dialog.find_element(
        #     By.XPATH,
        #     "//button[contains(@class, 'artdeco-button')]//*[contains(text(), 'Cancel')]"
        # ).click()
    else:
        print(f"\nReference prompt: {info_text}")
        return True


chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

driver.get("https://www.linkedin.com/jobs/view/4047813601")

# ul_element = WebDriverWait(driver, 5).until(
#             ec.presence_of_element_located(
#                 (By.XPATH, '//*[@id="main"]/div/div[2]/div[1]/div/ul')
#             )
#         )
#
# all_li_elements = ul_element.find_elements(By.XPATH, "./li")
# all_li_elements[0].click()

apply_button_click()

job_apply_dialog = driver.find_element(
    By.XPATH,
    '//div[@role="dialog" and @aria-labelledby="jobs-apply-header"'
    ' and contains(@class, "artdeco-modal")]'
)

try:
    for _ in range(8):
        get_prompt_reference(job_apply_dialog)

        button_element = job_apply_dialog.find_element(
            By.CSS_SELECTOR,
            'button.artdeco-button.artdeco-button--2.artdeco-button--primary'
        )
        print(button_element.text)
        print(len(button_element.text))

        if button_element.text == "Review":
            time.sleep(5)

        if button_element.text == "Next":
            time.sleep(4)

        if button_element.text == "Submit application":
            time.sleep(5)
            break
        else:
            button_element.click()

except StaleElementReferenceException:
    print("No box!")

input("Enter...")
