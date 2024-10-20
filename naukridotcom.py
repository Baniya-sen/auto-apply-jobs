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
from job_logger import log_applied_job, total_jobs_log
from model import QuestionAnsweringModel
from config import JOB_APPLY_TARGET
from config import DEFAULT_ANSWERS, PROFILE_PATH

DEFAULT_LINK = "https://www.naukri.com/mnjuser/recommendedjobs"


class NaukriDotComApply:
    def __init__(self, driver: WebDriver, link=None):
        """Naukri.com class to apply to all naukri jobs through Selenium webdriver"""
        self.driver = driver
        self.job_info = {}
        self.all_jobs_count = 0
        self.jobs_traversed = 0
        self.jobs_applied = 0
        self.apply_target = int(sqrt(min(JOB_APPLY_TARGET, 225)))
        self.link = DEFAULT_LINK if not link else link
        self.driver.get(self.link)
        if self.driver.current_url != self.link:
            self.is_user_logged_in()

    def is_user_logged_in(self):
        logged_in = True
        opened_link = self.driver.current_url

        if "login" in opened_link:
            logged_in = False
        else:
            try:
                WebDriverWait(self.driver, 1).until(
                    ec.presence_of_element_located(
                        (By.XPATH, "//a[contains(., 'Login')]")
                    ))
                logged_in = False
            except TimeoutException:
                pass

        while not logged_in:
            page_state = self.driver.execute_script('return document.readyState;')
            if page_state == 'complete':
                if self.link in self.driver.current_url:
                    print("SUCCESS: You are now logged-in.")
                    self.driver.get(self.link)
                    break

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
            self.all_jobs_count = self.dfs_job_traversal(articles, original_tab) + len(articles)
            print("Total jobs traversed are", self.all_jobs_count)

            total_jobs_log(
                self.all_jobs_count,
                self.all_jobs_count,
                self.jobs_applied,
                self.jobs_traversed - self.jobs_applied,
                "NaukriDotCom"
            )

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
            WebDriverWait(self.driver, 2).until(
                ec.element_to_be_clickable(
                    (By.XPATH,
                     '//button[contains(@id, "apply-button") and contains(text(), "Apply")]')
                )).click()
            try:
                WebDriverWait(self.driver, 2).until(
                    ec.staleness_of(reference_element)
                )
                print(f"Successfully applied for the {self.job_info[0]} at {self.job_info[1]}.")
                log_applied_job(self.job_info, "Naukridotcom")
                self.jobs_applied += 1
            except (TimeoutException, NoSuchElementException):
                self.jobs_traversed += 1
                print("ERROR: This job requires additional answers!.")

        except TimeoutException:
            pass

    def get_job_info(self):
        job_position_cname_exp_salary_css_paths = {
            "job_position": "div#root section#job_header h1",
            "company_name": "div#root section#job_header a",
            "experience_level": "div#root section#job_header div.styles_jhc__exp__k_giM",
            "salary": "div#root section#job_header div.styles_jhc__salary__jdfEC",
            "job_location": "div#root section#job_header span.styles_jhc__location__W_pVs a",
        }
        for info_name, path in job_position_cname_exp_salary_css_paths.items():
            if info_name == "job_location":
                break
            try:
                info = WebDriverWait(self.driver, 1).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, path))
                    ).text
            except TimeoutException:
                info = None
            self.job_info[info_name] = info

        try:
            job_location_elements = WebDriverWait(self.driver, 1).until(
                ec.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, job_position_cname_exp_salary_css_paths["job_location"]))
            )
            job_location = [location_element.text for location_element in job_location_elements]
        except TimeoutException:
            job_location = []
        self.job_info["job_location"] = ", ".join(job_location) if job_location else None


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")
    web_driver = webdriver.Chrome(options=chrome_options)
    web_driver.maximize_window()

    n = NaukriDotComApply(web_driver, 14)
    n.apply_recommended_jobs()
