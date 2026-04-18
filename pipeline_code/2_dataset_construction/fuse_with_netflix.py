import pandas as pd
import os
from rapidfuzz import process, fuzz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NETFLIX_DIR = os.path.join(BASE_DIR, "../../data/raw/netflix/")
MOVIE_EXCEL = os.path.join(BASE_DIR, "../../data/processed/spreadsheets/3_preprocessed_dataset.xlsx")
MOVIE_TITLES = os.path.join(NETFLIX_DIR, "movie_titles.csv")
COMBINED_FILES = [os.path.join(NETFLIX_DIR, f"combined_data_{i}.txt") for i in range(1, 5)]
OUTPUT = os.path.join(BASE_DIR, "../../data/processed/spreadsheets/2_netflix_ground_truth.tsv")

TITLE_THRESHOLD = 85

main_data = pd.read_excel(MOVIE_EXCEL)
main_data["title_lower"] = main_data["Title"].str.lower().str.strip()
main_data["director_lower"] = main_data["Director"].fillna("").str.lower().str.strip()

main_titles = main_data["title_lower"].tolist()

records = []
with open(MOVIE_TITLES, encoding="latin-1") as f:
    for line in f:
        parts = line.strip().split(",", 2)
        if len(parts) == 3:
            records.append((int(parts[0]), parts[1], parts[2].strip().lower()))

titles_df = pd.DataFrame(records, columns=["netflix_id", "year", "title_lower"])

netflix_id_to_tt = {}

for nf_id, nf_year, nf_title in titles_df.itertuples(index=False):
    match = process.extractOne(
        nf_title,
        main_titles,
        scorer=fuzz.ratio,
        score_cutoff=TITLE_THRESHOLD
    )

    if match is None:
        continue

    best_title, best_score, match_idx = match
    best_meta = main_data.iloc[match_idx]

    confirmed = best_score >= TITLE_THRESHOLD

    if best_meta["director_lower"] and best_score >= 70:
        try:
            meta_year = str(best_meta["Release Date"])
            nf_year_str = str(int(nf_year)) if pd.notna(nf_year) else ""
            if nf_year_str and nf_year_str in meta_year:
                confirmed = True
        except:
            pass

    if confirmed:
        netflix_id_to_tt[nf_id] = best_meta["Slug"]

print(f"Matched {len(netflix_id_to_tt)} Netflix movies to tt Ids")

valid_netflix_ids = set(netflix_id_to_tt.keys())
rows = []
current_movie_id = None

for filepath in COMBINED_FILES:
    print(f"Reading {os.path.basename(filepath)}...")
    with open(filepath, encoding="latin-1") as f:
        for line in f:
            if line.endswith(":\n"):
                current_movie_id = int(line[:-2])
                continue

            if current_movie_id not in valid_netflix_ids:
                continue

            parts = line.strip().split(",")
            if len(parts) == 3:
                customer_id, rating, date = parts
                rows.append((
                    int(customer_id),
                    netflix_id_to_tt[current_movie_id],
                    int(rating),
                    date
                ))

df = pd.DataFrame(rows, columns=["customer_id", "tt_id", "rating", "date"])

print(f"Found {len(rows):,} ratings")
print(f"Found {len(valid_netflix_ids):,} movies ground truth")

df.to_csv(OUTPUT, sep="\t", index=False)
print(f"Written to {OUTPUT}")
