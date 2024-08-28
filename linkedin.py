import time

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException, InvalidSelectorException

from extractor import ExtractQuestionsAndInputs
from model import QuestionAnsweringModel
from filler import FillAnswers

DEFAULT_LINK = "https://www.linkedin.com/jobs/collections/recommended/"


class LinkedInApply:
    def __init__(self, driver: WebDriver, model: QuestionAnsweringModel, link=None):
        """LinkedIn class to apply to all LinkedIn easy-apply jobs through Selenium webdriver"""
        self.driver = driver
        self.model = model
        self.job_info = []
        self.link = DEFAULT_LINK if not link else link
        self.driver.get(self.link)

    def apply_to_jobs(self) -> None:
        """Function to call to start applying for jobs"""
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

            self.easy_apply(job.text)

    def get_all_job_postings(self):
        """Extract all jobs posting from UL element"""
        ul_element = WebDriverWait(self.driver, 5).until(
            ec.presence_of_element_located(
                (By.XPATH, '//*[@id="main"]/div/div[2]/div[1]/div/ul')
            )
        )
        return ul_element.find_elements(By.XPATH, "./li")

    def get_job_info(self, job_element) -> None:
        """Saves Job position, Organisation name, and Jobs location in a list"""
        self.job_info = []

        job_info_paths = [
            ".//a[contains(@class, 'job-card-list__title')]//span/strong",
            ".//span[@class='job-card-container__primary-description ']",
            ".//li[@class='job-card-container__metadata-item ']"
        ]
        for xpath in job_info_paths:
            self.job_info.append(
                job_element.find_element(By.XPATH, xpath).text
            )

    def easy_apply(self, job_description="Easy Apply") -> None:
        """Easy-Apply to a given job after filling form and additional questions if available"""
        if "Easy Apply" in job_description:
            self.apply_button_click()

            if self.next_button_click() == "Submit application":
                self.single_button_click_xpath('/html/body/div[3]/div/div/button', 2)
                print(f"Successfully applied for: {self.job_info[0]}, at {self.job_info[1]}!\n")
            else:
                answer_filling_try_count = 0

                while True:
                    if self.get_prompt_reference():
                        questions = self.get_additional_questions()
                        self.fill_out_answers(questions)
                        answer_filling_try_count += 1  # Need to change this location

                    self.single_button_click_xpath(
                        '/html/body/div[3]/div/div/div[2]/div/'
                        'div[2]/form/footer/div[2]/button[2]'
                    )

                    if self.submit_additional_apply():
                        self.close_submit_dialog_box()
                        break

                    if answer_filling_try_count > 2:
                        self.close_apply_dialog()
                        break
        else:
            self.save_job_for_later()

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

    def apply_button_click(self) -> None:
        """Clicks on apply button and checks for suspicious activity dialog-box"""
        try:
            job_description_tab = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located(
                    (By.CLASS_NAME, 'scaffold-layout__detail')
                ))
        except TimeoutException:
            job_description_tab = self.driver

        WebDriverWait(job_description_tab, 5).until(
            ec.element_to_be_clickable(
                (By.CLASS_NAME, 'jobs-apply-button--top-card')
            )).click()

        try:
            WebDriverWait(self.driver, 1).until(ec.presence_of_element_located(
                (By.XPATH,
                 '/html/body/div[3]/div/div/div[1]/h2'
                 '[@id="header" and text()="Job search safety reminder"]')
            ))
            self.single_button_click_xpath(
                '/html/body/div[3]/div/div/div[3]/div/div/button',
                1)
        except TimeoutException:
            print(f"LinkedIn suspicious activity dialog-box not found!")

    def next_button_click(self) -> str:
        """Clicks on next button available on form dialog-box"""
        WebDriverWait(self.driver, 5).until(ec.presence_of_element_located(
            (By.XPATH,
             '/html/body/div[3]/div/div/div[1]/h2[@id="jobs-apply-header"]')
        ))

        next_button_object = None
        is_apply_button_visible = False

        next_button_paths = [
            '/html/body/div[3]/div/div/div[2]/div/div[2]/form/footer/div[2]/button',
            '/html/body/div[3]/div/div/div[2]/div/div/form/footer/div[2]/button',
            '/html/body/div[3]/div/div/div[2]/div/div/form/footer/div[3]/button',
            '/html/body/div[3]/div/div/div[2]/div/div/form/footer/div[3]/button/span'
        ]

        for xpath in next_button_paths:
            try:
                next_button_object = WebDriverWait(self.driver, 1).until(
                    ec.element_to_be_clickable((By.XPATH, xpath))
                )
                is_apply_button_visible = True
                break
            except TimeoutException:
                continue

        if is_apply_button_visible:
            next_button_object_text = next_button_object.text
            next_button_object.click()
            return next_button_object_text
        else:
            print(f'Next button element not found!')
            raise TimeoutException

    def get_prompt_reference(self) -> bool:
        """Extracts text from form headline to identify if the form requires
           additional questions to fill, or it is basic requirements"""
        info_text = ""
        info_text_xpath = [
            '/html/body/div[3]/div/div/div[2]/div/div[2]/form/div/div/h3',
            '/html/body/div[3]/div/div/div[2]/div/div[2]/form/div[1]/h3/span'
        ]

        for xpath in info_text_xpath:
            try:
                info_text = WebDriverWait(self.driver, 1).until(
                    ec.presence_of_element_located((By.XPATH, xpath))
                ).text
            except TimeoutException:
                print("No prompt found!")
                continue

        print(info_text)

        if info_text in {"Contact info", "Resume", "Education"}:
            return False
        elif info_text == "Work experience":
            work_exp_cancel_xpath = (
                '/html/body/div[3]/div/div/div[2]/div/'
                'div[2]/form/div[1]/div/div[2]/button[1]'
            )
            return not self.single_button_click_xpath(work_exp_cancel_xpath, 1)
        else:
            print(f"\nReference prompt: {info_text}")
            return True

    def get_additional_questions(self) -> list:
        """Extract questions and its type if the form requires additional info"""
        try:
            questions_form_div = self.driver.find_element(
                By.XPATH,
                '/html/body/div[3]/div/div/div[2]/div/div[2]/form/div/div[@class="pb4"]'
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
        default_answers = ["0", "350000", "0"]
        da_len = len(default_answers)

        for idx, tag in enumerate(form_questions):
            if tag["question"]:
                answer = self.model.ask_question(tag["question"])
                nlp_answers.append({tag["type"]: answer})
                print(f'{tag["question"]}: {tag["type"]}: {answer}')
            else:
                # This is a hack for work experience form page that asks CTC, ECTC, NOTICE PERIOD.
                # needs to be replaced with actual functioning code to fill then
                nlp_answers.append({tag["type"]: default_answers[idx % da_len]})

        time.sleep(10)

        form_filler = FillAnswers(self.driver, form_questions, nlp_answers)
        form_filler.fill_answers()

    def submit_additional_apply(self) -> bool:
        """Continuously checks for Submit-Application button to appear and click it"""
        submit_button_object = False
        submit_button_paths = [
            '/html/body/div[3]/div/div/div[2]/div/div[2]/div/footer/div[3]/'
            'button[2][@aria-label="Submit application"]',
            '/html/body/div[3]/div/div/div[2]/div/div[2]/div/footer/div[2]/'
            'button[2][@aria-label="Submit application"]',
            '/html/body/div[3]/div/div/div[3]/button/span[text()="Done"]'
        ]

        for xpath in submit_button_paths:
            try:
                submit_button = WebDriverWait(self.driver, 1).until(
                    ec.element_to_be_clickable((By.XPATH, xpath))
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);",
                    submit_button
                )
                submit_button.click()
                submit_button_object = True
            except (TimeoutException, InvalidSelectorException):
                continue

        if submit_button_object:
            print("Application submitted successfully after filling form.", end="\n\n")
            return True

    def close_submit_dialog_box(self) -> None:
        """Clicks on the close button on box that appears after submitting application"""
        close_submit_button_paths = [
            '/html/body/div[3]/div/div/div[3]/button',
            '/html/body/div[3]/div/div/button',
            '/html/body/div[3]/div/div/button/svg',
        ]
        for xpath in close_submit_button_paths:
            try:
                close_button = WebDriverWait(self.driver, 1).until(
                    ec.element_to_be_clickable((By.XPATH, xpath))
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView(true);",
                    close_button
                )
                close_button.click()
            except (TimeoutException, InvalidSelectorException):
                continue

    def save_job_for_later(self) -> None:
        """Saves a Non-Easy-apply job for later"""
        saved_later_xpath = [
            '/html/body/div[5]/div[3]/div[4]/div/div/main/div/div[2]/div[2]/div/'
            'div[2]/div/div[1]/div/div[1]/div/div[1]/div[1]/div[6]/div/button',
            '//button[contains(@class, "jobs-save-button") and span[text()="Save"]]'
        ]
        for xpath in saved_later_xpath:
            try:
                self.single_button_click_xpath(xpath, 1)
                print(f"Job application '{self.job_info[0]}' at '{self.job_info[1]}' saved!\n")
            except TimeoutException:
                continue

    def close_apply_dialog(self) -> None:
        """Click on close button of application form and discards it"""
        close_button_paths = [
            '/html/body/div[3]/div/div/button',
            '/html/body/div[3]/div[2]/div/div[3]/button[1]'
        ]

        for xpath in close_button_paths:
            self.single_button_click_xpath(xpath, 1)

        print("Application disposed!", end="\n\n")
