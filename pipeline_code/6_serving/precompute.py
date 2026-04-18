import json
import re
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from tqdm import tqdm
from pathlib import Path

MODELS_FOLDER = Path("models-item-item-05milpairs-150coraters")
TOP_K = 10
CHUNK_SIZE = 2048  # rows per batch

def extract_year(date_str):
    if not date_str:
        return 0
    match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
    return int(match.group(0)) if match else 0

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


def build_binary_matrix(items_per_row, vocab):
    vocab_idx = {v: i for i, v in enumerate(vocab)}
    n = len(items_per_row)
    mat = np.zeros((n, len(vocab)), dtype=np.float32)
    for row_i, items in enumerate(items_per_row):
        for item in items:
            if item in vocab_idx:
                mat[row_i, vocab_idx[item]] = 1.0
    return mat


def vectorized_jaccard(a_mat, b_mat):
    intersection = a_mat @ b_mat.T
    a_sum = a_mat.sum(axis=1, keepdims=True)
    b_sum = b_mat.sum(axis=1)
    union = a_sum + b_sum - intersection
    return intersection / (union + 1e-9)


def load_data():
    weights = {"plot_sim": 0.3, "year_sim": 0.15, "genre_sim": 0.2, "director_match": 0.15, "cast_sim": 0.2}

    embeddings_path = "xplot_embeddings_full_data.npy"
    combined_data = np.load(embeddings_path, allow_pickle=True).item()
    embeddings = combined_data['embeddings'].astype(np.float32)
    metadata = combined_data['metadata']
    movies_df = pd.DataFrame(metadata)
    print(f"Loaded {len(movies_df)} movies with {embeddings.shape[1]}-dim embeddings")

    model_path = MODELS_FOLDER / "item_item_recommender.pkl"
    feature_path = MODELS_FOLDER / "feature_columns.json"
    trained_model, feature_cols = None, None
    if model_path.exists() and feature_path.exists():
        trained_model = joblib.load(model_path)
        with open(feature_path) as f:
            feature_cols = json.load(f)
        print(f"Loaded model with features: {feature_cols}")
    else:
        print(f"Model not found at {model_path}. Skipping model precomputation.")

    return weights, embeddings, movies_df, trained_model, feature_cols


def precompute(weights, embeddings, movies_df, trained_model, feature_cols):
    n = len(movies_df)
    records = movies_df.to_dict(orient='records')
    slugs = movies_df['Slug'].tolist()

    years = np.array([extract_year(r.get('Release Date')) for r in records], dtype=np.float32)

    genre_sets = [set(str(r.get('Genre', '')).lower().split()) for r in records]
    genre_vocab = sorted({g for gs in genre_sets for g in gs})
    genre_mat = build_binary_matrix(genre_sets, genre_vocab)

    cast_sets = [set(get_cast_list(r)) for r in records]
    cast_vocab = sorted({c for cs in cast_sets for c in cs})
    cast_mat = build_binary_matrix(cast_sets, cast_vocab)

    directors = np.array([str(r.get('Director', '')).lower() for r in records])

    #normalize embeddings once for fast cosine similarity
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    emb_norm = embeddings / (norms + 1e-9)  # (n, d)

    algo_results = {}
    model_results = {} if trained_model is not None else None

    num_chunks = (n + CHUNK_SIZE - 1) // CHUNK_SIZE

    for chunk_i in tqdm(range(num_chunks), desc="Precomputing", unit="chunk"):
        start = chunk_i * CHUNK_SIZE
        end = min(start + CHUNK_SIZE, n)
        chunk_size = end - start

        plot_sim = emb_norm[start:end] @ emb_norm.T  # cosine sim already

        year_diff = np.abs(years[start:end, None] - years[None, :])  # (chunk, n)
        year_sim = np.maximum(0.0, 1.0 - year_diff / 50.0)

        genre_sim = vectorized_jaccard(genre_mat[start:end], genre_mat)

        director_match = (directors[start:end, None] == directors[None, :]).astype(np.float32)

        cast_sim = vectorized_jaccard(cast_mat[start:end], cast_mat)

        # --- algo score ---
        algo_score_mat = (
            weights['plot_sim']       * plot_sim +
            weights['year_sim']       * year_sim +
            weights['genre_sim']      * genre_sim +
            weights['director_match'] * director_match +
            weights['cast_sim']       * cast_sim
        ) 

        # Zero out self-scores
        for local_i in range(chunk_size):
            algo_score_mat[local_i, start + local_i] = -np.inf

        # Top-K per row
        top_k_indices = np.argpartition(algo_score_mat, -TOP_K, axis=1)[:, -TOP_K:]

        for local_i in range(chunk_size):
            query_slug = slugs[start + local_i]
            row_indices = top_k_indices[local_i]
            row_scores = algo_score_mat[local_i, row_indices]
            order = np.argsort(row_scores)[::-1]
            sorted_indices = row_indices[order]
            algo_results[query_slug] = [
                {"slug": slugs[j], "score": float(algo_score_mat[local_i, j])}
                for j in sorted_indices
            ]

        # --- model scores ---
        if trained_model is not None:
            feature_order = ['plot_sim', 'year_sim', 'genre_sim', 'director_match', 'cast_sim']
            feature_stack = np.stack([
                plot_sim.ravel(),
                year_sim.ravel(),
                genre_sim.ravel(),
                director_match.ravel(),
                cast_sim.ravel(),
            ], axis=1)

            col_map = {name: i for i, name in enumerate(feature_order)}
            feature_stack = feature_stack[:, [col_map[c] for c in feature_cols]]

            model_preds = trained_model.predict(feature_stack).reshape(chunk_size, n) 

            for local_i in range(chunk_size):
                query_slug = slugs[start + local_i]
                model_preds[local_i, start + local_i] = -np.inf
                row_indices = np.argpartition(model_preds[local_i], -TOP_K)[-TOP_K:]
                row_scores = model_preds[local_i, row_indices]
                order = np.argsort(row_scores)[::-1]
                sorted_indices = row_indices[order]
                model_results[query_slug] = [
                    {"slug": slugs[j], "score": float(model_preds[local_i, j])}
                    for j in sorted_indices
                ]

    return algo_results, model_results


def main():
    out_dir = Path("precomputed_recommendations")
    out_dir.mkdir(parents=True, exist_ok=True)

    weights, embeddings, movies_df, trained_model, feature_cols = load_data()

    print("Precomputing recommendations ")
    algo_results, model_results = precompute(weights, embeddings, movies_df, trained_model, feature_cols)

    algo_path = out_dir / "algorithm.json"
    with open(algo_path, "w") as f:
        json.dump(algo_results, f)
    print(f"Saved algorithm recommendations{algo_path}")

    if model_results is not None:
        model_path = out_dir / "model.json"
        with open(model_path, "w") as f:
            json.dump(model_results, f)
        print(f"Saved model recommendations {model_path}")

if __name__ == "__main__":
    main()