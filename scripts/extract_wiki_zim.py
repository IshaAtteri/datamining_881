import shutil
import re
from bs4 import BeautifulSoup
import os
from libzim.reader import Archive
from libzim.search import Query, Searcher
import csv
from slugify import slugify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_TSV = os.path.abspath(os.path.join(BASE_DIR, "../data/raw/imdb_datasets/title.basics.tsv"))
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../data/processed/wikipedia_html"))
ZIM_PATH = os.path.abspath(os.path.join(BASE_DIR, "../data/raw/wikipedia/wikipedia_en_all_maxi_2025-08.zim"))

os.makedirs(OUTPUT_DIR, exist_ok=True)
zim = Archive(ZIM_PATH)
searcher = Searcher(zim)
print("The Zim file is now opened")


def sanitize_slug(slug):
    return slugify(slug, separator="_", max_length=200) or "_unknown"

#Fetch the html AND the images and put them in a folder
def fetch_wikipedia_html_with_images(query, save_dir):
    q = Query().set_query(query)
    search = searcher.search(q)
    if search.getEstimatedMatches() == 0:
        return None
    results = list(search.getResults(0, 5))
    best_path = results[0]
    try:
        entry = zim.get_entry_by_path(best_path)
        item = entry.get_item()
        html_content = bytes(item.content).decode("UTF-8")
    except Exception:
        return None
    soup = BeautifulSoup(html_content, "html.parser")
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        img_path = src.lstrip("/")
        try:
            img_entry = zim.get_entry_by_path(img_path)
            img_bytes = bytes(img_entry.get_item().content)
        except Exception:
            continue
        img_name = os.path.basename(img_path)
        img_file_path = os.path.join(save_dir, img_name)
        with open(img_file_path, "wb") as f:
            f.write(img_bytes)
        img["src"] = img_name
    return str(soup), best_path

#Go through each row of the tsv file and try to get the movie on wiki
with open(INPUT_TSV, encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        tconst = row["tconst"]
        title = row["primaryTitle"]
        year = row["startYear"]
        titleType = row["titleType"]
        if year is None or titleType != "movie":
            print("Skipping from TSV: ", title)
            continue
        already_done = False
        for d in os.listdir(OUTPUT_DIR):
            if os.path.exists(os.path.join(OUTPUT_DIR, d, f"{tconst}.html")):
                already_done = True
                break
        if already_done:
            print(f"Skipping already processed: {tconst}")
            continue
        # folder for each movie
        movie_dir = os.path.join(OUTPUT_DIR, f"_tmp_{tconst}")
        os.makedirs(movie_dir, exist_ok=True)
        query = f"{title} ({year} film)" if year != "\\N" else title #if year not empty
        print(f"fetching Wikipedia HTML + images for {tconst}: {query}")
        result = fetch_wikipedia_html_with_images(query, movie_dir)
        if result is None:
            print("Wikipedia fetch failed")
            shutil.rmtree(movie_dir, ignore_errors=True)
            continue
        else:
            html_with_images, slug = result
        slug_dir = os.path.join(OUTPUT_DIR, sanitize_slug(slug))
        if html_with_images:
            if "Directed by" not in html_with_images:
                shutil.rmtree(movie_dir, ignore_errors=True)
                continue
            if os.path.exists(slug_dir):
                shutil.rmtree(movie_dir, ignore_errors=True)
            else:
                os.rename(movie_dir, slug_dir)
            outfile = os.path.join(slug_dir, f"{tconst}.html")
            if os.path.exists(outfile):
                continue
            with open(outfile, "w", encoding="utf-8") as out:
                out.write(html_with_images)
        else:
            shutil.rmtree(movie_dir, ignore_errors=True)
            print(f"no Wikipedia page found for {query}")