import csv
import os
import requests
from time import sleep

HEADERS = {"User-Agent": "cse881"}
SEARCH_URL = "https://en.wikipedia.org/w/api.php"
BASE_URL = "https://en.wikipedia.org/api/rest_v1"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_TSV = os.path.abspath(os.path.join(BASE_DIR, "../data/raw/imdb_datasets/title.basics.test.tsv"))
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../data/raw/wikipedia/wikipedia_html"))

os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_wikipedia_html(query):
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json"
    }

    resp = requests.get(SEARCH_URL, params=params, headers=HEADERS).json()
    results = resp.get("query", {}).get("search", [])

    if not results:
        return None

    best_title = results[0]["title"]
    wiki_title = best_title.replace(" ", "_")
    html_url = f"{BASE_URL}/page/html/{wiki_title}"
    r = requests.get(html_url, headers=HEADERS)

    if r.status_code != 200:
        return None
    return r.text


with open(INPUT_TSV, encoding="utf-8") as f:
    print("Opened file:", INPUT_TSV)
    print("First 500 chars:")
    print(f.read(500))
    f.seek(0)

    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        tconst = row["tconst"]
        title = row["primaryTitle"]
        year = row["startYear"]
        outfile = os.path.join(OUTPUT_DIR, f"{tconst}.html")
        print(outfile)

        if os.path.exists(outfile):
            print(f"Skipping {tconst}: {query}")
            continue #if exists, skip

        query = f"{title} {year}" if year != "\\N" else title
        print(f"Fetching Wikipedia for {tconst}: {query}")
        html = fetch_wikipedia_html(query)
        if html:
            with open(outfile, "w", encoding="utf-8") as out:
                out.write(html)
        else:
            print(f"No Wikipedia page found")
        sleep(0.5)
print("Completed")

#https://en.wikipedia.org/w/index.php?api=wmf-restbase&title=Special%3ARestSandbox#/Page%20content/get_page_summary__title_
