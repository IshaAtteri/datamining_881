import pandas as pd
import os
from rapidfuzz import fuzz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NETFLIX_DIR = os.path.join(BASE_DIR, "../data/raw/netflix/")
MOVIE_EXCEL = os.path.join(BASE_DIR, "../data/processed/spreadsheets/updated_data_test.xlsx")
MOVIE_TITLES = os.path.join(NETFLIX_DIR, "movie_titles.csv")
COMBINED_FILES = [os.path.join(NETFLIX_DIR, f"combined_data_{i}.txt") for i in range(1, 5)]
OUTPUT = os.path.join(BASE_DIR, "../data/processed/spreadsheets/fused_gtruth_test.csv")

TITLE_THRESHOLD = 85   # fuzzy search

main_data = pd.read_excel(MOVIE_EXCEL)
main_data["title_lower"] = main_data["Title"].str.lower().str.strip()
main_data["director_lower"] = main_data["Director"].fillna("").str.lower().str.strip()


records = []
with open(MOVIE_TITLES, encoding="latin-1") as f:
    for line in f:
        line = line.strip()
        parts = line.split(",", 2)
        if len(parts) == 3:
            records.append({"netflix_id": int(parts[0]), "year": parts[1], "title": parts[2].strip()})

titles_df = pd.DataFrame(records)
titles_df["title_lower"] = titles_df["title"].str.lower().str.strip()
netflix_id_to_tt = {}   # netflix_id -> tt_id

for _, nrow in titles_df.iterrows():
    best_score = 0
    best_meta = None

    #https://github.com/rapidfuzz/RapidFuzz docs
    for _, mrow in main_data.iterrows():
        score = fuzz.ratio(nrow["title_lower"], mrow["title_lower"])
        if score > best_score:
            best_score = score
            best_meta = mrow

    if best_score < TITLE_THRESHOLD or best_meta is None:
        continue

    # Director match
    confirmed = best_score >= TITLE_THRESHOLD
    print(best_score)
    if best_meta["director_lower"] and best_score >= 70:
        # year relese year match
        try:
            meta_year = str(best_meta["Release Date"])
            nf_year = str(int(nrow["year"])) if pd.notna(nrow["year"]) else ""
            if nf_year and nf_year in meta_year:
                confirmed = True
        except Exception:
            pass

    if confirmed:
        netflix_id_to_tt[int(nrow["netflix_id"])] = best_meta["Slug"]

print(f"Matched {len(netflix_id_to_tt)} Netflix movies to tt Ids")

valid_netflix_ids = set(netflix_id_to_tt.keys())
rows = []
current_movie_id = None

for filepath in COMBINED_FILES:
    print(f"Reading {os.path.basename(filepath)}...")
    with open(filepath, encoding="latin-1") as f:
        for line in f:
            line = line.strip()
            if line.endswith(":"):
                current_movie_id = int(line[:-1])
            elif current_movie_id in valid_netflix_ids:
                parts = line.split(",")
                if len(parts) == 3:
                    customer_id, rating, date = parts
                    rows.append({
                        "customer_id": int(customer_id),
                        "tt_id": netflix_id_to_tt[current_movie_id],
                        "rating": int(rating),
                        "date": date,
                    })

print(f"Found {len(rows):,} rating")
print(f"Found {len(valid_netflix_ids):,} movies ground truth")


df = pd.DataFrame(rows)
df.to_csv(OUTPUT, index=False)
print(f"Written to {OUTPUT}")
