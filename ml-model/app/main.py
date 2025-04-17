from fastapi import FastAPI
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import os
import pickle
import joblib

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend (e.g., React on localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Base directory: current directory of main.py
base_dir = os.path.dirname(os.path.abspath(__file__))

# Load saved data and model
with open(os.path.join(base_dir, '../notebooks/cosine_sim2.pkl'), 'rb') as f:
    cosine_sim = pickle.load(f)

with open(os.path.join(base_dir, '../notebooks/df2.pkl'), 'rb') as f:
    df2 = pickle.load(f)

with open(os.path.join(base_dir, '../notebooks/indices.pkl'), 'rb') as f:
    indices = pickle.load(f)

svd_model = joblib.load(os.path.join(base_dir, '../notebooks/svd_model.pkl'))


# Recommendation logic
def get_recommendations(title: str):
    title = title.lower().strip()
    title_mapping = {t.lower(): i for t, i in indices.items()}

    if title not in title_mapping:
        return ["Movie not found in dataset."]

    idx = title_mapping[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  # Top 10 similar movies
    movie_indices = [i[0] for i in sim_scores]
    return df2['title'].iloc[movie_indices].tolist()

# API endpoint
@app.get("/recommend/{movie_name}", response_model=List[str])
def recommend(movie_name: str):
    try:
        return get_recommendations(movie_name)
    except Exception:
        return ["Movie not found in dataset."]

