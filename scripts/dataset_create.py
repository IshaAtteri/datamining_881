import pandas as pd
import os
from scrape import extract_movie_info

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "../data/processed/wikipedia_html_test/")
SPREADSHEET_DIR = os.path.join(BASE_DIR, "../data/processed/spreadsheets/")

rows = []

for folder in os.listdir(INPUT_DIR):
    path = os.path.join(INPUT_DIR, folder)
    script_dir = next((f for f in os.listdir(path) if f.endswith(".html")), None)
    if not script_dir:
        continue
    full_path = os.path.join(path, script_dir)
    slug = os.path.splitext(script_dir)[0]
    try:
        print(full_path)
        title, directed_by, cast, genre, plot, year, poster_filename = extract_movie_info(full_path)
        rows.append({
            "Title": title,
            "Director": directed_by,
            "Cast": ", ".join(cast),
            "Genre": genre,
            "Plot": plot,
            "Release Date": year,
            "Slug": slug,
            "Poster Filename": poster_filename
        })

    except KeyboardInterrupt:
        movie_data = pd.DataFrame(rows)
        output_path = os.path.join(SPREADSHEET_DIR, "updated_datav_test.xlsx")
        movie_data.to_excel(output_path, index=False)
        quit()
    except Exception as e:
        print("error:", e)

movie_data = pd.DataFrame(rows)
output_path = os.path.join(SPREADSHEET_DIR, "updated_data_test.xlsx")
print(output_path)
movie_data.to_excel(output_path, index=False)