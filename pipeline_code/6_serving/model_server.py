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
import threading

app = FastAPI(title="Model Endpoint")

# needed to add this to connect this code to frontend stuff - a
################
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all
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
parsed_metadata = None

MODELS_FOLDER = "models-item-item-05milpairs-150coraters"

def _load_model_and_data():
    global model, feature_cols, movies_df, embeddings, embedding_norms, slug_to_idx, weights, precomputed_algorithm, precomputed_model, parsed_metadata
    base_dir = Path(__file__).parent

    # load feature weights
    weights_path = base_dir / "weights.json"
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
    model_path = base_dir / MODELS_FOLDER / "item_item_recommender.pkl"
    print(model_path)
    feature_path = base_dir / MODELS_FOLDER / "feature_columns.json"
    if model_path.exists() and feature_path.exists():
        model = joblib.load(model_path)
        with open(feature_path) as f:
            feature_cols = json.load(f)
        print(f"Loaded item-to-item model with features: {feature_cols}")
    else:
        print(f"Model not found at {model_path}. /predict/model endpoint will be unavailable.")

    # load embeddings and metadata
    embeddings_path = base_dir / "xplot_embeddings_full_data.npy"

    try:
        combined_data = np.load(embeddings_path, allow_pickle=True).item()
        embeddings = combined_data['embeddings']
        embedding_norms = np.linalg.norm(embeddings, axis=1)
        metadata = combined_data['metadata']
        movies_df = pd.DataFrame(metadata)
        slug_to_idx = {movie['Slug']: i for i, movie in enumerate(metadata)}
        print(f"Loaded {len(movies_df)} movies with {embeddings.shape[1]}-dim embeddings")



        # pre-parse metadata for fast feature computation
        parsed_metadata = []
        for movie in metadata:
            parsed_metadata.append({
                'slug': movie['Slug'],
                'year': extract_year(movie.get('Release Date')),
                'genres': set(str(movie.get('Genre', '')).lower().split()),
                'director': str(movie.get('Director', '')).lower(),
                'cast': set(get_cast(movie))
            })
        print(f"Pre-parsed metadata for {len(parsed_metadata)} movies")
    except FileNotFoundError:
        embeddings = None
        embedding_norms = None
        movies_df = None
        slug_to_idx = None
        parsed_metadata = None
        print(f"Embeddings file not found: {embeddings_path}. Server will start but scoring endpoints will fail until data is available.")

    # load precomputed recommendations
    precomputed_dir = base_dir / "precomputed_recomendations"
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

@app.on_event("startup")
def startup_event():
    threading.Thread(target=_load_model_and_data, daemon=True).start()

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

def compute_pairwise_features_fast(query_parsed, candidate_parsed, query_emb, candidate_emb, query_norm, candidate_norm):
    features = {}
    features['plot_sim'] = float(np.dot(query_emb, candidate_emb) / (query_norm * candidate_norm))
    features['year_sim'] = max(0.0, 1.0 - abs(query_parsed['year'] - candidate_parsed['year'])/50.0)
    features['genre_sim'] = jaccard_similarity(query_parsed['genres'], candidate_parsed['genres'])
    features['director_match'] = 1.0 if query_parsed['director'] and query_parsed['director'] == candidate_parsed['director'] else 0.0
    features['cast_sim'] = jaccard_similarity(query_parsed['cast'], candidate_parsed['cast'])
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
    query_emb = embeddings[query_idx]
    query_norm = embedding_norms[query_idx]
    query_parsed = parsed_metadata[query_idx] if parsed_metadata else None

    scores = []
    n_movies = len(parsed_metadata) if parsed_metadata else len(movies_df)

    for i in range(n_movies):
        if i == query_idx:
            continue

        slug = parsed_metadata[i]['slug'] if parsed_metadata else movies_df.iloc[i]['Slug']
        cand_emb = embeddings[i]
        cand_norm = embedding_norms[i]

        if parsed_metadata and query_parsed:
            features = compute_pairwise_features_fast(query_parsed, parsed_metadata[i], query_emb, cand_emb, query_norm, cand_norm)
        else:
            cand_movie = movies_df.iloc[i].to_dict()
            features = compute_pairwise_features(movies_df.iloc[query_idx].to_dict(), cand_movie, query_emb, cand_emb)

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
    query_slugs = list(dict.fromkeys(request.query_slugs))  # deduplicate and preserve order

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

    query_indices = []
    for query_slug in query_slugs:
        if query_slug not in slug_to_idx:
            raise HTTPException(status_code=404, detail=f"Query movie not found: {query_slug}")
        query_indices.append(slug_to_idx[query_slug])

    query_set = set(query_indices)
    n_movies = len(parsed_metadata) if parsed_metadata else len(movies_df)

    slug_scores: dict[str, list[float]] = {}

    #or each candidate movie, compute scores against all query movies.
    for i in range(n_movies):
        if i in query_set:
            continue

        cand_slug = parsed_metadata[i]['slug'] if parsed_metadata else movies_df.iloc[i]['Slug']
        cand_emb = embeddings[i]
        cand_norm = embedding_norms[i]

        scores_for_candidate = []
        for query_idx in query_indices:
            query_emb = embeddings[query_idx]
            query_norm = embedding_norms[query_idx]

            if parsed_metadata:
                features = compute_pairwise_features_fast(parsed_metadata[query_idx], parsed_metadata[i], query_emb, cand_emb, query_norm, cand_norm)
            else:
                query_movie = movies_df.iloc[query_idx].to_dict()
                cand_movie = movies_df.iloc[i].to_dict()
                features = compute_pairwise_features(query_movie, cand_movie, query_emb, cand_emb)

            score = sum(weights[k] * features[k] for k in weights)
            scores_for_candidate.append(score)

        slug_scores[cand_slug] = scores_for_candidate

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
