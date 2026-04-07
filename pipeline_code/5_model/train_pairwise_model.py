# Train a pairwise recommendation model from Netflix ground truth.
# Uses HistGradientBoostingRegressor to predict rating_j given features of (movie_i, movie_j).
# https://scikit-learn.org/stable/user_guide.html
# https://medium.com/@sumanadhikari/building-a-movie-recommendation-engine-using-scikit-learn-8dbb11c5aa4b

import pandas as pd
import numpy as np
import json
import os
from sklearn.ensemble import HistGradientBoostingRegressor
import joblib
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRAINING_DATA_FILE = os.path.join(BASE_DIR, "data", "processed", "pairwise_training_data.parquet")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_FILE = os.path.join(MODEL_DIR, "pairwise_recommender.pkl")
FEATURES_FILE = os.path.join(MODEL_DIR, "feature_columns.json")

def load_training_data():
    if not os.path.exists(TRAINING_DATA_FILE):
        raise FileNotFoundError(
            f"Pairwise training data not found at {TRAINING_DATA_FILE}. "
            "Please run create_pairwise_training_data.py first."
        )
    return pd.read_parquet(TRAINING_DATA_FILE)

def prepare_features(df):
    feature_cols = [
        'plot_sim',
        'year_diff',
        'year_sim',
        'genre_sim',
        'director_match',
        'cast_sim'
    ]
    X = df[feature_cols].values
    y = df['rating_j'].values
    return X, y, feature_cols

def train_model(X, y, feature_cols):
    model = HistGradientBoostingRegressor(
        max_iter=200,
        learning_rate=0.05, #faster for me to test
        max_depth=8,
        min_samples_leaf=20,
        l2_regularization=1.0,
        random_state=42
    )
    model.fit(X, y)
    return model

def save_model(model, feature_cols):
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    with open(FEATURES_FILE, 'w') as f:
        json.dump(feature_cols, f, indent=2)

if __name__ == "__main__":
    df = load_training_data()
    X, y, feature_cols = prepare_features(df)
    # Train on the entire dataset
    model = train_model(X, y, feature_cols)
    save_model(model, feature_cols)