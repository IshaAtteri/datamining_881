import requests

endpoints = [
    "https://ulse.wd5.myworkdayjobs.com/wday/cxs/ulse/ulsecareers/job/Evanston-IL/Data-Science---Engineering-Intern_JR1410-1",
    "https://ulse.wd5.myworkdayjobs.com/wday/cxs/ulse/ulsecareers/sidebar/Data-Science---Engineering-Intern_JR1410-1",
]

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
}

for url in endpoints:
    r = requests.get(url, headers=headers, timeout=30)
    print("\n===", url, "===")
    print("Status:", r.status_code)
    print("Content-Type:", r.headers.get("content-type"))
    # Try JSON
    try:
        data = r.json()
        print("JSON parsed ✅")
        if isinstance(data, dict):
            print("Top-level keys:", list(data.keys())[:40])
        else:
            print("Type:", type(data), "Len:", len(data))
    except Exception:
        print("Not JSON. Text preview:\n", r.text[:600])
