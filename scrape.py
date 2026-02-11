from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

URL = "https://ulse.wd5.myworkdayjobs.com/ulsecareers/job/Evanston-IL/Data-Science---Engineering-Intern_JR1410-1?jr_id=6979179b39f7f96cc6d173c0"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle", timeout=60000)

    # Wait a bit more for dynamic content (Workday can be heavy)
    page.wait_for_timeout(2000)

    html = page.content()
    browser.close()

soup = BeautifulSoup(html, "lxml")
text = soup.get_text(" ", strip=True)

print("Rendered text length:", len(text))
print("Title:", soup.title.get_text(strip=True) if soup.title else None)
# print("\nSample:\n", text[:1500])

def extract_job_description(full_text):
    lt = full_text.lower()

    start_markers = [
        "job description",
        "about the role",
        "job summary"
    ]

    end_markers = [
        "equal opportunity",
        "eeo",
        "ul is an equal",
        "application process",
        "how to apply",
        "privacy",
        "cookies"
    ]

    start_idx = -1
    for m in start_markers:
        i = lt.find(m)
        if i != -1:
            start_idx = i + len(m)
            break

    if start_idx == -1:
        return None

    end_idx = len(full_text)
    for m in end_markers:
        i = lt.find(m, start_idx)
        if i != -1:
            end_idx = i
            break

    description = full_text[start_idx:end_idx].strip()
    return description

job_desc = extract_job_description(text)

print("\n--- CLEAN JOB DESCRIPTION ---\n")
print(job_desc if job_desc else "No job description found.")
print("\nLength:", len(job_desc))
