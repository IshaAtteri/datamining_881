# uvicorn pipeline_code.6_serving.model_server:app --reload --host 0.0.0.0 --port 8000
# http://localhost:8000/docs
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np
import pandas as pd
import json
from pathlib import Path
import joblib
import re

app = FastAPI(title="Model Endpoint")

# needed to add this to connect this code to frontend stuff - a
################
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # current Next.js frontend url -- will need to change when switching to vercel
    allow_credentials=True,
    allow_methods=["*"],                      # allow POST, GET, OPTIONS, etc
    allow_headers=["*"],
)
#####################

model = None
feature_cols = None
movies_df = None
embeddings = None
embedding_norms = None
slug_to_idx = None
weights = None
precomputed_algorithm = None
precomputed_model = None

MODELS_FOLDER = "models-item-item-05milpairs-150coraters"

@app.on_event("startup")
def load_model_and_data():
    global model, feature_cols, movies_df, embeddings, embedding_norms, slug_to_idx, weights, precomputed_algorithm, precomputed_model
    base_dir = Path(__file__).parent.parent.parent

    # load feature weights
    weights_path = base_dir / "pipeline_code" / "6_serving" / "weights.json"
    if weights_path.exists():
        try:
            with open(weights_path) as f:
                weights = json.load(f)
            if abs(sum(weights.values()) - 1.0) > 0.01:
                print('something is wrong. using default')
                weights = {"plot_sim":0.3,"year_sim":0.15,"genre_sim":0.2,"director_match":0.15,"cast_sim":0.2}
        except:
            print('something is wrong. using default')
            weights = {"plot_sim":0.3,"year_sim":0.15,"genre_sim":0.2,"director_match":0.15,"cast_sim":0.2}
    else:
        print('something is wrong. using default')
        weights = {"plot_sim":0.3,"year_sim":0.15,"genre_sim":0.2,"director_match":0.15,"cast_sim":0.2}

    # load trained model if available
    model_path = base_dir / "data" / "processed" / MODELS_FOLDER / "item_item_recommender.pkl"
    print(model_path)
    feature_path = base_dir / "data" / "processed" / MODELS_FOLDER / "feature_columns.json"
    if model_path.exists() and feature_path.exists():
        model = joblib.load(model_path)
        with open(feature_path) as f:
            feature_cols = json.load(f)
        print(f"Loaded item-to-item model with features: {feature_cols}")
    else:
        print(f"Model not found at {model_path}. /predict/model endpoint will be unavailable.")

    # load embeddings and metadata
    embeddings_path = base_dir / "data" / "processed" / "xplot_embeddings_full_data.npy"

    try:
        combined_data = np.load(embeddings_path, allow_pickle=True).item()
        embeddings = combined_data['embeddings']
        embedding_norms = np.linalg.norm(embeddings, axis=1)
        metadata = combined_data['metadata']
        movies_df = pd.DataFrame(metadata)
        slug_to_idx = {movie['Slug']: i for i, movie in enumerate(metadata)}
        print(f"Loaded {len(movies_df)} movies with {embeddings.shape[1]}-dim embeddings")
    except FileNotFoundError:
        embeddings = None
        embedding_norms = None
        movies_df = None
        slug_to_idx = None
        print(f"Embeddings file not found: {embeddings_path}. Server will start but scoring endpoints will fail until data is available.")

    # load precomputed recommendations
    precomputed_dir = base_dir / "data" / "processed" / "precomputed_recommendations"
    algo_path = precomputed_dir / "algorithm.json"
    model_path_pre = precomputed_dir / "model.json"

    if algo_path.exists():
        with open(algo_path) as f:
            precomputed_algorithm = json.load(f)
        print(f"Loaded precomputed algorithm recommendations for {len(precomputed_algorithm)} movies")
    else:
        print(f"No precomputed algorithm data found at {algo_path}. Run precompute.py first.")

    if model_path_pre.exists():
        with open(model_path_pre) as f:
            precomputed_model = json.load(f)
        print(f"Loaded precomputed model recommendations for {len(precomputed_model)} movies")
    else:
        print(f"No precomputed model data found at {model_path_pre}. Run precompute.py first.")

def extract_year(date_str):
    if not date_str:
        return 0
    match = re.search(r'\b(19|20)\d{2}\b', str(date_str)) #https://stackoverflow.com/questions/4709652/python-regex-to-match-dates
    return int(match.group(0)) if match else 0

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)

def get_cast(movie):
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
    return [] #can make this more efficient prolly

# compares two movies and turns their similarity into numbers the system can score
# returns a dictionary of similarity scores (features) between them
def compute_pairwise_features(query_movie, candidate_movie, query_emb, candidate_emb):
    features = {}
    features['plot_sim'] = float(np.dot(query_emb, candidate_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(candidate_emb)))

    year_q = extract_year(query_movie.get('Release Date'))
    year_c = extract_year(candidate_movie.get('Release Date'))
    features['year_sim'] = max(0.0, 1.0 - abs(year_q - year_c)/50.0)

    genre_q = set(str(query_movie.get('Genre','')).lower().split())
    genre_c = set(str(candidate_movie.get('Genre','')).lower().split())
    features['genre_sim'] = jaccard_similarity(genre_q, genre_c)

    dir_q = str(query_movie.get('Director','')).lower()
    dir_c = str(candidate_movie.get('Director','')).lower()
    features['director_match'] = 1.0 if dir_q and dir_q == dir_c else 0.0

    cast_q = get_cast(query_movie)
    cast_c = get_cast(candidate_movie)
    features['cast_sim'] = jaccard_similarity(set(cast_q), set(cast_c))

    return features

class AlgorithmRequest(BaseModel):
    query_slugs: List[str]  # one or more movies; algorithm averages scores across all

class ModelRequest(BaseModel):
    query_slug: str

class ScoreResponse(BaseModel):
    slug: str
    score: float

def score_all_against(query_slug: str, use_model: bool) -> List[dict]:
    if movies_df is None or embeddings is None:
        raise HTTPException(status_code=503, detail="Movie data not loaded")
    if query_slug not in slug_to_idx:
        raise HTTPException(status_code=404, detail=f"Query movie not found: {query_slug}")
    if use_model and (model is None or feature_cols is None):
        raise HTTPException(status_code=503, detail="Trained model not available")
    query_idx = slug_to_idx[query_slug]
    query_movie = movies_df.iloc[query_idx].to_dict()
    query_emb = embeddings[query_idx]

    scores = []
    for i, row in movies_df.iterrows():
        slug = row['Slug']
        if slug == query_slug:
            continue
        cand_emb = embeddings[i]
        features = compute_pairwise_features(query_movie, row.to_dict(), query_emb, cand_emb)
        if use_model:
            X = np.array([[features[col] for col in feature_cols]])
            score = float(model.predict(X)[0])
        else:
            score = sum(weights[k] * features[k] for k in weights)
        scores.append({"slug": slug, "score": score})

    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores

@app.post("/predict/model", response_model=List[ScoreResponse])
def predict_model(request: ModelRequest):
    if precomputed_model is not None:
        results = precomputed_model.get(request.query_slug)
        if results is None:
            raise HTTPException(status_code=404, detail=f"Query movie not found: {request.query_slug}")
        return results[:10]
    # fallback: compute live
    return score_all_against(request.query_slug, use_model=True)[:10]

@app.post("/predict/algorithm", response_model=List[ScoreResponse])
def predict_algorithm(request: AlgorithmRequest):
    query_slugs = list(dict.fromkeys(request.query_slugs))  # deduplicate andd preserve order

    if len(query_slugs) == 1:
        # single movie  use precomputed if available
        slug = query_slugs[0]
        if precomputed_algorithm is not None:
            results = precomputed_algorithm.get(slug)
            if results is None:
                raise HTTPException(status_code=404, detail=f"Query movie not found: {slug}")
            return results[:10]
        return score_all_against(slug, use_model=False)[:10]

    # multiple movies: compute live and average scores across all query movies
    if movies_df is None or embeddings is None:
        raise HTTPException(status_code=503, detail="Movie data not loaded")

    slug_scores: dict[str, list[float]] = {}
    for query_slug in query_slugs:
        if query_slug not in slug_to_idx:
            raise HTTPException(status_code=404, detail=f"Query movie not found: {query_slug}")
        query_idx = slug_to_idx[query_slug]
        query_movie = movies_df.iloc[query_idx].to_dict()
        query_emb = embeddings[query_idx]
        for i, row in movies_df.iterrows():
            slug = row['Slug']
            if slug in query_slugs:
                continue
            cand_emb = embeddings[i]
            features = compute_pairwise_features(query_movie, row.to_dict(), query_emb, cand_emb)
            score = sum(weights[k] * features[k] for k in weights)
            slug_scores.setdefault(slug, []).append(score)

    combined = [{"slug": s, "score": sum(v) / len(v)} for s, v in slug_scores.items()]
    combined.sort(key=lambda x: x["score"], reverse=True)
    return combined[:10]

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "precomputed_algorithm": precomputed_algorithm is not None,
        "precomputed_model": precomputed_model is not None,
        "weights": weights,
    }

@app.get("/weights")
def get_weights():
    return weights

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)