import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

import pandas as pd
import numpy as np

# Load dataset
df = pd.read_excel(r"C:\Users\ishaa\OneDrive\Documents\MSU\Spring 2026\Data mining\Project\preprocessed_data.xlsx", engine='openpyxl')

print(df.head(2))

plot_embeddings = np.load(r"C:\Users\ishaa\OneDrive\Documents\MSU\Spring 2026\Data mining\Project\plot_embeddings.npy")

print(plot_embeddings.shape)  # (N, D)
print(df.shape)  # (N, ...)

sim_matrix = cosine_similarity(plot_embeddings)

print(sim_matrix.shape)  # (N, N)

M = 3  # candidate size

top_M_indices = []

for i in range(sim_matrix.shape[0]):
    sims = sim_matrix[i]

    # get indices of top M (excluding itself)
    # indices = np.argsort(sims)[::-1][1:M+1]
    indices = np.argsort(sims)[1:M+1]

    print(indices)
    # top_M_indices.append(indices)

    movie_title = df.iloc[i]["Title"]
    similar_titles = df.iloc[indices[:2]]["Title"].tolist()

    print(f"\nMovie: {movie_title}")
    print("Top 2 similar:", similar_titles)
    print("Scores:", sims[indices])

    # print(f"Movie {i} similar movies scores: {sims[indices]}")

    # print( df.iloc[i][['Title']], "is similar to: ", df.iloc[indices[:2]][['Title']])

    # 

