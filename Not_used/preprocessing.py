import pandas as pd
import string, re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sentence_transformers import SentenceTransformer

nltk.download('wordnet')
nltk.download('punkt_tab')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

df = pd.read_excel('C:\\Users\\ishaa\\OneDrive\\Documents\\MSU\\Spring 2026\\Data mining\\Project\\sample_data.xlsx', engine='openpyxl')

def clean_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    text = re.sub(r'\W', ' ', text)  # Remove special characters
    text = ([word for word in word_tokenize(text) if word not in stop_words])
    text = [stemmer.stem(word) for word in text]
    text = ' '.join(lemmatizer.lemmatize(word) for word in text)
    return text
# print(df.columns)

df['preprocessed'] = df['Plot'].apply(clean_text)
sample_plot = df['preprocessed'][0]
print(sample_plot)

embeddings = model.encode(sample_plot)
print(embeddings)