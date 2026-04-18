import requests

url = "https://ulse.wd5.myworkdayjobs.com/wday/cxs/ulse/ulsecareers/job/Evanston-IL/Data-Science---Engineering-Intern_JR1410-1"
# url = 'https://motorolasolutions.wd5.myworkdayjobs.com/en-US/Careers/job/Schaumburg-IL/Machine-Learning-AI-Intern--Summer-2026-Internship-Program-_R59959?jr_id=69793e9952f3c27ec6459544'

# url = 'https://mcafee.wd1.myworkdayjobs.com/External/job/US-California-San-Jose/Data-Science-Intern_JR0032270?jr_id=6979499688e2b47213bd807f'
page = requests.get(url)

print(page.content)

# data = page.json()
# print(data.keys())

# print('here')
# job = data["jobPostingInfo"]

# print(job.keys())

# company = data["hiringOrganization"]

# print(company.keys())

# comp = company["name"]
# print("Company:", comp)
