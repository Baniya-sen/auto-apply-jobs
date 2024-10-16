DEFAULT_LINK = "https://www.naukri.com/mnjuser/recommendedjobs"
link = "https://www.naukri.com/mnjuser/recommendedjobs/12"

jobs_css_pass = ("div.recommended-jobs-page div.list article"
                 if link == DEFAULT_LINK else "article")

print(jobs_css_pass)
