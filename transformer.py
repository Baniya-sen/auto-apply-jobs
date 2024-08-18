import logging
import warnings
import tensorflow as tf
import torch
from torch.utils.data import Dataset
from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments


class QADatasetCustom(Dataset):
    def __init__(self, tokenizer: T5Tokenizer, context, questions, answers, max_length=512):
        """Defined custom dataset for multiple questions with a single context"""
        self.context = context
        self.questions = questions
        self.answers = answers
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.questions)

    def __getitem__(self, idx):
        question = self.questions[idx]
        answer = self.answers[idx]

        input_text = f"question: {question}  context: {self.context}"
        input_ids = self.tokenizer(input_text, truncation=True, padding='max_length',
                                   max_length=self.max_length, return_tensors="pt")
        labels = self.tokenizer(answer, truncation=True, padding='max_length',
                                max_length=self.max_length, return_tensors="pt")
        labels[labels == self.tokenizer.pad_token_id] = -100

        return {"input_ids": input_ids.input_ids.squeeze(), "labels": labels.input_ids.squeeze()}


class QAModelCustom:
    def __init__(self, context: str, questions: list, answers: list, model_name='t5-small'):
        """Initializes model, tokenizer, and dataset"""
        self.save_model_path = "./trained_model"
        self.model_name = model_name
        self.context = context
        self.questions = questions
        self.answers = answers
        self.training_args = ()
        self.trainer = ()
        self.ft_model = None
        self.ft_tokenizer = None

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
        self.model = self.model.to(self.device)

        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
        self.dataset = QADatasetCustom(
            self.tokenizer, self.context, self.questions, self.answers
        )

        warnings.filterwarnings("ignore", category=FutureWarning)
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
        logging.getLogger("transformers").setLevel(logging.ERROR)

    def train_model(self) -> None:
        """ based on a context, list of questions, and list of answers"""
        self.training_args = TrainingArguments(
            output_dir="./results",
            num_train_epochs=10,
            per_device_train_batch_size=4,
            save_steps=10_000,
            save_total_limit=2,
            logging_dir="./logs",
        )

        self.trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=self.dataset,
        )

        self.trainer.train()

    def save_model(self, save_path=None) -> None:
        """Save the fine-tuned pre-trained model and tokenizer to directory"""
        if not save_path:
            save_path = self.save_model_path

        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)

    def load_trained_model(self, save_path=None) -> None:
        """Load the fine-tuned trained model and tokenizer to use"""
        if not save_path:
            save_path = self.save_model_path

        self.ft_tokenizer = T5Tokenizer.from_pretrained(save_path)
        self.ft_model = T5ForConditionalGeneration.from_pretrained(save_path)
        self.ft_model = self.ft_model.to(self.device)

    def generate_answer(self, question: str, context=None, max_length=5) -> str:
        if not context:
            context = self.context

        input_text = f"question: {question}  context: {context}"
        input_ids = self.tokenizer(input_text, return_tensors="pt")
        input_ids = input_ids.input_ids.to(self.device)
        outputs = self.model.generate(input_ids, max_length=max_length)
        predicted_answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return predicted_answer

    def generate_multiple_answers(self, questions: list, context=None) -> list:
        predicted_answers = []
        for question in questions:
            answer = self.generate_answer(question, context)
            predicted_answers.append(answer)

        return predicted_answers


if __name__ == "__main__":
    # Example dataset with one context and multiple questions
    contexts = """SUMMARY: I have 0 years of work experience in anything I did not mentioned here. If I don't mention
    something it means I have No experience in it. I have 0 years of experience with in anything any tool any tech any
    language everything that I didn't mentioned. I am having 0 years of experience with in anything. No I don't have any
    experience in anything and everything I didn't mentioned. No I am not familiar with anything any tool any tech any
    language that i did not mentioned. No I am not a anything. I will only answer in one word or number but not both. My
    name is Bhanu. My gender is Male. Yes I am looking for a job position as Data Analyst, Data Analysis, Data Scientist,
    DS/ML, or software developer. Yes, I can work from the office, Yes I can work from home, Yes I can work in a remote
    setting, and Yes I can work in a hybrid setting. I am a software developer. Yes I have 1 year of experience in Data
    Analysis. Yes I have 1 year of experience as a Data Analyst. Yes I know programming languages like Python Java C++.
    Yes I have experience with in backend development and cloud computing. Yes I have 1 year of experience with
    cloud-based data platforms. Yes I've worked on various projects from building high-performance APIs to developing
    machine learning models for predictive analytics. Yes I know Agile methodologies and Yes I know version control
    systems like Git. Yes I have 4 years of experience in Python. Yes I have 1 years of experience in Django. Yes I have
    2 years of experience in Flask. Yes I have 3 years of experience in HTML. Yes I have 2 years of experience in Web
    Frontend Development. Yes I have 1 year of experience in CSS and Javascript. Yes I have 1 year of experience in
    MongoDB. Yes I have 1 year of experience in SQL. Yes I have 1 years of work experience do you have with in Power BI.
    Yes I have 1 years of experience knowledge in Pandas Numpy Matplotlib Scikit-Learn Seaborn plotly.
    My expected salary ECTC is 350000. Currently I earn nothing. My current salary CTC is 0 . I do not work
    anywhere. No i am not working anywhere. Yes I am a fresher. Yes I have completed completed a level of Masters's
    Degree level. I had completed my post-graduation MCA in 2023. My post graduation stream was MCA. Yes I have completed
    a level of Bachelor's Degree in 2019. I had choose BCA as my graduation stream. Yes I can start immediately. Notice
    period is 0. I can start working in 0 days. Yes My current location is Faridabad. My home address is
    'Faridabad, Haryana, India'. I am an Indian so I select I prefer not to specify when asked about my race. No I do not
    have any disability. No I am not a veteran and I prefer not to say. Yes My preferred locations to work are Noida,
    Gurugram, and Delhi. Yes I can work anywhere in India. No I do not require work permit to work in the country I am
    applying for. Yes I am comfortable working in any timezone starting at any time. Yes I am willing to undergo a
    background check in accordance with local law/regulations. Yes I have experience in Data Analysis and Statistical
    Analysis. Yes I can work with role require for the job."""

    questions = [
        "Can you work in a remote setting?",
        "How much experience do you have in python?",
        "Do you know HTML?",
        "Do you have experience in Django?",
        "What is your expected salary?",
        "Are you working somewhere?",
        "Are you a fresher?",
        "When did you complete your post-graduation?",
        "Which stream did you do your post-graduation?",
        "How much experience do you have in Flask?",
        "Do you have experience in data analysis?",
        "Notice period in days?",
        "Can you start immediately?",
        "Can you work in a hybrid setting?",
        "How much experience do you have in C++?",
        "Do you have experience with Node.js?",
        "What is your current salary?",
        "Are you familiar with Azure?",
        "How much experience do you have in cloud technologies?",
        "When did you graduate in BCA?",
        "Do you have experience in data pre-processing?",
        "Where are you currently located?",
        "Can you work from the office?",
        "Proficiency with frameworks such as FastAPI or Django? ",
        "How many years of work experience do you have with Power BI?",
        "Do you have experience with cloud-based data platforms (e.g., AWS, Google Cloud, Azure) ?",
        "How many years of experience you are having in CRIF strategy one tool?",
        "This role requires Full time freelancer, Are you a full freelancer?",
        "How many years of work experience do you have with PyTorch?",
        "How many years of experience you have in SQL?",
        "How many years of experience you have in Jquery?",
        "Are you familiar with React.js?",
        "Do you require work permit in country you are applying for?",
        "Are you comfortable working in the New Zealand time zone starting at 1 a.m.? ",
        "How many years of work experience do you have with Database Testing?",
        "How much experience you have in frontend development?",
        "How much experience you have in Java?",
        "Experience with cloud platforms (AWS, Azure, GCP)? ",
        "Knowledge of Docker and container orchestration (Kubernetes)? ",
        "Generative AI Knowledge: Experience with Large Language Models (LLM) and mainstream AI technologies?",
        "Proficiency with frameworks such as FastAPI or Django? ",
        "Familiarity with LangChain and LangGraph? ",
        "Experience with data preprocessing, feature engineering, and model evaluation? ",
        "On a scale of 1 to 10, how well qualified do you consider yourself for this position? ",
        "Proficient in SQL, NoSQL and Vector Databases? ",
        "Experience with RESTful API development and integration? ",
        "Knowledge of Web scrapping libraries like beautiful soup etc? ",
        "Strong knowledge of Python and its libraries (NumPy, Pandas, Scikit-Learn, TensorFlow, PyTorch)? ",
        "NumPy, Pandas, Scikit-Learn, TensorFlow, PyTorch"
    ]

    answers = [
        "Yes",  # Can you work in a remote setting?
        "4",  # How much experience do you have in Python?
        "Yes",  # Do you know HTML?
        "Yes",  # Do you have experience in Django?
        "350000",  # What is your expected salary?
        "No",  # Are you working somewhere?
        "Yes",  # Are you a fresher?
        "2023",  # When did you complete your post-graduation?
        "MCA",  # Which stream did you do your post-graduation?
        "2",  # How much experience do you have in Flask?
        "Yes",  # Do you have experience in data analysis?
        "0",  # Notice period in days?
        "Yes",  # Can you start immediately?
        "Yes",  # Can you work in a hybrid setting?
        "1",  # How much experience do you have in C++?
        "No",  # Do you have experience with Node.js?
        "0",  # What is your current salary?
        "No",  # Are you familiar with Azure?
        "1",  # How much experience do you have in cloud technologies?
        "2019",  # When did you graduate in BCA?
        "Yes",  # Do you have experience in data pre-processing?
        "Faridabad",  # Where are you currently located?
        "Yes",  # Can you work from the office?
        "No",  # Proficiency with frameworks such as FastAPI or Django?
        "0",  # How many years of work experience do you have with Power BI?
        "Yes",  # Do you have experience with cloud-based data platforms (e.g., AWS, Google Cloud, Azure)?
        "0",  # How many years of experience you are having in CRIF strategy one tool?
        "No",  # This role requires Full time freelancer, Are you a full freelancer?
        "0",  # How many years of work experience do you have with PyTorch?
        "1",  # How many years of experience you have in SQL?
        "0",  # How many years of experience you have in Jquery?
        "No",  # Are you familiar with React.js?
        "No",  # Do you require work permit in country you are applying for?
        "Yes",  # Are you comfortable working in the New Zealand time zone starting at 1 a.m.?
        "0",  # How many years of work experience do you have with Database Testing?
        "2",  # How much experience you have in frontend development?
        "1",  # How much experience you have in Java?
        "Yes",  # Experience with cloud platforms (AWS, Azure, GCP)?
        "No",  # Knowledge of Docker and container orchestration (Kubernetes)?
        "No",  # Generative AI Knowledge: Experience with Large Language Models (LLM) and mainstream AI technologies?
        "Yes",  # Proficiency with frameworks such as FastAPI or Django?
        "No",  # Familiarity with LangChain and LangGraph?
        "Yes",  # Experience with data preprocessing, feature engineering, and model evaluation?
        "8",  # On a scale of 1 to 10, how well qualified do you consider yourself for this position?
        "Yes",  # Proficient in SQL, NoSQL and Vector Databases?
        "Yes",  # Experience with RESTful API development and integration?
        "Yes",  # Knowledge of Web scraping libraries like Beautiful Soup etc.?
        "Yes",  # Strong knowledge of Python and its libraries (NumPy, Pandas, Scikit-Learn, TensorFlow, PyTorch)?
        "Yes,"  # "NumPy, Pandas, Scikit-Learn, TensorFlow, PyTorch"
    ]

    val_questions = [
        "Is you preferred location Bangalore?",
        "Our office is in Ahmedabad, can you commute to this location?",
        "Can you work in a hybrid setting?",
        "How much experience do you have in C++?",
        "Do you have experience with Node.js?",
        "What is your current salary?",
        "Are you familiar with Azure?",
        "How much experience do you have in cloud technologies?",
        "When did you graduate in BCA?",
        "Do you have experience in data pre-processing?",
        "Where are you currently located?",
        "Can you work from the office?",
        "Proficiency with frameworks such as FastAPI or Django? ",
        "Generative AI Knowledge: Experience with Large Language Models (LLM) and mainstream AI technologies?",
        "Familiarity with LangChain and LangGraph? ",
        "Is you preferred location Noida?",
        "Our office is in Gurugram, can you commute to this location?",
        "Knowledge in ServiceNow?"
    ]

    model = QAModelCustom(contexts, questions, answers)
    model.train_model()
    model.save_model()
    model.load_trained_model()
    model.generate_answer("Do you know Python?")
