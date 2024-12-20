# Python 3.12

import csv
from os import path, makedirs, listdir

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from transformer import QAModelCustom
from model import QuestionAnsweringModel
from linkedin import LinkedInApply
from naukridotcom import NaukriDotComApply

from config import PROFILE_PATH, FINE_TUNED_MODEL_PATH
from config import LOGS_PATH, JOBS_POSTING_LOG_PATH, JOB_LOG_HEADERS
from config import TOTAL_JOBS_LOG_PATH, TOTAL_JOBS_LOG_HEADERS

# False these both if you don't want to train the model
MODEL_TRAINING, USE_FT_MODEL = True, True


def prerequisites():
    global MODEL_TRAINING, USE_FT_MODEL

    if not path.exists(PROFILE_PATH):
        makedirs(PROFILE_PATH)

    if not path.exists(LOGS_PATH):
        makedirs(LOGS_PATH)

    if not path.isfile(JOBS_POSTING_LOG_PATH):
        with open(JOBS_POSTING_LOG_PATH, mode='a',
                  newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(JOB_LOG_HEADERS)

    if not path.isfile(TOTAL_JOBS_LOG_PATH):
        with open(TOTAL_JOBS_LOG_PATH, mode='a',
                  newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(TOTAL_JOBS_LOG_HEADERS)

    if path.exists(FINE_TUNED_MODEL_PATH):
        if len(listdir(FINE_TUNED_MODEL_PATH)) >= 6:
            MODEL_TRAINING = False
    else:
        USE_FT_MODEL = False

    if MODEL_TRAINING:
        print("Training the model on given Dataset!")
        model_training = QAModelCustom()
        model_training.train_model(num_train_epochs=35)
        model_training.save_model(save_path=FINE_TUNED_MODEL_PATH)
        print("SUCCESS: Model trained and saved.")


def linkedin_job_apply(driver: webdriver, model: QuestionAnsweringModel, link=None) -> None:
    if not link:
        linkedin_apply = LinkedInApply(driver=driver, model=model)
        linkedin_apply.easy_apply_to_jobs()
        # linkedin_apply.search_jobs_apply("Python Developer")
    else:
        linkedin_single_apply = LinkedInApply(driver, model, link)
        linkedin_single_apply.easy_apply_single_job()


def naukridotcom_job_apply(driver: webdriver, model: QuestionAnsweringModel, link=None) -> None:
    if not link:
        naukri_apply = NaukriDotComApply(driver=driver, model=model)
        naukri_apply.apply_recommended_jobs()
    else:
        naukri_single_apply = NaukriDotComApply(driver, model, link,)
        naukri_single_apply.apply_to_job()


def main():
    prerequisites()

    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")
    web_driver = webdriver.Chrome(options=chrome_options)
    web_driver.maximize_window()

    qa_model = QuestionAnsweringModel(USE_FT_MODEL)

    try:
        linkedin_job_apply(web_driver, qa_model)
        naukridotcom_job_apply(web_driver, qa_model)
    finally:
        web_driver.quit()


if __name__ == "__main__":
    main()
