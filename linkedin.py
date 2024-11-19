import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException, InvalidSelectorException

from model import QuestionAnsweringModel
from extract_and_fill import LinkedInExtractAndFill
from job_logger import log_applied_job, total_jobs_log
from config import JOB_APPLY_TARGET

DEFAULT_LINK = "https://www.linkedin.com/jobs/collections/recommended/"


class LinkedInApply:
    def __init__(self, driver: WebDriver, model: QuestionAnsweringModel, link=None) -> None:
        """LinkedIn class to apply to all LinkedIn easy-apply jobs through Selenium webdriver"""
        self.driver = driver
        self.model = model
        self.job_info = dict()
        self.all_jobs_count = 1
        self.jobs_traversed = 0
        self.jobs_applied = 0
        self.apply_dialog_box = None
        self.link = DEFAULT_LINK if not link else link

        self.driver.get(self.link)
        if self.driver.current_url != self.link:
            self._is_user_logged_in()

    def _is_user_logged_in(self) -> None:
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

        if not logged_in:
            print("ERROR: You are not logged-in!")

        while not logged_in:
            page_state = self.driver.execute_script('return document.readyState;')
            if page_state == 'complete':
                if (self.link in self.driver.current_url
                        or "https://www.linkedin.com/feed" in self.driver.current_url):
                    print("SUCCESS: You are now logged-in.")
                    self.driver.get(self.link)
                    break

    def easy_apply_to_jobs(self) -> None:
        """Continue applying for jobs till target is hit."""
        try:
            while JOB_APPLY_TARGET >= self.jobs_applied:
                for job in self._get_all_job_postings():
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", job)
                    WebDriverWait(self.driver, 2).until(ec.visibility_of(job))

                    try:
                        job.click()
                        if self.easy_apply_single_job(job.text):
                            self.jobs_traversed += 1
                    except (ElementClickInterceptedException, StaleElementReferenceException):
                        print("ERROR: Failed to click due to an overlay OR Element is stale. Reloading.\n")
                        break

                self.driver.get(self.link)

        except Exception as e:
            print(e)

        total_jobs_log(
            self.all_jobs_count,
            self.jobs_traversed,
            self.jobs_applied,
            self.jobs_traversed - self.jobs_applied,
            "LinkedIn"
        )

    def _get_all_job_postings(self):
        """Extract all jobs posting from UL element"""
        ul_element = WebDriverWait(self.driver, 5).until(
            ec.presence_of_element_located(
                (By.XPATH, '//*[@id="main"]/div/div[2]/div[1]/div/ul')
            )
        )
        all_li_elements = ul_element.find_elements(By.XPATH, "./li")
        self.all_jobs_count += len(all_li_elements)
        return all_li_elements

    def _get_job_info(self) -> None:
        """Saves Job position, Organisation name, and Jobs location in a list"""
        job_info_css_paths = {
            "job_position": "div.job-details-jobs-unified-top-card__job-title",
            "company_name": "div.job-details-jobs-unified-top-card__company-name",
            "experience_level": "span.job-details-jobs-unified-top-card__job-insight-view-model-secondary[dir='ltr']",
            "salary": "li.job-details-jobs-unified-top-card__job-insight:first-of-type span[dir='ltr']:not([class])",
            "job_location": "div.job-details-jobs-unified-top-card__primary-description-container span",
        }
        for info_tag, path in job_info_css_paths.items():
            try:
                info = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, path))
                )
                info = info.text.split(",")[0] if info_tag == "job_location" else info.text
                self.job_info[info_tag] = info
            except TimeoutException:
                self.job_info[info_tag] = None

    def easy_apply_single_job(self, job_description="Easy Apply") -> bool:
        """Easy apply for job by filling out form and answering any additional questions."""
        self._get_job_info()

        if "Easy Apply" not in job_description or not self._apply_button_click():
            self._save_job_for_later()
            return True

        self._get_apply_dialog_box()
        if not self.apply_dialog_box:
            return False

        attempted, attempts = 0, 8
        while attempted < attempts:
            try:
                continue_button = WebDriverWait(self.apply_dialog_box, 5).until(
                    ec.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'button.artdeco-button.artdeco-button--2.artdeco-button--primary')
                    ))
                if continue_button.text == "Submit application":
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", continue_button)
                    continue_button.click()
                    print(f'SUCCESS: Successfully applied for: {self.job_info["job_position"]},'
                          f' at {self.job_info["company_name"]}!')
                    self.jobs_applied += 1
                    log_applied_job(self.job_info, "LinkedIn")
                    self._close_submitted_dialog_box()
                    return True

                if self._get_prompt_reference():
                    self._get_additional_questions_and_answer()
                    attempted += 1
                    if attempted >= 7:
                        raise TimeoutException

                self.driver.execute_script("arguments[0].scrollIntoView(true);", continue_button)
                continue_button.click()

            except (TimeoutException, ElementClickInterceptedException):
                print(f"ERROR: Application '{self.job_info['job_position']}' could not be pass! Disposing.")
                self._close_apply_dialog_box()
                return False

    def _apply_button_click(self) -> bool:
        """Clicks on apply button and checks for suspicious activity dialog-box"""
        apply_button_clicked = False
        apply_button_paths = {
            By.XPATH: "//button[contains(@class, 'jobs-apply-button') and contains(., 'Easy Apply')]",
            By.CSS_SELECTOR: "button#ember45.jobs-apply-button.artdeco-button.artdeco-button--3"
        }
        for selector_method, path in apply_button_paths.items():
            try:
                WebDriverWait(self.driver, 5).until(
                    ec.element_to_be_clickable((selector_method, path))
                ).click()
                apply_button_clicked = True
                break
            except TimeoutException:
                print("ERROR: Easy Apply button not found! Checking another path!")

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

    def _save_job_for_later(self) -> None:
        """Saves a Non-Easy-apply job for later"""
        try:
            WebDriverWait(self.driver, 2).until(
                ec.element_to_be_clickable(
                    (By.XPATH,
                     '//button[contains(@class, "jobs-save-button") and contains(., "Save")]')
                )).click()
            print(f'SUCCESS: Job application "{self.job_info["job_position"]}" saved!')
        except TimeoutException:
            pass

    def _get_apply_dialog_box(self):
        try:
            self.apply_dialog_box = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located(
                    (By.XPATH,
                     '//div[@role="dialog" and @aria-labelledby="jobs-apply-header"'
                     ' and contains(@class, "artdeco-modal")]')
                ))
        except TimeoutException:
            print("ERROR: Apply dialog box not found after clicking apply button! Skipping.")
            self.apply_dialog_box = None

    def _close_submitted_dialog_box(self) -> None:
        """Clicks on the close button on box that appears after submitting application"""
        try:
            post_apply_dialog_box = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located(
                    (By.XPATH,
                     '//div[@role="dialog" and @aria-labelledby="post-apply-modal"'
                     ' and contains(@class, "artdeco-modal")]')
                ))
            time.sleep(1)
            WebDriverWait(post_apply_dialog_box, 10).until(
                ec.element_to_be_clickable(
                    (By.XPATH,
                     '//button[@aria-label="Dismiss" and contains(@class, "artdeco-button")]')
                )).click()  # THIS IS ElementClickInterceptedException PROBLEM
        except (TimeoutException, InvalidSelectorException,
                ElementClickInterceptedException, StaleElementReferenceException):
            pass

    def _get_prompt_reference(self) -> bool:
        """Extracts text from form headline to identify if the form requires
           additional questions to fill, or it is basic requirements"""
        info_text = ""
        prompts_paths = ['h3.t-16.t-bold', 'h3.t-16.mb2']

        for xpath in prompts_paths:
            try:
                info_text = WebDriverWait(self.apply_dialog_box, 2).until(
                    ec.presence_of_element_located(
                        (By.CSS_SELECTOR, xpath)
                    )).text
                break
            except TimeoutException:
                pass

        if info_text == "Resume":
            try:
                self.apply_dialog_box.find_element(By.XPATH, './/input[@class="artdeco-text-input--input"]')
                return True
            except NoSuchElementException:
                pass
            return False
        elif info_text == "Education":
            return False
        elif info_text == "Work experience":
            try:
                self.apply_dialog_box.find_element(
                    By.XPATH,
                    "//button[contains(@class, 'artdeco-button') and contains(., 'Cancel')]"
                ).click()
                return False
            except NoSuchElementException:
                return True
        else:
            return True

    def _get_additional_questions_and_answer(self) -> None:
        """Extract questions and its type if the form requires additional info"""
        extractor = LinkedInExtractAndFill(self.driver, self.model)
        extractor.parse_questions_and_answers()

    def _close_apply_dialog_box(self) -> None:
        """Click on close button of application form and discards it"""
        try:
            WebDriverWait(self.apply_dialog_box, 10).until(
                ec.element_to_be_clickable(
                    (By.XPATH,
                     '//button[@aria-label="Dismiss" and contains(@class, "artdeco-button")]')
                )).click()
            job_close_save_box = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located(
                    (By.XPATH,
                     '//div[@role="alertdialog" and @aria-describedby="dialog-desc-st7"'
                     ' and contains(@class, "artdeco-modal")]')
                ))
            WebDriverWait(job_close_save_box, 10).until(
                ec.element_to_be_clickable(
                    (By.XPATH,
                     '//button[@data-control-name="discard_application_confirm_btn"'
                     ' and contains(@class, "artdeco-button")]')
                )).click()

        except (TimeoutException, InvalidSelectorException,
                ElementClickInterceptedException, StaleElementReferenceException):
            pass
