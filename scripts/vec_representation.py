import pandas as pd
from sentence_transformers import SentenceTransformer
from preprocessing import clean_plot, get_genre
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_excel('C:\\Users\\ishaa\\OneDrive\\Documents\\MSU\\Spring 2026\\Data mining\\Project\\updated_data.xlsx', engine='openpyxl')

print(len(df))

df = df.dropna(subset=['Genre', 'Plot'])

print(len(df))

# df = df[:2]

df['Processed_Plot'] = df['Plot'].apply(clean_plot)

df['Genre'] = df[['Genre', 'Title']].apply(get_genre, axis=1)

df.to_excel('C:\\Users\\ishaa\\OneDrive\\Documents\\MSU\\Spring 2026\\Data mining\\Project\\preprocessed_data.xlsx', index=False)

print(df.columns)