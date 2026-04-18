import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../3_preprocessing')))

import pandas as pd
from sentence_transformers import SentenceTransformer
from preprocessing import clean_plot, get_genre, pre_director, clean_cast
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INPUT_FILE = os.path.join(BASE_DIR, "data", "processed", "spreadsheets","2_dataset_structured.xlsx")
OUTPUT_XLSX = os.path.join(BASE_DIR, "data", "processed", "spreadsheets", "3_preprocessed_dataset.xlsx")
OUTPUT_NPY = os.path.join(BASE_DIR, "data", "processed", "xplot_embeddings_full_data.npy")

df = pd.read_excel(INPUT_FILE, engine='openpyxl')
df = df.dropna(subset=['Plot'])

print(len(df))

df['Processed_Plot'] = df['Plot'].apply(clean_plot)
df['Pre_genre'] = df[['Genre', 'Title']].apply(get_genre, axis=1)
df['Pre_director'] = df['Director'].apply(pre_director)
df['Pre_cast'] = df['Cast'].apply(clean_cast)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate embeddings
plot_embeddings = model.encode(
    df["Processed_Plot"].tolist(),
    show_progress_bar=True,
    convert_to_numpy=True
)

# Combine embeddings with metadata
metadata_fields = [
    'Title', 'Director', 'Cast', 'Genre', 'Plot', 'Release Date',
    'Slug', 'Poster Filename', 'Processed_Plot', 'Pre_genre',
    'Pre_director', 'Pre_cast'
]

combined_data = {
    'embeddings': plot_embeddings,
    'metadata': df[metadata_fields].to_dict('records'),
    'embedding_dim': plot_embeddings.shape[1],
    'num_movies': len(df)
}

# Save combined data
np.save(OUTPUT_NPY, combined_data, allow_pickle=True)

# Save updated Excel
df.to_excel(OUTPUT_XLSX, index=False)
