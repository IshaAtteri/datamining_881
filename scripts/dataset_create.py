import pandas as pd
import os
from scrape import extract_movie_info

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "..", "sample_data.xlsx")
movie_data = pd.read_excel(file_path)
print(movie_data.columns)

script_dir = os.path.dirname(os.path.abspath(__file__))
movie_html = os.path.join(script_dir, "..", "data", "tt0074888.html")

title, directed_by, cast, genre, plot = extract_movie_info(movie_html)
new_row = {
    "Movie": title,
    "Director": directed_by,
    "Cast": ", ".join(cast),
    "Genre": genre,
    "Plot": plot
}

movie_data.loc[len(movie_data)] = new_row
output_path = os.path.join(script_dir, "..", "updated_data.xlsx")
movie_data.to_excel(output_path, index=False)