import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from config import DEFAULT_ANSWERS
from model import QuestionAnsweringModel


def clean_text(text) -> str:
    """Remove trailing 'required' or similar words and duplicate parts in the question"""
    if text:
        text = re.sub(r'\s*required\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'(\b[\w\s]+\b)\s*\1+', r'\1', text)
        text = re.sub(r'\b(\w+)\b\s*\?\s*.*\?\s*$', r'\1?', text)
        text = re.sub(r'(?<!\S)(.+?)(?:(?!\S)\s*|\s*)(\1)(?!\S)', r'\1', text)
        text = ' '.join(text.split())
        return text.strip()
    return " "


class LinkedInExtractAndFill:
    def __init__(self, driver: WebDriver, model: QuestionAnsweringModel) -> None:
        """Extract LinkedIn questions and options and fill inputs using Selenium"""
        self.driver = driver
        self.model = model

    def parse_questions_and_answers(self) -> None:
        """Find and extract job-related form elements using Selenium"""
        sections = None

        try:
            sections = WebDriverWait(self.driver, 10).until(
                ec.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'jobs-easy-apply-form-section__grouping')
                ))
        except TimeoutException:
            pass

        if sections:
            for section in sections:
                self._extract_question_and_fill_answer(section)

    def _extract_question_and_fill_answer(self, section) -> None:
        """Extract the question, input type, options, and associated element"""
        if fieldsets := section.find_elements(
                By.XPATH, './/fieldset[@data-test-form-builder-radio-button-form-component]'):
            self._fill_radio(fieldsets[0], section)

        elif selects := section.find_elements(
                By.XPATH, './/select[@data-test-text-entity-list-form-select]'):
            self._fill_select(selects[0], section)

        elif checkboxes := section.find_elements(By.XPATH, './/input[@type="checkbox"]'):
            for checkbox in checkboxes:
                label = checkbox.find_element(By.XPATH, 'following-sibling::label')
                label.click()

        elif inputs := section.find_elements(By.XPATH, './/input[@type="text"]'):
            self._fill_input(section, inputs[0])

    def _fill_radio(self, radio_element, section) -> None:
        try:
            radio_buttons = radio_element.find_elements(By.TAG_NAME, 'label')
            question_text = section.find_element(By.TAG_NAME, 'legend').text.strip()
            options = [opt.text.strip() for opt in radio_buttons]
            answer = self._get_answer_from_model(clean_text(question_text))

            if answer not in options:
                print(f"No valid answer for radio '{question_text}', selecting first option.")
                radio_buttons[1].click()
            else:
                for radio, label in zip(radio_buttons, options):
                    if label == answer:
                        radio.click()
                        break

        except NoSuchElementException:
            print(f"Error: Could not find radio buttons in section: {section}")

    def _fill_select(self, select_element, section) -> None:
        select_object = Select(select_element)

        try:
            question_text = section.find_element(By.TAG_NAME, 'label').text.strip()
            options = [opt.text.strip()
                       for opt in select_element.find_elements(By.TAG_NAME, 'option')
                       if opt.get_attribute('value')]

            answer = self._get_answer_from_model(clean_text(question_text))
            if answer not in options:
                print(f"No valid answer provided for select '{question_text}', choosing the first option.")
                select_object.select_by_index(1)
            else:
                select_object.select_by_visible_text(answer)

        except NoSuchElementException:
            print(f"Error: Could not find question in section: {section}")
            select_object.select_by_index(1)

    def _fill_input(self, section, input_element) -> None:
        try:
            question_text = section.find_element(By.TAG_NAME, 'label')
            question_text = clean_text(question_text.text.strip())
            answer = self._get_answer_from_model(question_text)

            if (answer == DEFAULT_ANSWERS.get(question_text) or
                    (isinstance(answer, str) and answer.isdigit()) or
                    isinstance(answer, int)):
                input_element.clear()
                input_element.send_keys(answer)
                self._click_outside_to_hide_dropdown()
            else:
                raise ValueError

        except (ValueError, NoSuchElementException):
            input_element.clear()
            input_element.send_keys(0)

    def _click_outside_to_hide_dropdown(self):
        """Click on a non-interactive area to close the suggestion dropdown."""
        try:
            dialog_element = self.driver.find_element(
                By.CSS_SELECTOR,
                'div.artdeco-modal__header h2#jobs-apply-header'
            )
            dialog_element.click()
        except NoSuchElementException:
            print("Warning: Could not find element to click. Dropdown remain open.")

    def _get_answer_from_model(self, question) -> str:
        answer = DEFAULT_ANSWERS.get(question)
        if not answer:
            answer = self.model.ask_question(question)

        return answer


class NaukriDotComExtractAndFill:
    def __init__(self, driver: WebDriver, model: QuestionAnsweringModel) -> None:
        """Extract NaukriDotCom questions and options and fill inputs using Selenium"""
        self.driver = driver
        self.model = model
        self.fill_answer_try_count = 0

    def parse_questions_and_answers(self) -> bool:
        """Extract and fill job-related form elements in the chatbot interface."""
        self.fill_answer_try_count = 0
        li_locator = (By.CSS_SELECTOR, 'li.botItem.chatbot_ListItem')
        initial_li_count = 0

        try:
            while self.fill_answer_try_count < 11:
                chat_box_dialog = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, 'div.chatbot_DrawerContentWrapper'))
                )
                question_element = WebDriverWait(chat_box_dialog, 5).until(
                    ec.presence_of_all_elements_located(li_locator)
                )
                initial_li_count = len(question_element)
                print(initial_li_count)
                question_element = question_element[-1]

                norm_ques = re.sub(r'[^a-zA-Z]', '', question_element.text.strip()).lower()
                norm_target = re.sub(r'[^a-zA-Z]', '', "Thank you for your responses.").lower()

                if norm_ques == norm_target:
                    print(question_element.text.strip())
                    try:
                        WebDriverWait(self.driver, 3).until(ec.staleness_of(chat_box_dialog))
                        return True
                    except (TimeoutException, StaleElementReferenceException):
                        pass

                self._find_input_type_and_fill(question_element)

                try:
                    WebDriverWait(self.driver, 5).until(
                        ec.element_to_be_clickable((By.CSS_SELECTOR, "div.send div.sendMsg"))
                    ).click()
                except (TimeoutException, NoSuchElementException):
                    self.fill_answer_try_count += 1
                    continue

                WebDriverWait(self.driver, 5).until(
                    lambda d: len(d.find_elements(*li_locator)) == initial_li_count + 1
                )
                print("2nd", initial_li_count+1)
        #         STILL SAME ERROR ON INPUT ELEMENT: StaleElementReferenceException

        except (TimeoutException, IndexError):
            pass

        return False

    def _find_input_type_and_fill(self, question_element) -> None:
        try:
            ul_element = question_element.find_element(By.XPATH, "..")
            answer_element = ul_element.find_element(By.XPATH, "following-sibling::*")
        except NoSuchElementException:
            answer_element = None

        self.fill_answer_try_count += 1

        if answer_element:
            if input_div := answer_element.find_elements(By.CSS_SELECTOR, 'div.textArea'):
                self._fill_input_div(input_div[0], question_element.text.strip())

            elif radio_div := answer_element.find_elements(By.CSS_SELECTOR, 'div.singleselect-radiobutton-container'):
                self._fill_radio(radio_div[0], question_element.text.strip())

            elif input_text := answer_element.find_elements(By.XPATH, '//input[@type="text"]'):
                self._fill_input_text(input_text[0], answer_element, question_element.text.strip())

    def _fill_input_div(self, input_element, question) -> None:
        question_text = clean_text(question)
        answer = self._get_answer_from_model(question_text)

        if str(answer).isalnum():
            input_element.clear()
            input_element.send_keys(answer)
        else:
            input_element.clear()
            input_element.send_keys(0)

    def _fill_radio(self, radio_element, question) -> None:
        try:
            radio_buttons_divs = radio_element.find_element(By.CSS_SELECTOR, 'div.ssrc__radio-btn-container')
            options = radio_buttons_divs.find_elements(By.XPATH, './/label')
            options_text = [opt.text.strip() for opt in options]
            answer = self._get_answer_from_model(clean_text(question))

            if answer not in options_text:
                options[0].click()
            else:
                for option, label in zip(options, options_text):
                    if label == answer:
                        option.click()
                        break

        except NoSuchElementException:
            print(f"Error: Could not find radio buttons in section: {radio_element}")

    def _fill_input_text(self, answer_element, input_element, question) -> None:
        try:
            question_text = clean_text(question)
            answer = self._get_answer_from_model(question_text)
            suggestions = input_element.find_elements(By.CSS_SELECTOR, 'div.ssc__wrapper')
            suggestions_text = [suggest.text.strip() for suggest in suggestions]

            if answer in suggestions_text:
                answer_element.clear()
                answer_element.send_keys(answer)
                for suggest in suggestions:
                    if suggest.text.strip() == answer:
                        suggest.click()
                        break
            else:
                answer_element.send_keys("")
                suggestions[0].click()

        except NoSuchElementException:
            print(f"Error: Could not find suggestions in input: {input_element}")

    def _get_answer_from_model(self, question) -> str:
        for k, v in DEFAULT_ANSWERS.items():
            if k.lower() in question.lower():
                return DEFAULT_ANSWERS[k]

        return self.model.ask_question(question)
