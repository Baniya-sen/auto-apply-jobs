import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
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


def apply_recommended(self, depth=0):
    """Performs DFS scraping, starting from the current page."""
    articles = WebDriverWait(self.driver, 5).until(
        ec.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.recommended-jobs-page div.list article")
        )
    )[0:10]
    original_tab = self.driver.current_window_handle

    total_job_processed = self.dfs_job_traversal(articles, original_tab)
    print("Total jobs traversed are", total_job_processed + len(articles))


def dfs_job_traversal(self, original_articles, original_tab):
    all_jobs = 0

    for i, article in enumerate(original_articles):
        try:
            article.click()
            WebDriverWait(self.driver, 5).until(ec.number_of_windows_to_be(2))

            new_tab = [
                handle for handle in self.driver.window_handles if handle != original_tab
            ][0]
            self.driver.switch_to.window(new_tab)

            WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "div#root"))
            )

            new_page_articles = self.get_all_articles_on_page()
            all_jobs += len(new_page_articles)

            for j, sub_article in enumerate(new_page_articles):
                sub_article.click()
                WebDriverWait(self.driver, 5).until(ec.number_of_windows_to_be(3))
                new_sub_tab = [
                    handle for handle in self.driver.window_handles
                    if handle != original_tab and handle != new_tab
                ][0]
                self.driver.switch_to.window(new_sub_tab)
                sub_page_articles = self.get_all_articles_on_page()
                all_jobs += len(sub_page_articles)

                for sub_job in sub_page_articles:
                    sub_job.click()
                    WebDriverWait(self.driver, 5).until(ec.number_of_windows_to_be(4))
                    job_tab = self.driver.window_handles[-1]
                    self.driver.switch_to.window(job_tab)

                    self.apply_to_job(sub_job)
                    self.driver.close()
                    self.driver.switch_to.window(new_sub_tab)

                self.driver.close()
                self.driver.switch_to.window(new_tab)

            self.driver.close()
            self.driver.switch_to.window(original_tab)

            WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "div.recommended-jobs-page"))
            )

        except (TimeoutException, ElementClickInterceptedException, InvalidSelectorException) as e:
            print(f"An error at tab {i}: ", e)
            pass

    return all_jobs


def get_all_articles_on_page(self):
    """Scrapes and returns a list of article elements on the current page."""
    try:
        articles = WebDriverWait(self.driver, 5).until(
            ec.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "article")
            )
        )
        return articles
    except Exception as e:
        print(f"Error scraping articles: {e}")
        return []


def apply_to_job(self, job):
    current_url = self.driver.current_url
    apply_button_selected = False

    reference_element = WebDriverWait(self.driver, 1).until(
        ec.presence_of_element_located((By.TAG_NAME, "html"))
    )

    try:
        apply_button = WebDriverWait(self.driver, 5).until(
            ec.element_to_be_clickable(
                (By.XPATH,
                 '//button[contains(@id, "apply-button") and contains(text(), "Apply")]')
            ))
        apply_button.click()
        apply_button_selected = True

    except TimeoutException:
        pass

    if apply_button_selected:
        try:
            WebDriverWait(self.driver, 2).until(
                ec.staleness_of(reference_element)
            )
            print("The page has reloaded.")
        except Exception as e:
            print("The page did not reload.", e)
