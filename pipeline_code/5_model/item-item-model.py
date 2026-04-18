# plan
# load data  -> User ratings + movie metadata/embeddings
# center ratings  -> Subtract each user's average (remove bias - sub avg)
# build sparse matrix  -> (movies users) with centered ratings
# filter pairs  -> Keep only pairs with 100+ shared users
# compute cosine similarity  -> Measure how similarly users rate each pair
# compute content features  -> plot similarity, cast overlap, embedding distance, etc.
# write training data  -> pk1
# split data  -> 60% train, 40% eval
# train XGBoost  -> predict collab_similarity from features
# save model  -> similarity score

import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import joblib
import json
import pyarrow as pa
import pyarrow.parquet as pq
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity as sparse_cosine
import warnings
warnings.filterwarnings('ignore')
from xgboost import XGBRegressor

from helper_functions import (
    load_netflix_ratings,
    load_movie_data,
    compute_pairwise_features,
    FEATURE_COLS,
    BASE_DIR
)

MODEL_DIR = os.path.join(BASE_DIR, "data", "processed", "models-item-item-05milpairs-150coraters")
OUTPUT_PARQUET = os.path.join(MODEL_DIR, "item_item_training_data.parquet")
EVAL_PARQUET = os.path.join(MODEL_DIR, "item_item_eval_data.parquet")
MODEL_FILE = os.path.join(MODEL_DIR, "item_item_recommender.pkl")
FEATURES_FILE = os.path.join(MODEL_DIR, "feature_columns.json")
SPLIT_INFO_FILE = os.path.join(MODEL_DIR, "train_test_split_info.json")

TRAIN_FRACTION = 0.60
MIN_CO_RATERS = 150 #higher reduces noise
MAX_PAIRS = 500_000 #lower pair makes model more confident
CHUNK_SIZE = 50_000
RANDOM_SEED = 42


def _flush_chunk(rows, writer, schema):
    if not rows:
        return
    table = pa.Table.from_pydict(
        {col: [r[col] for r in rows] for col in schema},
    )
    writer.write_table(table)
    rows.clear()


def build_collaborative_similarity(ratings_df, valid_slugs):
    df = ratings_df[ratings_df['tt_id'].isin(valid_slugs)].copy()

    user_cat = df['customer_id'].astype('category')
    movie_cat = df['tt_id'].astype('category')
    user_idx = user_cat.cat.codes.values
    movie_idx = movie_cat.cat.codes.values
    ratings = df['rating'].values.astype(np.float32)
    slug_list = list(movie_cat.cat.categories)
    n_movies = len(slug_list)
    n_users = len(user_cat.cat.categories)

    user_means = df.groupby('customer_id')['rating'].transform('mean').values.astype(np.float32)
    centered_ratings = ratings - user_means

    matrix = csr_matrix(
        (centered_ratings, (movie_idx, user_idx)),
        shape=(n_movies, n_users)
    )

    binary = (matrix != 0).astype(np.float32)
    co_rater_counts = (binary @ binary.T).toarray()

    sim_matrix = sparse_cosine(matrix)

    pairs = {}
    for i in tqdm(range(n_movies), desc="Extracting pairs"):
        for j in range(i + 1, n_movies):
            if co_rater_counts[i, j] >= MIN_CO_RATERS:
                a, b = slug_list[i], slug_list[j]
                if a > b:
                    a, b = b, a
                pairs[(a, b)] = float(sim_matrix[i, j])

    return pairs


def write_pairs_to_parquet(pair_keys, collab_pairs, movie_dict, output_path, desc="Processing"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    schema_cols = ['movie_a', 'movie_b', 'collab_similarity'] + FEATURE_COLS

    writer = None
    chunk = []
    total_rows = 0

    for pair in tqdm(pair_keys, desc=desc):
        slug_a, slug_b = pair
        info_a = movie_dict.get(slug_a)
        info_b = movie_dict.get(slug_b)
        if info_a is None or info_b is None:
            continue

        features = compute_pairwise_features(
            info_a['metadata'], info_b['metadata'],
            info_a['embedding'], info_b['embedding'],
        )

        row = {
            'movie_a': slug_a,
            'movie_b': slug_b,
            'collab_similarity': collab_pairs[pair],
            **features,
        }
        chunk.append(row)

        if len(chunk) >= CHUNK_SIZE:
            if writer is None:
                table = pa.Table.from_pydict({c: [r[c] for r in chunk] for c in schema_cols})
                writer = pq.ParquetWriter(output_path, table.schema)
                writer.write_table(table)
            else:
                _flush_chunk(chunk, writer, schema_cols)
            total_rows += len(chunk)
            chunk.clear()

    if chunk:
        if writer is None:
            table = pa.Table.from_pydict({c: [r[c] for r in chunk] for c in schema_cols})
            writer = pq.ParquetWriter(output_path, table.schema)
            writer.write_table(table)
        else:
            _flush_chunk(chunk, writer, schema_cols)
        total_rows += len(chunk)
        chunk.clear()

    if writer is not None:
        writer.close()

    return total_rows


def create_item_item_training_data():
    ratings_df = load_netflix_ratings()
    movies_df, embeddings, slug_to_idx = load_movie_data()

    valid_slugs = set(movies_df['Slug'].unique())
    ratings_df = ratings_df[ratings_df['tt_id'].isin(valid_slugs)].copy()

    movie_dict = {}
    for _, row in movies_df.iterrows():
        slug = row['Slug']
        if slug in slug_to_idx:
            movie_dict[slug] = {
                'metadata': row.to_dict(),
                'embedding': embeddings[slug_to_idx[slug]],
            }

    collab_pairs = build_collaborative_similarity(ratings_df, valid_slugs)
    if len(collab_pairs) == 0:
        return None

    rng = np.random.RandomState(RANDOM_SEED)
    pair_keys = list(collab_pairs.keys())
    if len(pair_keys) > MAX_PAIRS:
        rng.shuffle(pair_keys)
        pair_keys = pair_keys[:MAX_PAIRS]

    rng.shuffle(pair_keys)
    split_idx = int(len(pair_keys) * TRAIN_FRACTION)
    train_pairs = pair_keys[:split_idx]
    eval_pairs = pair_keys[split_idx:]

    train_rows = write_pairs_to_parquet(
        train_pairs, collab_pairs, movie_dict, OUTPUT_PARQUET, desc="Train set"
    )

    eval_rows = write_pairs_to_parquet(
        eval_pairs, collab_pairs, movie_dict, EVAL_PARQUET, desc="Eval set"
    )

    split_info = {
        "total_pairs": len(pair_keys),
        "train_pairs": len(train_pairs),
        "eval_pairs": len(eval_pairs),
        "train_fraction": TRAIN_FRACTION,
        "train_rows": train_rows,
        "eval_rows": eval_rows,
        "min_co_raters": MIN_CO_RATERS,
        "max_pairs": MAX_PAIRS,
        "random_seed": RANDOM_SEED,
    }
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(SPLIT_INFO_FILE, 'w') as f:
        json.dump(split_info, f, indent=2)

    df = pd.read_parquet(OUTPUT_PARQUET)
    return df


def train_and_save_model(df):
    X = df[FEATURE_COLS].values
    y = df['collab_similarity'].values

    model = XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=8,
        min_child_weight=1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_SEED,
        tree_method='hist',
        verbosity=1,
    )
    model.fit(X, y, verbose=True)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    with open(FEATURES_FILE, 'w') as f:
        json.dump(FEATURE_COLS, f, indent=2)


if __name__ == "__main__":
    df = create_item_item_training_data()
    if df is not None:
        train_and_save_model(df)
