import csv
from math import sqrt
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException, InvalidSelectorException

from extractor import ExtractQuestionsAndInputs
from model import QuestionAnsweringModel
from filler import FillAnswers
from config import DEFAULT_ANSWERS
from config import JOBS_POSTING_LOG_PATH, JOB_LOG_HEADERS

from config import PROFILE_PATH

DEFAULT_LINK = "https://www.naukri.com/mnjuser/recommendedjobs"


class NaukriDotComApply:
    def __init__(self, driver: WebDriver, no_of_jobs=50, link=None):
        """Naukri.com class to apply to all naukri jobs through Selenium webdriver"""
        self.driver = driver
        self.job_info = []
        self.all_jobs_count = 1
        self.jobs_traversed = 0
        self.jobs_applied = 0
        self.apply_target = int(sqrt(min(no_of_jobs, 225)))
        self.link = DEFAULT_LINK if not link else link
        self.driver.get(self.link)

    def apply_recommended_jobs(self):
        """Extracts limited job postings from the recommended job page."""
        jobs_css_pass = ("div.recommended-jobs-page div.list article"
                         if self.link == DEFAULT_LINK else "article")
        try:
            articles = WebDriverWait(self.driver, 5).until(
                ec.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, jobs_css_pass)
                )
            )[0:self.apply_target]

            original_tab = self.driver.current_window_handle
            total_job_processed = self.dfs_job_traversal(articles, original_tab)
            print("Total jobs traversed are", total_job_processed + len(articles))

        except TimeoutException:
            print("ERROR: No job elements found!")

    def dfs_job_traversal(self, articles, parent_tab, depth=1):
        """Recursively traverses job postings(DFS), applying jobs, limited depth."""
        if depth > self.apply_target:
            return 0

        total_jobs = 0

        for i, article in enumerate(articles):
            try:
                original_tabs = self.driver.window_handles
                article.click()
                WebDriverWait(self.driver, 5).until(
                    ec.number_of_windows_to_be(len(original_tabs) + 1))

                new_tab = [
                    tab for tab in self.driver.window_handles
                    if tab not in original_tabs
                ][0]
                self.driver.switch_to.window(new_tab)

                WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, "div#root"))
                )
                new_page_articles = self.get_all_articles_on_page()
                total_jobs += len(new_page_articles)

                if new_page_articles and depth < self.apply_target:
                    total_jobs += self.dfs_job_traversal(
                        new_page_articles, new_tab, depth + 1
                    )
                self.apply_to_job()

            except (TimeoutException, ElementClickInterceptedException) as e:
                print(f"Error processing article {i} at depth {depth}: {e}")

            self.driver.close()
            self.driver.switch_to.window(parent_tab)

        return total_jobs

    def get_all_articles_on_page(self):
        """Scrapes and returns limited list of article elements on the current page."""
        try:
            articles = WebDriverWait(self.driver, 5).until(
                ec.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "article")
                )
            )
            return articles[0:self.apply_target]
        except TimeoutException:
            print("ERROR: No job articles found!")
            return []

    def apply_to_job(self):
        """Apply to the current job posting and its verification"""
        self.get_job_info()

        try:
            reference_element = WebDriverWait(self.driver, 2).until(
                ec.presence_of_element_located((By.TAG_NAME, "html"))
            )
            WebDriverWait(self.driver, 1).until(
                ec.element_to_be_clickable(
                    (By.XPATH,
                     '//button[contains(@id, "apply-button") and contains(text(), "Apply")]')
                )).click()
            try:
                WebDriverWait(self.driver, 2).until(
                    ec.staleness_of(reference_element)
                )
                print(f"Successfully applied for the {self.job_info[0]} at {self.job_info[1]}.")
                self.log_applied_job("Naukridotcom")
            except (TimeoutException, NoSuchElementException):
                print("ERROR: This job requires additional answers!.")

        except TimeoutException:
            pass

    def get_job_info(self):
        self.job_info = []

        job_position_cname_exp_salary_css_paths = [
            "div#root section#job_header h1",
            "div#root section#job_header a",
            "div#root section#job_header div.styles_jhc__exp__k_giM",
            "div#root section#job_header div.styles_jhc__salary__jdfEC"
        ]
        for path in job_position_cname_exp_salary_css_paths:
            try:
                info = WebDriverWait(self.driver, 1).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, path))
                    ).text
            except TimeoutException:
                info = None
            self.job_info.append(info)

        try:
            job_location_css_path = "div#root section#job_header span.styles_jhc__location__W_pVs a"
            job_location_elements = WebDriverWait(self.driver, 1).until(
                ec.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, job_location_css_path))
            )
            job_location = [job_location_element.text for job_location_element in job_location_elements]
        except TimeoutException:
            job_location = []
        self.job_info.append(", ".join(job_location) if job_location else None)
        print(self.job_info)

    def log_applied_job(self, site):
        now = datetime.now()
        new_job = [
            self.job_info[0],
            self.job_info[1],
            self.job_info[2],
            self.job_info[3],
            self.job_info[4],
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


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")
    web_driver = webdriver.Chrome(options=chrome_options)
    web_driver.maximize_window()

    n = NaukriDotComApply(web_driver, 14)
    n.apply_recommended_jobs()
