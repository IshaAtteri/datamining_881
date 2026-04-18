import pandas as pd
import string, re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sentence_transformers import SentenceTransformer
import pkg_resources

nltk.download('wordnet')
nltk.download('punkt_tab')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()
_PUNCT_TABLE = str.maketrans('', '', string.punctuation)

def clean_plot(text):
    text = text.lower()
    text = text.translate(_PUNCT_TABLE)
    text = re.sub(r'\W', ' ', text)
    text = ([word for word in word_tokenize(text) if word not in stop_words])
    text = [stemmer.stem(word) for word in text]
    text = ' '.join(lemmatizer.lemmatize(word) for word in text)
    return text

def get_genre(row):
    if pd.isna(row['Genre']):
        return ""
    movie = row['Title']
    text = row['Genre']
    text = text.replace(movie, "")
    text = text.split(".")[0]
    text = text.lower()
    match = re.search(r'is a ((?:\S+\s+){4}\S+)', text)
    if match:
        words = match.group(1).split()
        text = ' '.join(words[1:])
    text = text.translate(_PUNCT_TABLE)
    text = re.sub(r'\W', ' ', text)  # Remove special characters
    text = ([word for word in word_tokenize(text) if word not in stop_words])
    text = ' '.join(text)

    return text

def pre_director(text):
    if pd.isna(text) or not text:
        return ""
    text = text.lower().strip()
    return text

def clean_cast(text):
    print(f"Original cast: {text}")
    if pd.isna(text) or not text:
        return []
    text = text.lower()
    cast_list = [actor.strip() for actor in text.split(",")]
    cast_list = [actor for actor in cast_list if actor]
    return cast_list

# print(df.columns)

# df['preprocessed'] = df['Plot'].apply(clean_text)
# sample_plot = df['preprocessed'][0]
# print(sample_plot)

# embeddings = model.encode(sample_plot)
# print(embeddings)
