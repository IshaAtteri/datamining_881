# F0 = Plot Similarity
# F1 = Year Similarity
# F2 = Genre Similarity
# F3 = Director Match
# F4 = Cast Similarity

import os
import json
import warnings
import numpy as np
import pandas as pd
import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

warnings.filterwarnings("ignore")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODEL_DIR = os.path.join(BASE_DIR, "data", "processed", "models-item-item-05milpairs-150coraters")
OUT_DIR = os.path.join(BASE_DIR, "data", "processed", "report_figures")
os.makedirs(OUT_DIR, exist_ok=True)

WEIGHTS_PATH = os.path.join(BASE_DIR, "pipeline_code", "6_serving", "weights.json")
with open(WEIGHTS_PATH) as f:
    ALGO_WEIGHTS = json.load(f)

def save_figure(fig, filename):
    fig.tight_layout()
    png_path = os.path.join(OUT_DIR, filename)
    fig.savefig(png_path, dpi=300)
    plt.close(fig)
    print(f"  Saved -> {png_path}")

def calc_metrics(actual, pred): # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html
    return {
        "pearson": pearsonr(pred, actual)[0],
        "spearman": spearmanr(pred, actual)[0],
        "rmse": np.sqrt(mean_squared_error(actual, pred))
    }

def add_stats_box(ax, data):
    stats_text = f"μ={data.mean():.3f}\nσ={data.std():.3f}\n[{data.min():.3f}, {data.max():.3f}]"
    ax.text(0.97, 0.95, stats_text, transform=ax.transAxes, fontsize=9, 
            va="top", ha="right", bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
    # https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.text.html

def add_metrics_box(ax, metrics):
    text = f"Pearson: {metrics['pearson']:.4f}\nSpearman: {metrics['spearman']:.4f}\nRMSE: {metrics['rmse']:.4f}"
    ax.text(0.03, 0.96, text, transform=ax.transAxes, fontsize=9, 
            va="top", bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

train_df = pd.read_parquet(os.path.join(MODEL_DIR, "item_item_training_data.parquet"))
eval_df = pd.read_parquet(os.path.join(MODEL_DIR, "item_item_eval_data.parquet"))
model = joblib.load(os.path.join(MODEL_DIR, "item_item_recommender.pkl"))

with open(os.path.join(MODEL_DIR, "feature_columns.json")) as f:
    feature_cols = json.load(f)

print(f"Train samples: {len(train_df):,}\nEval samples:  {len(eval_df):,}")

# Generate Raw Scores
for df in [train_df, eval_df]:
    df['model_raw'] = model.predict(df[feature_cols].values)
    df['algo_raw'] = sum(df[feature] * weight for feature, weight in ALGO_WEIGHTS.items())

scalers = {
    'gt': MinMaxScaler().fit(train_df[['collab_similarity']]),
    'model': MinMaxScaler().fit(train_df[['model_raw']]),
    'algo': MinMaxScaler().fit(train_df[['algo_raw']])
}

for df in [train_df, eval_df]:
    df['gt_norm'] = scalers['gt'].transform(df[['collab_similarity']])
    df['model_norm'] = scalers['model'].transform(df[['model_raw']])
    df['algo_norm'] = scalers['algo'].transform(df[['algo_raw']])

metrics = {
    'train': {
        'model': calc_metrics(train_df['gt_norm'], train_df['model_norm']),
        'algo': calc_metrics(train_df['gt_norm'], train_df['algo_norm'])
    },
    'eval': {
        'model': calc_metrics(eval_df['gt_norm'], eval_df['model_norm']),
        'algo': calc_metrics(eval_df['gt_norm'], eval_df['algo_norm'])
    }
}

print("Generating graphs")

# FIG 1: Ground Truth Distribution
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
fig.suptitle("Fig 1 - Collaborative Similarity Distribution (Ground Truth)", fontweight="bold")

for ax, df, title in zip(axes, [train_df, eval_df], ["Train (60%)", "Eval (40%)"]):
    data = df["collab_similarity"].values
    ax.hist(data, bins=80, alpha=0.7)
    ax.axvline(data.mean(), color="black", linestyle="--", label=f"mean={data.mean():.4f}")
    ax.set_title(title)
    ax.set_xlabel("Centered Cosine Similarity")
    ax.legend()
    add_stats_box(ax, data)
    ax.grid(True, axis="y", alpha=0.5)
    
save_figure(fig, "fig1_collab_distribution.png")

# FIG 2: Score Distributions
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Fig 2 - Predicted Score Distributions (Normalized)", fontweight="bold")

configs = [
    (axes[0, 0], train_df, "algo_norm", "Train (60%) - Algorithm"),
    (axes[0, 1], train_df, "model_norm", "Train (60%) - XGBoost"),
    (axes[1, 0], eval_df, "algo_norm", "Eval (40%) - Algorithm"),
    (axes[1, 1], eval_df, "model_norm", "Eval (40%) - XGBoost")
]

for ax, df, col, title in configs:
    ax.hist(df['gt_norm'], bins=50, alpha=0.5, label="Ground truth", density=True)
    ax.hist(df[col], bins=50, alpha=0.5, label="Prediction", density=True)
    ax.set_title(title)
    ax.set_xlabel("Normalized Score [0, 1]")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.5)
    
save_figure(fig, "fig2_score_distributions.png")

# FIG 3 & 4: Scatter Plots (Model & Algorithm)
for fnum, pred_col, pred_name in [("fig3", "model", "XGBoost"), ("fig4", "algo", "Algorithm")]:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f"Fig {fnum[-1]} - {pred_name} Predictions vs Ground Truth (Normalized)", fontweight="bold")
    
    for ax, df, split_key, title in zip(axes, [train_df, eval_df], ['train', 'eval'], ["Train", "Eval"]):
        ax.scatter(df['gt_norm'], df[f'{pred_col}_norm'], alpha=0.15, s=6)
        ax.plot([0, 1], [0, 1], color="black", linestyle="--", label="Perfect Agreement")
        ax.set_title(title)
        ax.set_xlabel("Ground Truth (Normalized)")
        ax.set_ylabel("Prediction (Normalized)")
        ax.legend()
        add_metrics_box(ax, metrics[split_key][pred_col])
        ax.grid(True, alpha=0.5)
        
    save_figure(fig, f"{fnum}_{pred_col}_scatter.png")

# FIG 5: Correlation Bar Charts
fig, axes = plt.subplots(1, 2, figsize=(11, 5))
fig.suptitle("Fig 5 - Pearson & Spearman Correlations", fontweight="bold")
x = np.arange(2)
width = 0.35

for ax, split_key, title in zip(axes, ['train', 'eval'], ["Train (60%)", "Eval (40%)"]):
    algo_vals = [metrics[split_key]['algo']['pearson'], metrics[split_key]['algo']['spearman']]
    model_vals = [metrics[split_key]['model']['pearson'], metrics[split_key]['model']['spearman']]
    
    ax.bar(x - width/2, algo_vals, width, label="Algorithm")
    ax.bar(x + width/2, model_vals, width, label="XGBoost")
    
    for container in ax.containers:
        ax.bar_label(container, fmt='%.4f', padding=3, fontsize=9)
        
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(["Pearson r", "Spearman ρ"])
    ax.set_ylim(0, max(max(algo_vals), max(model_vals)) * 1.3)
    ax.legend()
    ax.grid(True, axis="y", alpha=0.5)
    
save_figure(fig, "fig5_correlation_bars.png")

# FIG 6: Feature Importance
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
fig.suptitle("Fig 6 - XGBoost Feature Importance", fontweight="bold")

bst = model.get_booster()
for ax, imp_type, title in zip(axes, ["gain", "weight", "cover"], ["Gain (Quality)", "Weight (Frequency)", "Cover (Reach)"]):
    scores = bst.get_score(importance_type=imp_type)
    total = sum(scores.values())
    # https://xgboost.readthedocs.io/en/stable/python/python_api.html
    # Normalize and sort
    norm_scores = {k: v / total for k, v in sorted(scores.items(), key=lambda item: item[1])}
    features = list(norm_scores.keys())
    labels = [f.replace("_", " ").title() for f in features]
    values = list(norm_scores.values())
    
    bars = ax.barh(labels, values)
    ax.bar_label(bars, fmt='%.3f', padding=3, fontsize=9)
    ax.set_title(title)
    ax.set_xlabel("Normalized Importance")
    ax.set_xlim(0, max(values) * 1.2)
    
save_figure(fig, "fig6_feature_importance.png")

# FIG 7: Generalization
fig, axes = plt.subplots(1, 3, figsize=(13, 5))
fig.suptitle("Fig 7 - Train vs Eval Generalization (Overfitting Check)", fontweight="bold")
x = np.arange(2)

for ax, metric_key, title in zip(axes, ["pearson", "spearman", "rmse"], ["Pearson r", "Spearman ρ", "RMSE"]):
    algo_vals = [metrics['train']['algo'][metric_key], metrics['eval']['algo'][metric_key]]
    model_vals = [metrics['train']['model'][metric_key], metrics['eval']['model'][metric_key]]
    
    ax.bar(x - width/2, algo_vals, width, label="Algorithm")
    ax.bar(x + width/2, model_vals, width, label="XGBoost")
    
    for container in ax.containers:
        ax.bar_label(container, fmt='%.4f', padding=3, fontsize=9)
        
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(["Train", "Eval"])
    ax.legend()
    ax.grid(True, axis="y", alpha=0.5)
    
save_figure(fig, "fig7_generalization.png")

# FIG 8: Recall@K
def recall_at_k(df, pred_col, gt_col='gt_norm', k_vals=None, threshold=0.5):
    if k_vals is None:
        k_vals = [5, 10, 20, 50, 100]
    # Sort by predicted score descending, check how many true positives land in top-K
    sorted_df = df[[gt_col, pred_col]].sort_values(pred_col, ascending=False).reset_index(drop=True)
    relevant = (sorted_df[gt_col] >= threshold).sum()
    if relevant == 0:
        return {k: 0.0 for k in k_vals}
    return {
        k: (sorted_df[gt_col][:k] >= threshold).sum() / relevant
        for k in k_vals
    }

K_VALS = [5, 10, 20, 50, 100]
GT_THRESHOLD = 0.5  # normalized gt_norm threshold for "relevant"

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Fig 8 - Recall@K (gt_norm threshold=0.5)", fontweight="bold")

for ax, df, split_key, title in zip(axes, [train_df, eval_df], ['train', 'eval'], ["Train (60%)", "Eval (40%)"]):
    model_recalls = recall_at_k(df, 'model_norm', k_vals=K_VALS, threshold=GT_THRESHOLD)
    algo_recalls  = recall_at_k(df, 'algo_norm',  k_vals=K_VALS, threshold=GT_THRESHOLD)

    ax.plot(K_VALS, [model_recalls[k] for k in K_VALS], marker='o', label="XGBoost")
    ax.plot(K_VALS, [algo_recalls[k]  for k in K_VALS], marker='s', label="Algorithm")
    ax.set_title(title)
    ax.set_xlabel("K")
    ax.set_ylabel("Recall@K")
    ax.set_xticks(K_VALS)
    ax.legend()
    ax.grid(True, alpha=0.5)

save_figure(fig, "fig8_recall_at_k.png")

print("Finished")