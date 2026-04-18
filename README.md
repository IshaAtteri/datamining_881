# CSE 881: Data Mining - Movie Recommendation System

Movie recommendation system using both algorithm-based (item-item collab filtering) and model-based approaches, combining IMDB data, Wikipedia plots, and Netflix ratings.

## Setup

1. Create venv and install frontend dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install
```

2. Get the data:

**IMDB datasets** - Download from https://developer.imdb.com/non-commercial-datasets/:
- `title.basics.tsv` (required for movie list)
- Unzip and put in `data/raw/imdb_datasets/`

**Wikipedia ZIM** - Download from https://www.kiwix.org/:
- `wikipedia_en_all_maxi_2025-08.zim` → `data/raw/wikipedia/`
- Plot text,  movie descriptions, and movie posters


**Netflix data (ground truth)** - Download from https://www.kaggle.com/datasets/netflix-inc/netflix-prize-data:
- Extract the rating files and put in `data/raw/netflix_data/`
- Used in ground truth user ratings evaluation to compare model recommendations against actual user ratings

3. Run the pipeline (from `pipeline_code/` dir):

```bash
cd pipeline_code

# 1. Data Collection - Extracts movie HTML from Wikipedia ZIM files
python 1_data_collection/extract_wiki_zim.py

# 2. Dataset Construction - Parses metadata from HTML, fuses with Netflix ratings
python 2_dataset_construction/dataset_create.py
python 2_dataset_construction/scrape.py
python 2_dataset_construction/fuse_with_netflix.py

# 3. Preprocessing - Cleans plot text (tokenize, remove stopwords, stem/lemmatize)
python 3_preprocessing/preprocessing.py

# 4. Embeddings - Converts plots to sentence embeddings (vectors)
python 4_embeddings/vec_representation.py

# 5. Model - Builds item-item similarity model based on plot embeddings
python 5_model/item-item-model.py

# 6. Serving - Starts Flask API for recommendations
python 6_serving/model_server.py

# 7. Evaluation - Compares predictions against Netflix user ratings and generate figures
python 7_evaluation/ground_truth_comp.py
```

4. Run frontend (new terminal):
```bash
cd frontend
npm run dev  # http://localhost:3000

# The frontend relies on a Supabase DB. Make sure to configure the DB and update the endpoints in order to be able to use the frontend. You can still use the model server (step 6) and check the results from either the model or the algorithm without needing the frontend. 
```

## Citations
- [IMDB Non-Commercial Datasets](https://developer.imdb.com/non-commercial-datasets/)
- [Netflix Prize Data](https://www.kaggle.com/datasets/netflix-inc/netflix-prize-data)
- [Kiwix](https://www.kiwix.org/)
