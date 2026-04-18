import pandas as pd
import numpy as np
import os
import re
import warnings

warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RATINGS_FILE = os.path.join(BASE_DIR, "data", "processed", "spreadsheets", "2_netflix_ground_truth.tsv")
EMBEDDINGS_FILE = os.path.join(BASE_DIR, "data", "processed", "xplot_embeddings_full_data.npy")
FEATURE_COLS = ['plot_sim', 'year_sim', 'genre_sim', 'director_match', 'cast_sim']

def load_netflix_ratings():
    return pd.read_csv(RATINGS_FILE, sep="\t")

def load_movie_data():
    combined_data = np.load(EMBEDDINGS_FILE, allow_pickle=True).item()
    embeddings = combined_data['embeddings']
    metadata = combined_data['metadata']
    movies_df = pd.DataFrame(metadata)
    slug_to_idx = {movie['Slug']: i for i, movie in enumerate(metadata)}
    
    # Normalize embeddings once
    emb_matrix = np.array(embeddings, dtype=np.float32)
    norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    emb_matrix /= norms
    
    return movies_df, emb_matrix, slug_to_idx

def extract_year(date_str):
    if not date_str or pd.isna(date_str):
        return 0
    match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
    return int(match.group(0)) if match else 0

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def get_cast_list(movie):
    val = movie.get('Pre_cast')
    if isinstance(val, str):
        return [x.strip().lower() for x in val.split(',') if x.strip()]
    if isinstance(val, list):
        return [str(x).strip().lower() for x in val if str(x).strip()]
    
    val = movie.get('Cast')
    if isinstance(val, str):
        return [x.strip().lower() for x in val.split(',') if x.strip()]
    if isinstance(val, list):
        return [str(x).strip().lower() for x in val if str(x).strip()]
    
    return []

def compute_pairwise_features(movie_a, movie_b, emb_a, emb_b):
    features = {}
    
    # plot similarity (cosine of pre-normalized embeddings)
    features['plot_sim'] = np.dot(emb_a, emb_b)

    # year similarity
    year_a = extract_year(movie_a.get('Release Date'))
    year_b = extract_year(movie_b.get('Release Date'))
    features['year_sim'] = max(0, 1 - abs(year_a - year_b) / 50)

    # genre similarity
    genre_a = set(str(movie_a.get('Genre', '')).lower().split())
    genre_b = set(str(movie_b.get('Genre', '')).lower().split())
    features['genre_sim'] = jaccard_similarity(genre_a, genre_b)

    # director match
    dir_a = str(movie_a.get('Director', '')).lower().strip()
    dir_b = str(movie_b.get('Director', '')).lower().strip()
    features['director_match'] = 1.0 if dir_a and dir_b and dir_a == dir_b else 0.0

    # cast similarity
    cast_a = set(get_cast_list(movie_a))
    cast_b = set(get_cast_list(movie_b))
    features['cast_sim'] = jaccard_similarity(cast_a, cast_b)

    return features
