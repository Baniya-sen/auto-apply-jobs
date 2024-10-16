import csv
import time
from datetime import datetime

from selenium.common.exceptions import ElementClickInterceptedException, InvalidSelectorException
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from config import DEFAULT_ANSWERS, JOB_APPLY_TARGET, JOBS_POSTING_LOG_PATH
from extractor import ExtractQuestionsAndInputs
from filler import FillAnswers
from model import QuestionAnsweringModel

DEFAULT_LINK = "https://www.linkedin.com/jobs/collections/recommended/"


class LinkedInApply:
    def __init__(self, driver: WebDriver, model: QuestionAnsweringModel, link=None):
        """LinkedIn class to apply to all LinkedIn easy-apply jobs through Selenium webdriver"""
        self.driver = driver
        self.model = model
        self.job_info = []
        self.all_jobs_count = 1
        self.jobs_traversed = 0
        self.jobs_applied = 0
        self.link = DEFAULT_LINK if not link else link

    def apply_to_jobs(self) -> None:
        """Continue applying for jobs till target is hit."""
        while JOB_APPLY_TARGET != self.jobs_applied:
            self.driver.get(self.link)
            if self.driver.current_url != self.link:
                self.is_user_logged_in()

            for job in self.get_all_job_postings():
                self.driver.execute_script("arguments[0].scrollIntoView(true);", job)
                WebDriverWait(self.driver, 2).until(ec.visibility_of(job))

                self.get_job_info(job_element=job)
                print(f"Processing job: {self.job_info[0]}, located in {self.job_info[2]}")

                try:
                    job.click()
                except ElementClickInterceptedException:
                    print("Failed to click job posting due to an overlay.\n")
                    continue

                if self.easy_apply(job.text):
                    self.jobs_traversed += 1

    def is_user_logged_in(self):
        logged_in = True
        opened_link = self.driver.current_url

        if "authwall" in opened_link or "login" in opened_link:
            logged_in = False
        else:
            try:
                WebDriverWait(self.driver, 1).until(
                    ec.presence_of_element_located((By.XPATH, "//a[contains(., 'Join now')]"))
                )
                logged_in = False
            except TimeoutException:
                pass

        while not logged_in:
            page_state = self.driver.execute_script('return document.readyState;')
            if page_state == 'complete':
                if (self.link in self.driver.current_url
                        or "https://www.linkedin.com/feed" in self.driver.current_url):
                    print("SUCCESS: You are now logged-in.")
                    self.driver.get(self.link)
                    break

    def get_all_job_postings(self):
        """Extract all jobs posting from UL element"""
        ul_element = WebDriverWait(self.driver, 5).until(
            ec.presence_of_element_located(
                (By.XPATH, '//*[@id="main"]/div/div[2]/div[1]/div/ul')
            )
        )
        all_li_elements = ul_element.find_elements(By.XPATH, "./li")
        self.all_jobs_count = len(all_li_elements)
        return all_li_elements

    def get_job_info(self, job_element) -> None:
        """Saves Job position, Organisation name, and Jobs location in a list"""
        self.job_info = []

        job_info_paths = [
            ".//a[contains(@class, 'job-card-list__title')]//span/strong",
            ".//span[@class='job-card-container__primary-description ']",
            ".//li[@class='job-card-container__metadata-item ']"
        ]
        for i, xpath in enumerate(job_info_paths):
            info = job_element.find_element(By.XPATH, xpath)
            info = info.text.split(",")[0] if i == 2 else info.text
            self.job_info.append(info)
        try:
            exp_level_info = WebDriverWait(self.driver, 1).until(
                ec.presence_of_all_elements_located(
                    (By.CSS_SELECTOR,
                     "li.job-details-jobs-unified-top-card__job-insight."
                     "job-details-jobs-unified-top-card__job-insight--highlight "
                     "span.job-details-jobs-unified-top-card__job-insight-view-model-secondary")
                ))
            exp_level_info = exp_level_info[1].text if len(exp_level_info) == 2 else None
        except TimeoutException:
            exp_level_info = None
        self.job_info.append(exp_level_info)

    def easy_apply(self, job_description="Easy Apply") -> bool:
        """Easily apply for a job by filling out the form and answering any additional questions."""

        if "Easy Apply" not in job_description or not self.apply_button_click():
            self.save_job_for_later()
            return False

        apply_dialog_box = self.get_apply_dialog_box()
        if not apply_dialog_box:
            return False

        for attempt in range(7):
            try:
                continue_button = WebDriverWait(apply_dialog_box, 5).until(
                    ec.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'button.artdeco-button.artdeco-button--2.artdeco-button--primary')
                    ))
                if continue_button.text == "Submit application":
                    continue_button.click()
                    print(f"Successfully applied for: {self.job_info[0]}, at {self.job_info[1]}!\n")
                    self.jobs_applied += 1
                    self.log_applied_job("LinkedIn")
                    self.close_submit_dialog_box()
                    return True

                if self.get_prompt_reference(apply_dialog_box):
                    self.fill_out_answers(self.get_additional_questions())

                continue_button.click()
            except TimeoutException:
                if attempt == 6:
                    self.close_apply_dialog(apply_dialog_box)
                    return False

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

    def apply_button_click(self) -> bool:
        """Clicks on apply button and checks for suspicious activity dialog-box"""
        apply_button_clicked = False
        try:
            WebDriverWait(self.driver, 5).until(
                ec.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'jobs-apply-button')"
                               " and contains(., 'Easy Apply')]")
                )).click()
            apply_button_clicked = True
        except TimeoutException:
            print("Easy Apply button not found!")

        # LinkedIn's "Job search safety reminder" dialog-box check and close
        if apply_button_clicked:
            try:
                safety_reminder_box = WebDriverWait(self.driver, 1).until(
                    ec.presence_of_element_located(
                        (By.XPATH,
                         '//div[@role="dialog" and @aria-labelledby="header"'
                         ' and contains(@class, "artdeco-modal")]')
                    ))
                safety_reminder_box.find_element(
                    By.CSS_SELECTOR,
                    'button.artdeco-button.artdeco-button--3.artdeco-button--primary'
                ).click()
            except TimeoutException:
                pass

        return apply_button_clicked

    def get_apply_dialog_box(self):
        try:
            apply_dialog_box = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located(
                    (By.XPATH,
                     '//div[@role="dialog" and @aria-labelledby="jobs-apply-header"'
                     ' and contains(@class, "artdeco-modal")]')
                ))
            return apply_dialog_box
        except TimeoutException:
            return None

    def get_prompt_reference(self, apply_box_dialog) -> bool:
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
                pass

        if info_text in {"Resume", "Education"}:
            return False
        elif info_text == "Work experience":
            work_exp_cancel_xpath = (
                '/html/body/div[3]/div/div/div[2]/div/'
                'div[2]/form/div[1]/div/div[2]/button[1]'
            )
            if not self.single_button_click_xpath(work_exp_cancel_xpath, 1):
                try:
                    apply_box_dialog.find_element(
                        By.XPATH,
                        "//button[contains(@class, 'artdeco-button')"
                        " and contains(., 'Cancel')]"
                    ).click()
                except NoSuchElementException:
                    pass
                return False
        else:
            print(f"\nReference prompt: {info_text}")
            return True

    def get_additional_questions(self) -> list:
        """Extract questions and its type if the form requires additional info"""
        try:
            apply_dialog_box = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located(
                    (By.XPATH,
                     '//div[@role="dialog" and @aria-labelledby="jobs-apply-header"'
                     ' and contains(@class, "artdeco-modal")]')
                ))
            questions_form_div = apply_dialog_box.find_element(
                By.XPATH,
                './/div[contains(@class, "pb4")]'
            )
            questions_html_content = questions_form_div.get_attribute('outerHTML')

            extractor = ExtractQuestionsAndInputs(questions_html_content)
            questions_list = extractor.extract_questions()
            return questions_list

        except NoSuchElementException:
            print("No additional questions dialog-box element found!")
            return []

    def fill_out_answers(self, form_questions) -> None:
        """Passes questions to model to get list of answers and passes to FillAnswers class"""
        nlp_answers = []
        default_answers = ["0", "300000", "0"]
        da_len = len(default_answers)

        for idx, tag in enumerate(form_questions):
            if tag["question"]:
                answer = DEFAULT_ANSWERS.get(
                    tag["question"],
                    self.model.ask_question(tag["question"])
                )
                nlp_answers.append({tag["type"]: answer})
                print(f'{tag["type"]}- {tag["question"]}: {answer}')
            else:
                # This is a hack for work experience form page that asks CTC, ECTC, NOTICE PERIOD.
                # needs to be replaced with actual functioning code to fill then
                nlp_answers.append({tag["type"]: default_answers[idx % da_len]})

        form_filler = FillAnswers(self.driver, form_questions, nlp_answers)
        form_filler.fill_answers()

    def close_submit_dialog_box(self) -> None:
        """Clicks on the close button on box that appears after submitting application"""
        try:
            apply_dialog_box = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located(
                    (By.XPATH,
                     '//div[@role="dialog" and @aria-labelledby="post-apply-modal"'
                     ' and contains(@class, "artdeco-modal")]')
                ))
            WebDriverWait(apply_dialog_box, 5).until(
                ec.element_to_be_clickable(
                    (By.XPATH,
                     '//button[@aria-label="Dismiss" and contains(@class, "artdeco-button")]')
                )).click()
        except (TimeoutException, InvalidSelectorException):
            print("Submit close box not found!")
            pass

    def log_applied_job(self, site):
        now = datetime.now()

        new_job = [
            self.job_info[0],
            self.job_info[1],
            self.job_info[3],
            None,
            self.job_info[2],
            now.strftime("%d-%m-%Y"),
            now.strftime("%H:%M"),
            now.day,
            now.month,
            now.year,
            site
        ]
        with open(JOBS_POSTING_LOG_PATH, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(new_job)

    def save_job_for_later(self) -> None:
        """Saves a Non-Easy-apply job for later"""
        try:
            WebDriverWait(self.driver, 2).until(
                ec.element_to_be_clickable(
                    (By.XPATH,
                     '//button[contains(@class, "jobs-save-button") and contains(., "Save")]')
                )).click()
            print(f"Job application '{self.job_info[0]}' at '{self.job_info[1]}' saved!\n")
        except TimeoutException:
            pass

    def close_apply_dialog(self, apply_box_dialog) -> None:
        """Click on close button of application form and discards it"""
        try:
            apply_box_dialog.find_element(
                By.XPATH,
                '//button[@aria-label="Dismiss" and contains(@class, "artdeco-button")]'
            ).click()

            job_close_save_box = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located(
                    (By.XPATH,
                     '//div[@role="alertdialog" and @aria-describedby="dialog-desc-st7"'
                     ' and contains(@class, "artdeco-modal")]')
                ))
            job_close_save_box.find_element(
                By.XPATH,
                '//button[@data-control-name="discard_application_confirm_btn"'
                ' and contains(@class, "artdeco-button")]'
            ).click()

            print("Application disposed!", end="\n\n")

        except (TimeoutException, InvalidSelectorException):
            print("Close button not found!")
            pass
