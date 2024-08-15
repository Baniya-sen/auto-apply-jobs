from selenium.webdriver.common.by import By


class FillAnswers:
    def __init__(self, driver, nlp_output, questions):
        self.driver = driver
        self.nlp_output = nlp_output
        self.questions = questions

    def fill_answers(self):
        for answer, question in zip(self.nlp_output, self.questions):
            input_type = question['type']
            if input_type == 'text':
                input_element = self.driver.find_element(By.XPATH, f"//label[text()='{question['question']}']/following-sibling::input")
                input_element.send_keys(answer['text'])
            elif input_type == 'radio':
                radio_element = self.driver.find_element(By.XPATH, f"//label[text()='{answer['radio']}']/preceding-sibling::input")
                radio_element.click()
            elif input_type == 'select':
                select_element = self.driver.find_element(By.XPATH, f"//label[text()='{question['question']}']/following-sibling::select")
                select_element.select_by_visible_text(answer['select'])
