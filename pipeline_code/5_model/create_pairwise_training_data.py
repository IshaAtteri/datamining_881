# Create pairwise training data from Netflix ground truth ratings.
# For each user, for each pair of movies they rated, compute features and target
# pairwise model learns based on the score of movie which is preferred. 
# It can see if users prefer certain things over the other.

#this one is still broken. needs fixing
import pandas as pd
import numpy as np
import os
import re
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RATINGS_FILE = os.path.join(BASE_DIR, "data", "processed", "spreadsheets", "2_netflix_ground_truth.csv")
EMBEDDINGS_FILE = os.path.join(BASE_DIR, "data", "processed", "xplot_embeddings_full_data.npy")
OUTPUT_PARQUET = os.path.join(BASE_DIR, "data", "processed", "pairwise_training_data.parquet")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "processed", "pairwise_training_data.csv")

def load_netflix_ratings():
    return pd.read_csv(RATINGS_FILE)

def load_movie_data():
    combined_data = np.load(EMBEDDINGS_FILE, allow_pickle=True).item()
    embeddings = combined_data['embeddings']
    metadata = combined_data['metadata']
    movies_df = pd.DataFrame(metadata)
    slug_to_idx = {movie['Slug']: i for i, movie in enumerate(metadata)}
    return movies_df, embeddings, slug_to_idx

def extract_year(date_str):
    if not date_str:
        return 0
    match = re.search(r'\b(19|20)\d{4}\b', str(date_str))
    return int(match.group(0)) if match else 0

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def cosine_similarity_vec(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return np.dot(a, b) / (norm_a * norm_b)

def compute_pairwise_features(movie_a, movie_b, emb_a, emb_b):
    features = {}
    features['plot_sim'] = cosine_similarity_vec(emb_a, emb_b)

    year_a = extract_year(movie_a.get('Release Date'))
    year_b = extract_year(movie_b.get('Release Date'))
    features['year_diff'] = abs(year_a - year_b)
    features['year_sim'] = max(0, 1 - features['year_diff'] / 50)

    genre_a = str(movie_a.get('Genre', '')).lower().strip()
    genre_b = str(movie_b.get('Genre', '')).lower().strip()
    features['genre_sim'] = jaccard_similarity(set(genre_a.split()), set(genre_b.split()))

    dir_a = str(movie_a.get('Director', '')).lower().strip()
    dir_b = str(movie_b.get('Director', '')).lower().strip()
    features['director_match'] = int(dir_a and dir_b and dir_a == dir_b)

    cast_a = movie_a.get('Pre_cast') or movie_a.get('Cast', [])
    cast_b = movie_b.get('Pre_cast') or movie_b.get('Cast', [])
    if isinstance(cast_a, str):
        cast_a = [a.strip().lower() for a in cast_a.split(',') if a.strip()]
    if isinstance(cast_b, str):
        cast_b = [b.strip().lower() for b in cast_b.split(',') if b.strip()]
    features['cast_sim'] = jaccard_similarity(set(cast_a), set(cast_b))

    return features

def create_pairwise_training_data():
    ratings_df = load_netflix_ratings()
    movies_df, embeddings, slug_to_idx = load_movie_data()

    # Keep only movies we have embeddings for
    valid_slugs = set(movies_df['Slug'].unique())
    ratings_df = ratings_df[ratings_df['tt_id'].isin(valid_slugs)].copy()

    pairwise_rows = []
    user_groups = ratings_df.groupby('customer_id')

    for user_id, group in tqdm(user_groups, total=len(user_groups)):
        if len(group) < 2:
            continue
        user_ratings = list(zip(group['tt_id'], group['rating']))
        for i in range(len(user_ratings)):
            for j in range(len(user_ratings)):
                if i == j:
                    continue
                slug_i, rating_i = user_ratings[i]
                slug_j, rating_j = user_ratings[j]
                try:
                    movie_i = movies_df[movies_df['Slug'] == slug_i].iloc[0].to_dict()
                    movie_j = movies_df[movies_df['Slug'] == slug_j].iloc[0].to_dict()
                    emb_i = embeddings[slug_to_idx[slug_i]]
                    emb_j = embeddings[slug_to_idx[slug_j]]
                except (IndexError, KeyError):
                    continue
                features = compute_pairwise_features(movie_i, movie_j, emb_i, emb_j)
                pairwise_rows.append({
                    'user_id': user_id,
                    'movie_i': slug_i,
                    'movie_j': slug_j,
                    'rating_i': rating_i,
                    'rating_j': rating_j,
                    **features
                })

    pairwise_df = pd.DataFrame(pairwise_rows)
    os.makedirs(os.path.dirname(OUTPUT_PARQUET), exist_ok=True)

    pairwise_df.to_parquet(OUTPUT_PARQUET, index=False)
    pairwise_df.to_csv(OUTPUT_CSV, index=False)

    return pairwise_df

if __name__ == "__main__":
    create_pairwise_training_data()