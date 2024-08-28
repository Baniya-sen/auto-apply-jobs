import random
import re
from logging import getLogger, ERROR
from warnings import filterwarnings
from tensorflow import compat
from torch import device, cuda
from transformers import pipeline
from transformers import T5ForConditionalGeneration, T5Tokenizer
from sklearn.metrics import accuracy_score

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
                print(f"{question}: {answer}")
                answers_list.append(answer)
            else:
                answers_list.append("")

        return answers_list


# Example usage
# if __name__ == "__main__":
#     questions = [
#         "Experience with RESTful API development and integration? ",
#         "Knowledge of Web scrapping libraries like beautiful soup etc? ",
#         "Strong knowledge of Python and its libraries (NumPy, Pandas, Scikit-Learn, TensorFlow, PyTorch)? ",
#         "NumPy, Pandas, Scikit-Learn, TensorFlow, PyTorch?",
#         "Proven experience in SaaS environments? ",
#         "How many years of work experience do you have in Python?",
#         "How many years of work experience do you have with Google Cloud Platform (GCP)?",
#         "What is your current yearly CTC",
#         "What is your current notice period ?",
#         "How many years of work experience do you have with Looker (Software)?",
#         "How many years of work experience you have in Service Now?",
#         "experience in Python",
#         "Are you familiar with Scikit-Learn?",
#         "Are you open to Unpaid Internship?",
#         "Do you have experience in Numpy?",
#         "Expected yearly salary?",
#         "Do you have experience in Azure?",
#         "Can you work in a remote setting",
#         "How will you rate yourself in Python from 1-5?",
#         "Can you commute to this jon location?",
#         "How much experience you have in ETL?",
#         "How many years of experience do you have with Python?"
#         "How many years of experience do you have in Django?",
#         "How many years of work experience do you have in Django?",
#         "Expected yearly salary?",
#         "What is your current CTC?",
#         "Your notice period?",
#         "Do you have experience with Amazon Web Services?",
#         "Do you have work experience with Amazon Web Services?",
#         "How many years of experience you have with Microsoft Azure?",
#         "How many years of work experience you have with Microsoft Azure?",
#         "How many years of work experience do you have with Node.js?",
#         "How many years of experience do you have with React.js?",
#     ]
#
#     answers_true = ["Yes", "Yes", "Yes,", "Yes", "No", "4", "1", "0",
#                     "0", "0", "0", "Yes", "Yes", "No", "Yes", "350000",
#                     "Yes", "Yes", "4", "Yes", "1", "4", "1", "1", "350000",
#                     "0", "0", "Yes", "Yes" "1", "1", "0", "0"]
#
#     # print(len(questions))
#     # print(len(answers_true))
#
#     indices = random.sample(range(len(questions)), 10)
#     selected_list1 = [questions[i] for i in indices]
#     selected_list2 = [answers_true[i] for i in indices]
#
    # model = QuestionAnsweringModel(True)
    # answers_pred = model.ask_multiple_questions(questions)
#     answers_pred_rand = model.ask_multiple_questions(selected_list1)
#
#     print("\nThe all ques accuracy is " + str(accuracy_score(answers_true, answers_pred)) + "%")
#     print("The random ques accuracy is " + str(accuracy_score(selected_list2, answers_pred_rand)) + "%")
