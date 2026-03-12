import pandas as pd
import os
from scrape import extract_movie_info

script_dir = os.path.dirname(os.path.abspath(__file__))
# file_path = os.path.join(script_dir, "..", "sample_data.xlsx")
# movie_data = pd.read_excel(file_path)
# print(movie_data.columns)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = r'C:\Users\Prabhaav\Projects\PyCharm\datamining_881\data\processed\wikipedia_html'
SPREADSHEET_DIR = os.path.join(BASE_DIR, "../data/processed/spreadsheets/")

movie_data = pd.DataFrame(columns=['Title', 'Director', 'Cast', 'Genre', 'Plot', 'Release Date', 'Slug', 'Poster Filename'])

for folder in os.listdir(INPUT_DIR):
    path = os.path.join(INPUT_DIR, folder)
    script_dir = os.path.join(path, next((f for f in os.listdir(path) if f.endswith(".html")), None))
    if not script_dir:
        continue
    try:
        print(script_dir)
        title, directed_by, cast, genre, plot, year, poster_filename = extract_movie_info(script_dir)
        new_row = {
            "Title": title,
            "Director": directed_by,
            "Cast": ", ".join(cast),
            "Genre": genre,
            "Plot": plot,
            "Release Date": year,
            "Slug": script_dir,
            "Poster Filename": poster_filename
        }
        movie_data.loc[len(movie_data)] = new_row

    except Exception as e:
        print("error:", e)
    except KeyboardInterrupt:
        output_path = os.path.join(SPREADSHEET_DIR, "updated_data.xlsx")
        print(output_path)
        movie_data.to_excel(output_path, index=False)
        quit()

output_path = os.path.join(SPREADSHEET_DIR, "updated_data.xlsx")
print(output_path)
movie_data.to_excel(output_path, index=False)