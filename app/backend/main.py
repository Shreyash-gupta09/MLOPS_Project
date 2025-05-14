from fastapi import FastAPI
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import os
import pickle
import joblib

app = FastAPI()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load all required model artifacts
cosine_sim = pickle.load(open("models/cosine_sim2.pkl", "rb"))
df2 = pickle.load(open("models/df2.pkl", "rb"))
indices = pickle.load(open("models/indices.pkl", "rb"))
svd_model = joblib.load("models/svd_model.pkl")

def get_recommendations(title: str):
    title = title.lower().strip()
    title_mapping = {t.lower(): i for t, i in indices.items()}
    if title not in title_mapping:
        return ["Movie not found in dataset."]
    
    idx = title_mapping[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return df2['title'].iloc[movie_indices].tolist()

@app.get("/recommend/{movie_name}", response_model=List[str])
def recommend(movie_name: str):
    try:
        return get_recommendations(movie_name)
    except Exception:
        return ["Something went wrong. Please try again."]
