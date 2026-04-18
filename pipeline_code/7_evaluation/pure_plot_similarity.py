import pandas as pd, numpy as np, joblib, matplotlib.pyplot as plt, os
from sklearn.metrics.pairwise import cosine_similarity
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODELS = os.path.join(BASE, "data", "processed", "models-item-item-2milpairs-100coraters")
EMB_DATA = np.load(os.path.join(BASE, "data", "processed", "xplot_embeddings_full_data.npy"), allow_pickle=True).item()
MODEL = joblib.load(os.path.join(MODELS, "item_item_recommender.pkl"))

embs = EMB_DATA['embeddings']
df = pd.DataFrame(EMB_DATA['metadata']).reset_index()
feats = ['plot_sim', 'year_sim', 'genre_sim', 'director_match', 'cast_sim']
weights = [0.3, 0.15, 0.2, 0.15, 0.2]

N_QUERIES, TOP_K = 20, 5
results = {'algo': [], 'model': []}

for idx in np.random.choice(df.index, N_QUERIES):
    cands = np.random.choice(df.index, 500)
    query_emb = embs[idx].reshape(1, -1)
    
    sims = cosine_similarity(query_emb, embs[cands])[0]
    
    algo_scores = sims 
    top_algo_idx = cands[np.argsort(algo_scores)[-TOP_K:]]
    
    X = np.zeros((len(cands), len(feats)))
    X[:, 0] = sims
    model_scores = MODEL.predict(X)
    top_model_idx = cands[np.argsort(model_scores)[-TOP_K:]]
    
    results['algo'].append(np.mean(cosine_similarity(query_emb, embs[top_algo_idx])))
    results['model'].append(np.mean(cosine_similarity(query_emb, embs[top_model_idx])))

plt.figure(figsize=(6, 4))
means = [np.mean(results['algo']), np.mean(results['model'])]
plt.bar(['Heuristic Algorithm', 'XGBoost Model'], means, color=['orange', 'green'])
plt.ylabel('Average Plot Cosine Similarit')
plt.title(f'Semantic Cohesion (Top {TOP_K} Recommendations)')
for i, v in enumerate(means): plt.text(i, v + 0.01, f'{v:.3f}', ha='center', fontweight='bold')
plt.ylim(0, 1.0)
plt.show()

print(f"Algorithm Plot Sim: {means[0]:.4f}")
print(f"XGBoost Plot Sim:   {means[1]:.4f}")
