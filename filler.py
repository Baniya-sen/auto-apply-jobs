from random import choice

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import InvalidSelectorException


class FillAnswers:
    def __init__(self, driver: WebDriver, questions: list, answers: list):
        """Class to fill tailored answers to given questions through Selenium"""
        self.driver = driver
        self.questions = questions
        self.answers = answers

    def fill_answers(self) -> None:
        """Fill answers to given questions after filtering input type"""
        for answer, question in zip(self.answers, self.questions):
            input_type = question['type']
            question_text = question['question']
            ques_text_match_len = min(int(len(question_text) * 0.60), 50)

            try:
                if input_type == 'text':
                    input_element = self.driver.find_element(
                        By.XPATH, f"//label[contains(normalize-space(text()), '"
                                  f"{question_text.strip()}')]/following-sibling::input")
                    input_element.clear()
                    input_element.send_keys(answer['text'])

                if input_type == 'radio':
                    right_option = answer['radio']
                    if right_option not in question['options']:
                        right_option = choice(question['options'])

                    radio_xpath = (f"//legend[starts-with(normalize-space(), '"
                                   f"{question_text[:ques_text_match_len]}')]/following::"
                                   f"label[text()='{right_option}']")
                    radio_element = self.driver.find_element(By.XPATH, radio_xpath)
                    radio_element.click()

                elif input_type == 'select':
                    right_option = answer['select']
                    if right_option not in question['options']:
                        right_option = choice(question['options'])

                    select_xpath = (f"//label[starts-with(normalize-space(), '"
                                    f"{question_text[:ques_text_match_len]}')]"
                                    f"/following-sibling::select")
                    select_element = self.driver.find_element(By.XPATH, select_xpath)
                    select_object = Select(select_element)
                    select_object.select_by_visible_text(right_option)

                elif input_type == 'checkbox':
                    checkbox_xpath = (f"//legend[starts-with(normalize-space(), '"
                                      f"{question_text[:20]}')]/following::"
                                      f"label")
                    checkbox_element = self.driver.find_element(By.XPATH, checkbox_xpath)
                    checkbox_element.click()

                else:
                    input_element = self.driver.find_element(
                        By.XPATH,
                        f"//label[span[contains(normalize-space(text()), "
                        f"'{question_text.strip()}')]]/following-sibling::div/input"
                    )
                    input_element.clear()
                    input_element.send_keys(answer['text'])

            except (TimeoutException, NoSuchElementException, InvalidSelectorException) as e:
                print(f"Failed to fill {input_type} for question '{question_text}'")
                print(e)
