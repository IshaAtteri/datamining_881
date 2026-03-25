import pandas as pd
from sentence_transformers import SentenceTransformer
from preprocessing import clean_plot, get_genre, pre_director, clean_cast
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_excel('C:\\Users\\ishaa\\OneDrive\\Documents\\MSU\\Spring 2026\\Data mining\\Project\\updated_data.xlsx', engine='openpyxl')

df = df.dropna(subset=['Genre', 'Plot'])

df['Processed_Plot'] = df['Plot'].apply(clean_plot)

df['Pre_genre'] = df[['Genre', 'Title']].apply(get_genre, axis=1)

df['Pre_director'] = df['Director'].apply(pre_director)
df['Pre_cast'] = df['Cast'].apply(clean_cast)

df.to_excel('C:\\Users\\ishaa\\OneDrive\\Documents\\MSU\\Spring 2026\\Data mining\\Project\\preprocessed_data.xlsx', index=False)