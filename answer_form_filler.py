from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, InvalidSelectorException


class FillAnswers:
    def __init__(self, driver, nlp_output, questions):
        self.driver = driver
        self.nlp_output = nlp_output
        self.questions = questions

    def fill_answers(self):
        for answer, question in zip(self.nlp_output, self.questions):
            input_type = question['type']
            question_text = question['question']
            q_text_len = int(len(question_text) * 0.60)

            try:
                if input_type == 'text':
                    input_element = self.driver.find_element(
                        By.XPATH, f"//label[contains(normalize-space(text()), '"
                        f"{question_text.strip()}')]/following-sibling::input")
                    input_element.send_keys(answer['text'])

                elif input_type == 'radio':
                    radio_xpath = (f"//legend[starts-with(normalize-space(), '"
                                   f"{question_text[:q_text_len]}')]/following::label"
                                   f"[text()='{answer['radio']}']")
                    radio_element = self.driver.find_element(By.XPATH, radio_xpath)
                    radio_element.click()

                elif input_type == 'select':
                    select_xpath = (f"//legend[starts-with(normalize-space(), '"
                                    f"{question_text[:q_text_len]}')]/following-"
                                    f"sibling::select")
                    select_element = self.driver.find_element(By.XPATH, select_xpath)
                    select_element.select_by_visible_text(answer['select'])

            except (NoSuchElementException, TimeoutException, InvalidSelectorException) as e:
                print(f"Failed to fill {input_type} for question '{question_text}': {str(e)}")
