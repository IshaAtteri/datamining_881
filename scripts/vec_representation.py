import pandas as pd
from sentence_transformers import SentenceTransformer
from preprocessing import clean_plot, get_genre, pre_director, clean_cast
import numpy as np

df = pd.read_excel('C:\\Users\\ishaa\\OneDrive\\Documents\\MSU\\Spring 2026\\Data mining\\Project\\updated_datav2.xlsx', engine='openpyxl')
df = df.dropna(subset=['Plot'])

df = df[:100]

print(len(df))

df['Processed_Plot'] = df['Plot'].apply(clean_plot)

df['Pre_genre'] = df[['Genre', 'Title']].apply(get_genre, axis=1)

df['Pre_director'] = df['Director'].apply(pre_director)
df['Pre_cast'] = df['Cast'].apply(clean_cast)


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Generate one embedding per movie plot
plot_embeddings = model.encode(
    df["Processed_Plot"].tolist(),
    show_progress_bar=True,
    convert_to_numpy=True
)


np.save(r"C:\Users\ishaa\OneDrive\Documents\MSU\Spring 2026\Data mining\Project\plot_embeddings.npy",plot_embeddings)

df.to_excel('C:\\Users\\ishaa\\OneDrive\\Documents\\MSU\\Spring 2026\\Data mining\\Project\\preprocessed_data.xlsx', index=False)