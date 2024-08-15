import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from additional_questions_extraction import ExtractQuestionsAndInputs
from additional_questions_form_filler import FormFiller

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


def get_all_job_postings():
    time.sleep(2)

    show_more_jobs_button_xpath = [
        '/html/body/div[4]/div[3]/div/div[3]/div/div/main/'
        'div/div[1]/div[1]/div/div/div/section/div[2]/a/span',
        '/html/body/div[5]/div[3]/div/div[3]/div/div/main/'
        'div/div[1]/div[1]/div/div/div/section/div[2]/a'
    ]
    for xpath in show_more_jobs_button_xpath:
        single_button_click_xpath(xpath, 2)

    time.sleep(2)
    ul_element = WebDriverWait(driver, 5).until(
        ec.presence_of_element_located(
            (By.XPATH, '//*[@id="main"]/div/div[2]/div[1]/div/ul')
        )
    )
    return ul_element.find_elements(By.XPATH, "./li")


def apply_button_click():
    job_description_tab = WebDriverWait(driver, 5).until(
        ec.presence_of_element_located(
            (By.CLASS_NAME, 'scaffold-layout__detail')
        ))
    apply_button = WebDriverWait(job_description_tab, 5).until(
        ec.element_to_be_clickable(
            (By.CLASS_NAME, 'jobs-apply-button--top-card')
        ))
    apply_button.click()

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
        print(f"No Suspicious header found -", TimeoutException)


def next_button_click():
    WebDriverWait(driver, 6).until(ec.presence_of_element_located(
        (By.XPATH,
         '/html/body/div[3]/div/div/div[1]/h2[@id="jobs-apply-header"]')
    ))

    next_button_object = None
    is_apply_button_visible = False

    # List of XPaths to try
    next_button_paths = [
        '/html/body/div[3]/div/div/div[2]/div/div[2]/form/footer/div[2]/button',
        '/html/body/div[3]/div/div/div[2]/div/div/form/footer/div[2]/button',
        '/html/body/div[3]/div/div/div[2]/div/div/form/footer/div[3]/button',
        '/html/body/div[3]/div/div/div[2]/div/div/form/footer/div[3]/button/span'
    ]

    for xpath in next_button_paths:
        try:
            next_button_object = WebDriverWait(driver, 1).until(
                ec.element_to_be_clickable((By.XPATH, xpath))
            )
            is_apply_button_visible = True
            break
        except TimeoutException:
            print(f'TOE - {TimeoutException}')
            continue

    if is_apply_button_visible:
        next_button_object_text = next_button_object.text
        next_button_object.click()
        return next_button_object_text
    else:
        raise TimeoutException


def get_prompt_reference():
    try:
        info_text_xpath = '/html/body/div[3]/div/div/div[2]/div/div[2]/form/div/div/h3'
        info_text = WebDriverWait(driver, 2).until(
            ec.presence_of_element_located((By.XPATH, info_text_xpath))
        ).text

        if info_text in {"Contact info", "Resume", "Education"}:
            return False
        elif info_text == "Work experience":
            work_exp_cancel_button_xpath = (
                '/html/body/div[3]/div/div/div[2]/div/'
                'div[2]/form/div[1]/div/div[2]/button[1]'
            )
            single_button_click_xpath(work_exp_cancel_button_xpath, 1)
            return False
        else:
            print(f"\nDifferent prompt: {info_text}")
            return True

    except TimeoutException:
        print("No prompt found!", TimeoutException)
        return True


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

    nlp_answers = [{"4": "input"}, {"3": "input"}, {"Yes": "radio"}, {"No": "select"}]
    nlp_answers2 = [{"4": "input"}, {"2": "input"}, {"0": "input"}, {"1": "input"},
                    {"0": "input"}, {"0": "input"}, {"300000": "input"}, {"Yes": "select"}]

    form_filler = FormFiller(driver, questions_html_content, nlp_answers)
    form_filler.fill_form()


def submit_additional_apply():
    submit_button_object = False
    submit_button_paths = [
        '/html/body/div[3]/div/div/div[2]/div/div[2]/div/footer/div[3]/'
        'button[2][@aria-label="Submit application"]',
        '/html/body/div[3]/div/div/div[2]/div/div[2]/div/footer/div[2]/'
        'button[2][@aria-label="Submit application"]',
        '/html/body/div[3]/div/div/div[3]/button/span[text()="Done"]',
        '/html/body/div[3]/div/div/div[3]/button'
    ]

    for xpath in submit_button_paths:
        try:
            submit_button = WebDriverWait(driver, 1).until(
                ec.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script(
                "arguments[0].scrollIntoView(true);",
                submit_button
            )
            submit_button.click()
            submit_button_object = True
        except TimeoutException:
            print(f'TOE - {TimeoutException}')
            print("This path not worked-", xpath)
            continue

    if submit_button_object:
        print("Application submitted successfully after filling form.", end="\n\n")
        return True


def close_apply_dialog():
    close_button_paths = [
        '/html/body/div[3]/div/div/button',
        '/html/body/div[3]/div[2]/div/div[3]/button[1]'
    ]

    for xpath in close_button_paths:
        single_button_click_xpath(xpath, 1)

    print("Application disposed!", end="\n\n")


chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
driver.get("https://www.linkedin.com/jobs/")

for li in get_all_job_postings():
    # Scroll the <li> into view and wait for element to visible
    driver.execute_script("arguments[0].scrollIntoView(true);", li)
    WebDriverWait(driver, 2).until(ec.visibility_of(li))

    job_name = " ".join(li.text.split()[0:2])
    print(f"JOB - {job_name}!")
    li.click()

    if "Easy Apply" in li.text:
        apply_button_click()
        time.sleep(1)

        if next_button_click() == "Submit application":
            time.sleep(2)
            single_button_click_xpath('/html/body/div[3]/div/div/button')
            print(f"Applied for the job '{job_name}'!", end="\n\n")

        else:
            while True:
                if get_prompt_reference():
                    # print("Sleeping...")
                    # for i in range(60):
                    #     print(60 - i)
                    #     time.sleep(1)
                    # print("Waking...")
                    get_additional_questions()
                    break

                else:
                    single_button_click_xpath(
                        '/html/body/div[3]/div/div/div[2]/div/'
                        'div[2]/form/footer/div[2]/button[2]'
                    )

                if submit_additional_apply(): break

input("Press Enter to close the browser...")

'/html/body/div[3]/div/div/div[2]/div/div[2]/div/div/h3'  "-- Review your application"

'/html/body/div[3]/div/div/div[1]/h2'  "--Job search safety reminder"
'/html/body/div[3]/div/div/div[3]/div/div/button'  "--Continue applying"
'/html/body/div[3]/div/div/button'  "--dismiss cross"

"/html/body/div[3]/div/div/div[2]/div/div[2]/form/div/div/div/div/fieldset/div/input"  "-- terms agree input checkbox"
"//input[@type='checkbox' and contains(@data-test-text-selectable-option__input, 'I Agree Terms & Conditions')]" "--chatgpt xpath for above"
