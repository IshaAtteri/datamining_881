import shutil
import re
from bs4 import BeautifulSoup
import os
from libzim.reader import Archive
from libzim.search import Query, Searcher
import csv
from slugify import slugify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_TSV = os.path.abspath(os.path.join(BASE_DIR, "../data/raw/imdb_datasets/title.basics.test.tsv"))
OUTPUT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../data/processed/wikipedia_html_test"))
ZIM_PATH = os.path.abspath(os.path.join(BASE_DIR, "../data/raw/wikipedia/wikipedia_en_all_maxi_2025-08.zim"))

os.makedirs(OUTPUT_DIR, exist_ok=True)
zim = Archive(ZIM_PATH)
searcher = Searcher(zim)
print("The Zim file is now opened")


def sanitize_slug(slug):
    return slugify(slug, separator="_", max_length=200) or "_unknown"


def is_movie_page(html_content, primary_title, original_title, year):
    soup = BeautifulSoup(html_content, "html.parser")
    page_title = soup.find("h1", {"id": "firstHeading"})
    if not page_title:
        return False
    page_title_text = page_title.get_text().lower()
    if primary_title.lower() not in page_title_text and original_title.lower() not in page_title_text:
        return False
    infobox = soup.find("table", {"class": "infobox"})
    if not infobox:
        return False
    infobox_text = infobox.get_text()
    if "Directed by" not in infobox_text or ("Produced by" not in infobox_text and "Written by" not in infobox_text):
        return False
    # Also verify the year appears in the infobox
    if year and year != "\\N" and year not in infobox_text:
        return False
    return True


# Fetch the html AND the images and put them in a folder
def fetch_wikipedia_html_with_images(query, save_dir, primary_title, original_title, year):
    q = Query().set_query(query)
    search = searcher.search(q)
    if search.getEstimatedMatches() == 0:
        return None
    results = list(search.getResults(0, 5))

    for best_path in results:
        try:
            entry = zim.get_entry_by_path(best_path)
            item = entry.get_item()
            html_content = bytes(item.content).decode("UTF-8")
        except Exception:
            continue

        if not is_movie_page(html_content, primary_title, original_title, year):
            continue

        soup = BeautifulSoup(html_content, "html.parser")
        poster_img = None
        infobox = soup.find("table", class_="infobox")
        if infobox:
            poster_img = infobox.select_one("img")
            if poster_img and poster_img.get("src"):
                img_path = poster_img["src"].lstrip("/")
                try:
                    img_entry = zim.get_entry_by_path(img_path)
                    img_bytes = bytes(img_entry.get_item().content)
                    img_name = os.path.basename(img_path)
                    with open(os.path.join(save_dir, img_name), "wb") as f:
                        f.write(img_bytes)
                    poster_img["src"] = img_name
                except Exception:
                    pass
        for img in soup.find_all("img"):
            if img is not poster_img:
                img["src"] = ""
        return str(soup), best_path

    return None


done_set = {
    fname[:-5]
    for d in os.listdir(OUTPUT_DIR)
    if not d.startswith("_tmp_")
    for fname in os.listdir(os.path.join(OUTPUT_DIR, d))
    if fname.endswith(".html")
}
print(f"Found {len(done_set)} already processed")

# Go through each row of the tsv file and try to get the movie on wiki
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
        if tconst in done_set:
            print(f"Skipping already processed: {tconst}")
            continue
            # folder for each movie
        movie_dir = os.path.join(OUTPUT_DIR, f"_tmp_{tconst}")
        os.makedirs(movie_dir, exist_ok=True)
        query = f"{title} ({year} film)" if year != "\\N" else title  # if year not empty
        print(f"fetching Wikipedia HTML + images for {tconst}: {query}")
        result = fetch_wikipedia_html_with_images(query, movie_dir, title, row["originalTitle"], row["startYear"])
        if result is None:
            print("Wikipedia fetch failed")
            shutil.rmtree(movie_dir, ignore_errors=True)
            continue
        else:
            html_with_images, slug = result
        slug_dir = os.path.join(OUTPUT_DIR, sanitize_slug(slug))
        if html_with_images:
            if os.path.exists(slug_dir):
                shutil.rmtree(movie_dir, ignore_errors=True)
            else:
                os.rename(movie_dir, slug_dir)
            outfile = os.path.join(slug_dir, f"{tconst}.html")
            if os.path.exists(outfile):
                continue
            with open(outfile, "w", encoding="utf-8") as out:
                out.write(html_with_images)
                done_set.add(tconst)
        else:
            shutil.rmtree(movie_dir, ignore_errors=True)
            print(f"no Wikipedia page found for {query}")
