import os
import time
import pyautogui
import logging
from paddleocr import PaddleOCR

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from additional_questions_extraction import ExtractQuestionsAndInputs
from answer_form_filler import FillAnswers


# logging.getLogger('ppocr').setLevel(logging.ERROR)
# ocr = PaddleOCR()

PROFILE_PATH = os.path.abspath("selenium_profile")
if not os.path.exists(PROFILE_PATH):
    os.makedirs(PROFILE_PATH)


def single_button_click_xpath(xpath, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(ec.element_to_be_clickable(
            (By.XPATH, xpath)
        )).click()

    except TimeoutException:
        print(TimeoutException)


def apply_button_click():
    apply_button = WebDriverWait(driver, 5).until(
        ec.element_to_be_clickable(
            (By.XPATH,
             '/html/body/div[5]/div[3]/div[2]/div/div/main/div/div[1]'
             '/div/div[1]/div/div/div[1]/div[6]/div/div/div/button')
        ))
    apply_button.click()


def take_apply_form_screenshot(number):
    # Locate the div using its class name or any other selector
    div_element = driver.find_element(By.CSS_SELECTOR, "div.artdeco-modal.jobs-easy-apply-modal")

    has_vertical_scrollbar = driver.execute_script(
        "return arguments[0].scrollHeight > arguments[0].clientHeight;",
        div_element)

    if not has_vertical_scrollbar:
        div_position = div_element.location
        distance_from_left = div_position['x']
        distance_from_top = div_position['y'] + 225

        div_size = div_element.size
        width = div_size['width']
        height = div_size['height'] - 200

        region = (distance_from_left, distance_from_top, width, height)
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(f"question_box_{number}.png")

        # result = ocr.ocr(f'question_box_{number}.png', cls=True)
        # for line in result:
        #     for word_info in line:
        #         box, text = word_info
        #         print(f"{text[0]}")


# def get_additional_questions():
#     div_element = driver.find_element(
#         By.CSS_SELECTOR, "div.artdeco-modal.jobs-easy-apply-modal"
#     )
#     all_questions_elements = div_element.find_elements(
#         By.CSS_SELECTOR, 'div.jobs-easy-apply-form-section__grouping'
#     )
#
#     for ele in all_questions_elements:
#         print(ele.text, end="\n\n")


def get_additional_questions():
    questions_form_div = driver.find_element(
        By.XPATH,
        '/html/body/div[3]/div/div/div[2]/div/div[2]/form/div/div[@class="pb4"]'
    )
    questions_html_content = questions_form_div.get_attribute('outerHTML')

    extractor = ExtractQuestionsAndInputs(questions_html_content)
    questions_list = extractor.extract_questions()

    for ques in questions_list:
        for k, v in ques.items():
            print(f"{k}: {v}")
        print()

    print("Sleeping...")
    for i in range(20):
        print(20 - i)
        time.sleep(1)
    print("Waking...")

    nlp_answers = [{"4": "input"}, {"3": "input"}, {"Yes": "radio"}, {"No": "select"}]
    nlp_answers2 = [{"4": "input"}, {"2": "input"}, {"0": "input"}, {"1": "input"},
                    {"0": "input"}, {"0": "input"}, {"300000": "input"}, {"Yes": "select"}]
    nlp_answers3 = [{"radio": "Yes"}, {"radio": "Yes"}, {"text": "4"}, {"text": "1"}, {"radio": "Yes"}]

    form_filler = FillAnswers(driver, nlp_answers3, questions_list)
    form_filler.fill_answers()


# Assuming driver is already initialized and navigated to the page
chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
driver.get("https://www.linkedin.com/jobs/view/4000150756")

time.sleep(2)
apply_button_click()

time.sleep(2)
single_button_click_xpath(
    '/html/body/div[3]/div/div/div[2]/div/div[2]/form/footer/div[2]/button',
    2
)

time.sleep(2)
single_button_click_xpath(
    '/html/body/div[3]/div/div/div[2]/div/div[2]/form/footer/div[2]/button[2]',
    2
)

time.sleep(5)
# single_button_click_xpath(
#     '/html/body/div[3]/div/div/div[2]/div/div[2]/form/footer/div[2]/button[2]',
#     2
# )
# take_apply_form_screenshot(1)

# time.sleep(2)
# single_button_click_xpath(
#     '/html/body/div[3]/div/div/div[2]/div/div[2]/form/footer/div[2]/button[2]',
#     2
# )

get_additional_questions()

driver.quit()
