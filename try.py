from playwright.sync_api import sync_playwright

URL = "https://ulse.wd5.myworkdayjobs.com/ulsecareers/job/Evanston-IL/Data-Science---Engineering-Intern_JR1410-1?jr_id=6979179b39f7f96cc6d173c0"

hits = []

def on_response(resp):
    req = resp.request
    rtype = req.resource_type
    ct = resp.headers.get("content-type", "")

    # Job data is usually fetched via XHR/fetch and returns JSON
    if rtype in ("xhr", "fetch") and "application/json" in ct:
        hits.append(resp.url)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.on("response", on_response)

    page.goto(URL, wait_until="domcontentloaded", timeout=60000)

    # Scroll a bit in case job details load on scroll
    page.mouse.wheel(0, 2000)
    page.wait_for_timeout(4000)

    browser.close()

print("XHR/FETCH JSON URLs found:", len(hits))
for u in hits[:50]:
    print(u)
