from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, InvalidSelectorException


class FillAnswers:
    def __init__(self, driver, form_questions, answers):
        self.driver = driver
        self.form_questions = form_questions
        self.answers = answers

    def fill_answers(self):
        for idx, question in enumerate(self.form_questions):
            question_text = question.get('question', '')
            input_type = question.get('type', 'input')
            element = question.get('element', None)
            answer = self.answers[idx]

            if element is None:
                print(f"Warning: No element found for question '{question_text}'. Skipping.")
                continue  # Skip if the element is None

            try:
                # Use the provided element directly without re-searching
                if input_type == 'radio':
                    self._fill_radio(element, answer.get('radio'))
                elif input_type == 'select':
                    self._fill_select(element, answer.get('select'))
                elif input_type == 'checkbox':
                    self._fill_checkbox(element, answer.get('checkbox'))
                else:
                    self._fill_input(element, answer.get('input', '0'))  # Default to '0' if no answer

            except (TimeoutException, NoSuchElementException, InvalidSelectorException) as e:
                print(f"Failed to fill {input_type} for question '{question_text}'")
                print(e)

    def _fill_radio(self, element, value):
        radio_buttons = element.find_elements_by_tag_name('input')  # Get all radio options
        # Choose the first radio button if no value is provided
        if not value and radio_buttons:
            print("No answer provided for radio button, choosing the first option.")
            radio_buttons[0].click()  # Click the first radio button
        else:
            for radio in radio_buttons:
                if radio.get_attribute("value") == value:
                    radio.click()  # Click the matching radio button
                    break

    def _fill_select(self, element, value):
        select_object = Select(element)
        if not value:
            print("No answer provided for select, choosing the first option.")
            select_object.select_by_index(0)  # Select the first option
        else:
            select_object.select_by_visible_text(value)

    def _fill_checkbox(self, element, value):
        if value:  # If a specific value is provided, click checkbox
            element.click()

    def _fill_input(self, element, value):
        if not value:
            value = '0'  # Default to '0' if no value is provided

        element.clear()
        element.send_keys(value)

        # Ensure element is not None before trying to interact with it
        # if element:
        #     element.clear()
        #     element.send_keys(value)
        # else:
        #     print("Warning: No input element to fill.")
