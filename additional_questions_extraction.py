from bs4 import BeautifulSoup


def clean_text(text):
    return ' '.join(dict.fromkeys(text.split()).keys())


class ExtractQuestionsAndInputs:
    def __init__(self, html_content):
        self.html_content = html_content
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.questions = []
        self.options = []
        self.input_tag_type = ''

    def parse_and_extract(self):
        for section in self.soup.find_all('div', class_='jobs-easy-apply-form-section__grouping'):
            ques_text, options = self.get_options(section)
            input_type = self.get_input_type(section)
            self.questions.append({'question': ques_text, 'input_type': input_type, 'options': options})

    def get_options(self, section):
        self.options = []
        if section.find('fieldset', {'data-test-form-builder-radio-button-form-component': True}):
            self.options = [opt.get_text(strip=True) for opt in section.find_all('label')]
            question_text_extracted = section.find('legend').get_text(strip=True)

        elif section.find('select', {'data-test-text-entity-list-form-select': True}):
            self.options = [opt.get_text(strip=True)
                            for opt in section.find_all('option')
                            if opt.get_text(strip=True) != 'Select an option']
            question_text_extracted = section.find(
                'label', {'data-test-text-entity-list-form-title': True}
            ).get_text(strip=True)

        else:
            question_text_extracted = section.find('label').get_text(strip=True)

        return question_text_extracted, self.options

    def get_input_type(self, section):
        if section.find('div', {'data-test-single-line-text-form-component': True}):
            self.input_tag_type = 'text'
        elif section.find('fieldset', {'data-test-form-builder-radio-button-form-component': True}):
            self.input_tag_type = 'radio'
        elif section.find('select', {'data-test-text-entity-list-form-select': True}):
            self.input_tag_type = 'select'
        else:
            self.input_tag_type = ''

        return self.input_tag_type

    def format_output(self):
        return [
            {
                'idx': idx,
                'question': question,
                'type': input_type,
                'options': options
            }
            for idx, (question, input_type, options) in enumerate(
                zip(
                    [clean_text(question['question']) for question in self.questions],
                    [question['input_type'] for question in self.questions],
                    [question['options'] for question in self.questions]
                ), 1
            )
        ]

    def extract_questions(self):
        self.parse_and_extract()
        return self.format_output()
