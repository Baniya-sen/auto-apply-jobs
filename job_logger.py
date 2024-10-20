import csv
from datetime import datetime

from config import JOBS_POSTING_LOG_PATH, TOTAL_JOBS_LOG_PATH


def log_applied_job(job_info, site_name):
    now = datetime.now()

    new_job = [
        job_info["job_position"],
        job_info["company_name"],
        job_info["experience_level"],
        job_info["salary"],
        job_info["job_location"],
        now.strftime("%d-%m-%Y"),
        now.strftime("%H:%M"),
        now.day,
        now.month,
        now.year,
        site_name
    ]
    with open(JOBS_POSTING_LOG_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(new_job)


def total_jobs_log(jobs_extracted, jobs_traversed, jobs_applied, jobs_saved, site_name):
    now = datetime.now()

    new_job = [
        now.strftime("%d-%m-%Y"),
        jobs_extracted,
        jobs_traversed,
        jobs_applied,
        jobs_saved,
        site_name
    ]
    with open(TOTAL_JOBS_LOG_PATH, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(new_job)
