import re
from logging import getLogger, ERROR
from warnings import filterwarnings
from tensorflow import compat
from torch import device, cuda
from transformers import pipeline
from transformers import T5ForConditionalGeneration, T5Tokenizer

from config import SUMMARY_TEXT
from config import FINE_TUNED_MODEL_PATH


class QuestionAnsweringModel:
    def __init__(self, model_training=False):
        """Initializes a question-answering model, either pre-trained or fine-tuned"""

        # Set TensorFlow logging level to ERROR to suppress info logs
        compat.v1.logging.set_verbosity(compat.v1.logging.ERROR)
        getLogger("transformers").setLevel(ERROR)
        filterwarnings("ignore", category=FutureWarning)

        self.number_pattern = re.compile(r'\b\d+\b')
        self.train_model = model_training

        if self.train_model:
            self.tokenizer = T5Tokenizer.from_pretrained(FINE_TUNED_MODEL_PATH)
            self.model = T5ForConditionalGeneration.from_pretrained(FINE_TUNED_MODEL_PATH)
            self.device = device("cuda" if cuda.is_available() else "cpu")
            self.model = self.model.to(self.device)
        else:
            self.qa_model = pipeline(
                "question-answering",
                model="distilbert-base-cased-distilled-squad",
                revision="626af31"
            )

    def infer_answer(self, text: str) -> str:
        """Infers the answer from the given text."""
        if text:
            if text.startswith("Yes") or text.startswith("No"):
                return "Yes" if text.startswith("Yes") else "No"
            else:
                number_match = self.number_pattern.search(text)
                if number_match:
                    return number_match.group()
            return text.split()[0]
        else:
            return ""

    def ask_question(self, question: str, max_length=5) -> str:
        """Asks a question and returns the inferred answer."""
        if question:
            if self.train_model:
                input_text = f"question: {question}  context: {SUMMARY_TEXT}"
                input_ids = self.tokenizer(input_text, return_tensors="pt")
                input_ids = input_ids.input_ids.to(self.device)
                outputs = self.model.generate(input_ids, max_length=max_length)
                predicted_answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            else:
                result = self.qa_model(question=question, context=SUMMARY_TEXT)
                predicted_answer = result['answer']

            return self.infer_answer(str(predicted_answer))

    def ask_multiple_questions(self, questions_list) -> list:
        """Asks multiple questions and return the inferred answers."""
        answers_list = []
        for question in questions_list:
            if question:
                answer = self.ask_question(question)
                answers_list.append(answer)
            else:
                answers_list.append("")

        return answers_list
