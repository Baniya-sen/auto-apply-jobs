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

DEFAULT_LINK = "https://www.naukri.com/mnjuser/recommendedjobs"


class NaukriDotComApply:
    def __init__(self, driver: WebDriver, model: QuestionAnsweringModel, link=None):
        """Naukri.com class to apply to all naukri jobs through Selenium webdriver"""
        self.driver = driver
        self.model = model
        self.job_info = []
        self.all_jobs_count = 1
        self.jobs_traversed = 0
        self.jobs_applied = 0
        self.apply_target = 25
        self.link = DEFAULT_LINK if not link else link

    def apply_recommended(self, depth=0):
        """Performs DFS scraping, starting from the current page."""
        all_articles = WebDriverWait(self.driver, 5).until(
            ec.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.recommended-jobs-page div.list article")
            )
        )
        try:
            # Wait until all articles are present on the current page
            articles = WebDriverWait(self.driver, 5).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.recommended-jobs-page div.list article"))
            )

            # Store the current page URL, in case we need to go back
            current_url = self.driver.current_url

            # Loop through all articles on this page
            for i, article in enumerate(articles):
                # Click on the article to navigate to the next page
                article.click()

                # Wait for the new page to load
                WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, "div.recommended-jobs-page"))
                )

                # Scrape information from the new page, e.g., titles of articles
                new_page_articles = self.get_all_articles_on_page()
                print(f"Depth {depth}: Found {len(new_page_articles)} articles on this new page.")

                # Recursively go deeper (DFS)
                self.dfs_scrape(depth + 1)

                # Return to the previous page
                self.driver.back()

                # Wait for the original page to load again
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.recommended-jobs-page"))
                )

                # Refresh the list of articles after returning to the previous page
                articles = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "div.recommended-jobs-page div.list article"))
                )

        except Exception as e:
            print(f"An error occurred during scraping: {e}")

    def get_all_articles_on_page(self):
        """Scrapes and returns a list of article elements on the current page."""
        try:
            articles = WebDriverWait(self.driver, 5).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.recommended-jobs-page div.list article"))
            )
            return articles
        except Exception as e:
            print(f"Error scraping articles: {e}")
            return []

# Example usage:
driver = webdriver.Chrome(executable_path='path_to_chromedriver')
driver.get("https://example.com")

scraper = ArticleScraper(driver)
scraper.dfs_scrape()  # Start the DFS scraping process

driver.quit()
