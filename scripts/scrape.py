import requests

url = "https://en.wikipedia.org/w/api.php"

headers = {
    "User-Agent": "CSE881-MovieProject/1.0 (ishaa@msu.edu)"
}

params = {
    "action": "query",
    "format": "json",
    "prop": "extracts",
    "titles": "Interstellar",
    "explaintext": True,
    "redirects": 1
}

response = requests.get(url, headers=headers, params=params)

print("Status:", response.status_code)
print("Content-Type:", response.headers.get("content-type"))
print("First 200 chars:\n", response.text[:200])

data = response.json()

pages = data["query"]["pages"]
page = next(iter(pages.values()))

print("\nTitle:", page["title"])
print("\nPreview:\n", page["extract"][:500])
