import os
import re
import csv
import pandas as pd
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "../data/processed/wikipedia_html")
OUTPUT_TSV = os.path.join(BASE_DIR, "../data/processed/spreadsheet/wikipedia_metadata4.tsv")

WHITELIST = {
    "slug",
    "title",
    "poster_filename",
    "Directed by",
    "Produced by",
    "Written by",
    "Starring",
    "Release date",
    "Running time",
    "Country",
    "Language",
    "Budget",
    "Box office",
    "Plot"
}

def clean(el):
    if not el:
        return ""
    for br in el.find_all("br"):
        br.replace_with(" | ")
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()

def parse_html(path, slug):
    with open(path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    row = {"slug": slug}
    h1 = soup.select_one("h1.firstHeading")
    if h1:
        row["title"] = h1.get_text(strip=True)
    else:
        row["title"] = ""
    # infobox
    infobox = soup.select_one("table.infobox")
    if infobox:
        img = infobox.select_one("img")
        if img and img.get("src"):
            row["poster_filename"] = os.path.basename(img["src"])
        else:
            row["poster_filename"] = ""
        for tr in infobox.select("tr"):
            th = tr.select_one(".infobox-label")
            td = tr.select_one(".infobox-data")
            if th and td:
                row[clean(th)] = clean(td)
    # sections
    content = soup.select_one(".mw-parser-output")
    if not content:
        return {k: v for k, v in row.items() if k in WHITELIST}
    skip = {"references", "external links", "see also"}
    current = None
    lead = []
    for el in content.children:
        if getattr(el, "name", None) == "div" and "mw-heading" in el.get("class", []):
            h = el.find(["h2", "h3", "h4", "h5", "h6"]) #assuming no more than first 6 headers need to be looked at
            if h:
                title = clean(h)
                if title.lower() in skip:
                    current = None
                else:
                    current = title
                if current:
                    row[current] = ""
            continue
        if not current:
            if getattr(el, "name", None) == "p":
                text = clean(el)
                if text:
                    lead.append(text)
            continue
        if el.name in ["p", "ul", "ol", "table"]:
            text = clean(el)
            if text:
                row[current] += text
    if lead:
        if row.get("Plot"):
            row["Plot"] = " | ".join(lead) + " | " + row["Plot"]
        else:
            row["Plot"] = " | ".join(lead)
    return {k: v for k, v in row.items() if k in WHITELIST}

def main():
    rows = []
    for folder in os.listdir(INPUT_DIR):
        path = os.path.join(INPUT_DIR, folder)
        html = next((f for f in os.listdir(path) if f.endswith(".html")), None)
        if not html:
            continue
        try:
            rows.append(parse_html(os.path.join(path, html), folder))
        except Exception as e:
            print("error:", html, e)
    df = pd.DataFrame(rows).fillna("")
    if df.empty:
        print("The folder was empty / None parsed")
        return
    cols = ["slug", "poster_filename"] + [c for c in df.columns if c not in ("slug", "poster_filename")]
    df = df[cols]
    os.makedirs(os.path.dirname(OUTPUT_TSV), exist_ok=True)
    df.to_csv(OUTPUT_TSV, sep="\t", index=False, quoting=csv.QUOTE_NONE, escapechar="\\")
    print(f"Wrote {len(df)} rows -> {OUTPUT_TSV}")

if __name__ == "__main__":
    main()

