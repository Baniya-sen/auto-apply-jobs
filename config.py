from os import path

# Default paths
PROFILE_PATH = path.abspath("selenium_profile")
FINE_TUNED_MODEL_PATH = path.abspath("fine_tuned_model")
LOGS_PATH = path.abspath("logs")
JOBS_POSTING_LOG_PATH = path.abspath("logs/jobs_applied_log.csv")
TOTAL_JOBS_LOG_PATH = path.abspath("logs/total_jobs_log.csv")

# Default answers to basic questions
DEFAULT_ANSWERS = {
    "First name": "Bhanu",
    "Middle name": "",
    "Last name": "Pratap",
    "Gender": "Male",
    "Email address": "bhanugupta421.bg@gmail.com",
    "Phone country code": "India (+91)",
    "Mobile phone number": 9873173896,
    "State": "Haryana",
    "Location (city)": "Faridabad, Haryana, India",
    "City": "Faridabad, Haryana, India",
    "Address": "Faridabad, Haryana, India",
    "Specialization": "Python, Data Analysis, Visualization, Backend, Development",
    "Highest Qualification": "MCA",
    "Class 12": 55,
    "Class 10": 50,
    "UG": 6.7,
    "PG": 7.7,
    "rate": 4,
}

# Default number of job apply target and log headers
JOB_APPLY_TARGET = 50
JOB_LOG_HEADERS = ["Job Title", "Company Name", "Experience", "Salary", "Location",
                   "Date Applied", "Time Applied", "Day", "Month", "Year", "Job Site"]
TOTAL_JOBS_LOG_HEADERS = ["Date", "Jobs Extracted", "Job Traversed", "Job Applied", "Jobs Saved", "Site"]

# These are the context passage, training questions, and answers for model to train from
SUMMARY_TEXT = """SUMMARY: I have 0 years of work experience in anything I did not mentioned here. If I don't mention 
something it means I have No work experience in it. I have 0 years of work experience with in anything any tool any 
tech any language everything that I didn't mentioned. I am having 0 years of work experience with in anything. No I 
don't have any work experience in anything and everything I didn't mentioned. No I am not familiar with anything any 
tool any tech any language that i did not mentioned. No I am not a anything. I will only answer in one word or number 
but not both. My name is Bhanu. My gender is Male. Yes I am looking for a job position as Data Analyst, 
Data Analysis, Data Scientist, DS/ML, or software developer. Yes, I can work from the office, Yes I can work from 
home, Yes I can work in a remote setting, Yes I can work in a hybrid setting, and Yes I can work with a contractual 
role. I am a software developer. Yes I have 1 year of work experience in Data Analysis. Yes I have 1 year of work 
experience as a Data Analyst. Yes I know programming languages like Python Java C++. Yes I have work experience with 
in backend development and cloud computing. Yes I have 1 year of work experience with cloud-based data platforms. Yes 
I've worked on various projects from building high-performance APIs to developing machine learning models for 
predictive analytics. Yes I know Agile methodologies and Yes I know version control systems like Git. Yes I have 4 
years of work experience in Python. Yes I have 1 year of work experience in Pandas, Numpy, Matplotlib, Plotly, 
Seaborn, Scikit-Learn, TensorFlow, PyTorch. Yes I am familiar with Pandas, Numpy, Matplotlib, Plotly, Seaborn, 
Scikit-Learn, TensorFlow, PyTorch. Yes I have 1 years of experience with in ETL [Extract Transform Load]. Yes I have 
1 year of work experience in Django. Yes I have 2 years of work experience in Flask. Yes I have 3 years of work 
experience in HTML. Yes I have 2 years of work experience in Web Frontend Development. Yes I have 1 year of work 
experience in CSS and Javascript. Yes I have 1 year of work experience in MongoDB. Yes I have 1 year of work 
experience in SQL. Yes I have 1 years of work experience do you have with in Power BI. Yes I have 1 year of work 
experience familiar with in Google cloud platform, Amazon Web Services AWS, Microsoft Azure. My expected CTC [ECTC] 
is 350000. My yearly expected compensation is 350000. Currently I earn nothing. My current salary CTC is 0. 0 CTC. I 
do not work anywhere. No i am not working anywhere. Yes I am a fresher. Yes I have completed completed a level of 
Masters's Degree level. I had completed my post-graduation MCA in 2023. My post graduation stream was MCA. Yes I have 
completed a level of Bachelor's Degree in 2019. I had choose BCA as my graduation stream. Yes I can start 
immediately. Notice period is 0. I can start working in 0 days. Yes My current location is Sector-11 Faridabad. My 
home address is 'Faridabad, Haryana, India'. I am an Indian so I select I prefer not to specify when asked about my 
race. No I do not have any disability. No I am not a veteran and I prefer not to say. Yes My preferred locations to 
work are Noida, Gurugram, and Delhi. Yes I can work anywhere in India. No I do not require work permit to work in the 
country I am applying for. Yes I am comfortable working in any timezone starting at any time. Yes I am willing to 
undergo a background check in accordance with local law/regulations. Yes I have work experience in Data Analysis and 
Statistical Analysis. Yes I can work with role require for the job. I would rate me 4 on on every skill and 
technology I have mentioned. On a scale of 1 to 10 I would consider myself 10 for this position."""

QUESTIONS = [
    "Can you work in a remote setting?",
    "How much experience do you have in python?",
    "Do you know HTML?",
    "Do you have experience in Django?",
    "What is your expected salary?",
    "Current salary?",
    "ECTC",
    "CTC",
    "Are you working somewhere?",
    "Are you a fresher?",
    "When did you complete your post-graduation?",
    "Which stream did you do your post-graduation?",
    "How much experience do you have in Flask?",
    "Do you have experience in data analysis?",
    "Notice period?",
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
    "How would you rate yourself on Python?",
    "How would you rate yourself on SQL?",
    "Experience with cloud platforms (AWS, Azure, GCP)? ",
    "Knowledge of Docker and container orchestration (Kubernetes)? ",
    "Generative AI Knowledge: Experience with Large Language Models (LLM) and mainstream AI technologies?",
    "Proficiency with frameworks such as FastAPI or Django? ",
    "Familiarity with LangChain and LangGraph? ",
    "Experience with data preprocessing, feature engineering, and model evaluation? ",
    "Proficient in SQL, NoSQL and Vector Databases? ",
    "Experience with RESTful API development and integration? ",
    "Knowledge of Web scrapping libraries like beautiful soup etc? ",
    "Strong knowledge of Python and its libraries (NumPy, Pandas, Scikit-Learn, TensorFlow, PyTorch)? ",
    "NumPy, Pandas, Scikit-Learn, TensorFlow, PyTorch?",
    "Proven experience in SaaS environments? ",
    "On a scale of 1 to 10, how well qualified do you consider yourself for this position?",
    "How many years of work experience do you have in Python?",
    "How many years of work experience do you have with Google Cloud Platform (GCP)?",
    "What is your current yearly CTC",
    "What is your current notice period ?",
    "How many years of work experience do you have with Looker (Software)?",
    "How many years of work experience you have in Service Now?",
    "Experience in Python",
    "Are you familiar with Scikit-Learn?",
    "Are you open to Unpaid Internship?",
    "Do you have experience in Numpy?"
]

ANSWERS = [
    "Yes",  # Can you work in a remote setting?
    "4",  # How much experience do you have in Python?
    "Yes",  # Do you know HTML?
    "Yes",  # Do you have experience in Django?
    "350000",  # What is your expected salary?
    "0",  # Current salary?
    "350000",  # ECTC?
    "0",  # CTC?
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
    "2",  # "How much experience you have in frontend development?"
    "1",  # "How much experience you have in Java?"
    "4",  # "How would you rate yourself on Python?"
    "4",  # "How would you rate yourself on SQL?"
    "Yes",  # Experience with cloud platforms (AWS, Azure, GCP)?
    "No",  # Knowledge of Docker and container orchestration (Kubernetes)?
    "No",  # Generative AI Knowledge: Experience with Large Language Models (LLM) and mainstream AI technologies?
    "Yes",  # Proficiency with frameworks such as FastAPI or Django?
    "No",  # Familiarity with LangChain and LangGraph?
    "Yes",  # Experience with data preprocessing, feature engineering, and model evaluation?
    "Yes",  # Proficient in SQL, NoSQL and Vector Databases?
    "Yes",  # Experience with RESTful API development and integration?
    "Yes",  # Knowledge of Web scraping libraries like Beautiful Soup etc.?
    "Yes",  # Strong knowledge of Python and its libraries (NumPy, Pandas, Scikit-Learn, TensorFlow, PyTorch)?
    "Yes,",  # "NumPy, Pandas, Scikit-Learn, TensorFlow, PyTorch"
    "No",  # "Proven experience in SaaS environments? "
    "8",  # "On a scale of 1 to 10, how well qualified do you consider yourself for this position?"
    "4",
    "1",
    "0",
    "0",
    "0",
    "0",
    "4",
    "Yes",
    "No",
    "Yes",
]
