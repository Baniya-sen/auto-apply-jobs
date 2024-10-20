import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


def clean_text(text):
    """Remove trailing 'required' or similar words and duplicate parts in the question"""
    if text:
        text = re.sub(r'\s*required\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'(\b[\w\s]+\b)\s*\1+', r'\1', text)
        text = re.sub(r'\b(\w+)\b\s*\?\s*.*\?\s*$', r'\1?', text)
        text = re.sub(r'(?<!\S)(.+?)(?:(?!\S)\s*|\s*)(\1)(?!\S)', r'\1', text)
        text = ' '.join(text.split())
        return text.strip()
    return " "


class ExtractQuestionsAndInputs:
    def __init__(self, driver, model):
        """Extract questions, input types, and options using Selenium WebDriver"""
        self.driver = driver
        self.model = model
        self.questions = []
        self.options = []

    def parse_and_extract(self):
        """Find and extract job-related form elements using Selenium"""
        sections = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, 'jobs-easy-apply-form-section__grouping')
            ))

        for section in sections:
            question, input_type, options, element = self.extract_question_and_input(section)
            self.questions.append({
                'question': question,
                'input_type': input_type,
                'options': options,
                'element': element
            })

    def extract_question_and_input(self, section):
        """Extract the question, input type, options, and associated element"""
        question_text = ""
        options = []

        if fieldsets := section.find_elements(By.XPATH, './/fieldset[@data-test-form-builder-radio-button-form-component]'):
            question_text = section.find_element(By.TAG_NAME, 'legend').text.strip()
            options = [opt.text.strip() for opt in fieldsets[0].find_elements(By.TAG_NAME, 'label')]
            return clean_text(question_text), 'radio', options, fieldsets[0]

        elif selects := section.find_elements(By.XPATH, './/select[@data-test-text-entity-list-form-select]'):
            question_text = section.find_element(By.TAG_NAME, 'label').text.strip()
            options = [opt.text.strip() for opt in selects[0].find_elements(By.TAG_NAME, 'option') if opt.get_attribute('value')]
            return clean_text(question_text), 'select', options, selects[0]

        elif checkboxes := section.find_elements(By.XPATH, './/input[@data-test-form-builder-checkbox-form-component]'):
            question_text = section.find_element(By.TAG_NAME, 'legend').text.strip()
            options = [opt.text.strip() for opt in section.find_elements(By.TAG_NAME, 'label')]
            return clean_text(question_text), 'checkbox', options, checkboxes[0]

        elif inputs := section.find_elements(By.XPATH, './/input[@type="text"]'):
            input_element = inputs[0]
            try:
                question_text = section.find_element(By.TAG_NAME, 'label').text.strip()
            except NoSuchElementException:
                question_text = ""
            return clean_text(question_text), 'input', options, input_element

        return clean_text(question_text), 'input', options, None

    def format_output(self):
        """Formats the extracted questions into a list of dictionaries"""
        return [
            {
                'idx': idx,
                'question': clean_text(question['question']),
                'type': question['input_type'],
                'options': question['options'],
                'element': question['element']
            }
            for idx, question in enumerate(self.questions, 1)
        ]

    def extract_questions(self):
        """Start the extraction process and return formatted output"""
        self.parse_and_extract()
        return self.format_output()
