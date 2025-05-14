import os
import pandas as pd
import numpy as np
import pickle
import joblib
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from surprise import Reader, Dataset, SVD

# Ensure output directory exists
os.makedirs('models', exist_ok=True)

# Load datasets
credits = pd.read_csv('data/raw/tmdb_5000_credits.csv')
movies = pd.read_csv('data/raw/tmdb_5000_movies.csv')
ratings = pd.read_csv('data/raw/ratings_small.csv')

# Fix column names and merge
credits.columns = ['id', 'title', 'cast', 'crew']
df2 = movies.merge(credits, on='id')

# Fix 'title_x'/'title_y' issue
df2.rename(columns={'title_x': 'title'}, inplace=True)
if 'title_y' in df2.columns:
    df2.drop(columns=['title_y'], inplace=True)

# Optional debug print
print(df2.columns)

# Parse JSON-like strings into Python objects
for feature in ['cast', 'crew', 'keywords', 'genres']:
    df2[feature] = df2[feature].apply(literal_eval)

# TF-IDF on overviews
df2['overview'] = df2['overview'].fillna('')
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df2['overview'])

# Save for reference (not used later)
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Extract director
def get_director(x):
    for i in x:
        if i.get('job') == 'Director':
            return i['name']
    return np.nan

def get_list(x):
    if isinstance(x, list):
        names = [i['name'] for i in x]
        return names[:3] if len(names) > 3 else names
    return []

def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    elif isinstance(x, str):
        return str.lower(x.replace(" ", ""))
    return ''

df2['director'] = df2['crew'].apply(get_director)

for feature in ['cast', 'keywords', 'genres']:
    df2[feature] = df2[feature].apply(get_list)

for feature in ['cast', 'keywords', 'director', 'genres']:
    df2[feature] = df2[feature].apply(clean_data)

df2['soup'] = df2.apply(lambda x: ' '.join(x['keywords']) + ' ' +
                                     ' '.join(x['cast']) + ' ' +
                                     x['director'] + ' ' +
                                     ' '.join(x['genres']), axis=1)

# Count Vectorizer
count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(df2['soup'])

cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

# Index mapping
df2 = df2.reset_index()
assert 'title' in df2.columns, "❌ 'title' column missing"
indices = pd.Series(df2.index, index=df2['title'].str.lower())

# Collaborative Filtering with Surprise SVD
reader = Reader(rating_scale=(0.5, 5.0))
data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
trainset = data.build_full_trainset()
svd_model = SVD()
svd_model.fit(trainset)

# Save models
with open('models/cosine_sim2.pkl', 'wb') as f:
    pickle.dump(cosine_sim2, f)

with open('models/df2.pkl', 'wb') as f:
    pickle.dump(df2, f)

with open('models/indices.pkl', 'wb') as f:
    pickle.dump(indices, f)

joblib.dump(svd_model, 'models/svd_model.pkl')

print("✅ Training complete. Models saved in /models")
