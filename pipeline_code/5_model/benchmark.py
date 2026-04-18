import os, warnings, itertools
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from scipy.stats import pearsonr, spearmanr
from xgboost import XGBRegressor
from joblib import Parallel, delayed
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

warnings.filterwarnings("ignore")
from helper_functions import FEATURE_COLS, BASE_DIR, load_netflix_ratings, load_movie_data, compute_pairwise_features

MASTER_PARQUET = os.path.join(BASE_DIR, "data", "processed", "data_config_sweep", "master_pairs.parquet")
os.makedirs(os.path.dirname(MASTER_PARQUET), exist_ok=True)

MIN_CO_OPTIONS = [20, 75, 150]
MAX_PAIRS_OPS  = [500_000, 2_000_000, 5_000_000]
XGB_GRID = [
    dict(n_estimators=200, learning_rate=lr, max_depth=d, subsample=0.8, colsample_bytree=0.8)
    for lr, d in itertools.product([0.05, 0.10], [4, 6])
]
SEED = 42


def build_master():
    ratings_df = load_netflix_ratings()
    movies_df, embeddings, slug_to_idx = load_movie_data()
    valid = set(movies_df["Slug"])
    ratings_df = ratings_df[ratings_df["tt_id"].isin(valid)]
    movie_dict = {row["Slug"]: {"metadata": row.to_dict(), "embedding": embeddings[slug_to_idx[row["Slug"]]]}
                  for _, row in movies_df.iterrows() if row["Slug"] in slug_to_idx}

    df = ratings_df.copy()
    uc, mc = df["customer_id"].astype("category"), df["tt_id"].astype("category")
    slugs = list(mc.cat.categories)
    means = df.groupby("customer_id")["rating"].transform("mean").values.astype(np.float32)
    mat = csr_matrix((df["rating"].values.astype(np.float32) - means,
                      (mc.cat.codes.values, uc.cat.codes.values)),
                     shape=(len(slugs), len(uc.cat.categories)))
    co, sim = ((mat != 0).astype(np.float32) @ (mat != 0).T.astype(np.float32)).toarray(), cosine_similarity(mat)

    rows = []
    for i in tqdm(range(len(slugs))):
        for j in range(i + 1, len(slugs)):
            if co[i, j] >= 10:
                a, b = sorted([slugs[i], slugs[j]])
                if a in movie_dict and b in movie_dict:
                    feats = compute_pairwise_features(movie_dict[a]["metadata"], movie_dict[b]["metadata"],
                                                      movie_dict[a]["embedding"], movie_dict[b]["embedding"])
                    rows.append({"movie_a": a, "movie_b": b, "collab_similarity": float(sim[i, j]),
                                 "co_raters": int(co[i, j]), **feats})

    df_out = pd.DataFrame(rows)
    if len(df_out) > 5_000_000:
        df_out = df_out.sample(5_000_000, random_state=SEED)
    df_out.to_parquet(MASTER_PARQUET, index=False)
    return df_out

def run_config(min_co, max_pairs, xgb_params):
    df = pd.read_parquet(MASTER_PARQUET)
    df = df[df["co_raters"] >= min_co]
    if len(df) < 200: return None
    if len(df) > max_pairs: df = df.sample(max_pairs, random_state=SEED)
    df = df.sample(frac=1, random_state=SEED)
    cut = int(len(df) * 0.6)
    tr, ev = df.iloc[:cut].sample(frac=0.05, random_state=SEED), df.iloc[cut:]

    model = XGBRegressor(tree_method="hist", random_state=SEED, verbosity=0, **xgb_params)
    model.fit(tr[FEATURE_COLS], tr["collab_similarity"])
    pred = model.predict(ev[FEATURE_COLS])

    y, p = ev["collab_similarity"].values, pred
    sg = MinMaxScaler().fit_transform(y.reshape(-1,1)).ravel()
    sp = MinMaxScaler().fit_transform(p.reshape(-1,1)).ravel()
    rmse = float(np.sqrt(mean_squared_error(sg, sp)))
    r20 = float((sg[np.argsort(sp)[::-1][:20]] >= 0.5).sum() / max((sg >= 0.5).sum(), 1))
    pe, sr = float(pearsonr(sg, sp)[0]), float(spearmanr(sg, sp)[0])
    sc = 0.35*pe + 0.35*sr - 0.20*rmse + 0.10*r20
    return dict(min_co=min_co, max_pairs=max_pairs, score=sc, pearson=pe, spearman=sr, rmse=rmse, params=xgb_params)


def main():
    tasks = [(mc, mp, xp) for mc, mp in itertools.product(MIN_CO_OPTIONS, MAX_PAIRS_OPS) for xp in XGB_GRID]
    results = sorted([r for r in Parallel(n_jobs=-1)(delayed(run_config)(*t) for t in tasks) if r],
                     key=lambda x: x["score"], reverse=True)
    print(f"\n{'Rank':<5} {'Score':>7} {'Pearson':>8} {'Spearman':>9} {'RMSE':>7} {'co≥':>5} {'maxP':>8}")
    for i, r in enumerate(results[:10], 1):
        print(f"{i:<5} {r['score']:>7.4f} {r['pearson']:>8.4f} {r['spearman']:>9.4f} "
              f"{r['rmse']:>7.4f} {r['min_co']:>5} {r['max_pairs']//1_000_000:>7}M")
    best = results[0]
    print(f"\nWinner: co≥{best['min_co']}, max_pairs={best['max_pairs']:,}, score={best['score']:.4f}")

if __name__ == "__main__":
    main()