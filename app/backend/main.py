# app/backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load cleaned dataset
df = pd.read_csv("cleaned_data.csv")
vectorizer = CountVectorizer(stop_words='english')
count_matrix = vectorizer.fit_transform(df['soup'])
cosine_sim = cosine_similarity(count_matrix, count_matrix)

# Index mapping for titles
df = df.reset_index()
indices = pd.Series(df.index, index=df['title'])

def get_recommendations(title: str, cosine_sim=cosine_sim):
    title = title.replace(" ", "").lower()
    title_mapping = {t.replace(" ", "").lower(): i for t, i in indices.items()}
    if title not in title_mapping:
        return ["Movie not found."]
    idx = title_mapping[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return df['title'].iloc[movie_indices].tolist()

@app.get("/recommend/{movie_name}", response_model=List[str])
def recommend(movie_name: str):
    try:
        return get_recommendations(movie_name)
    except KeyError:
        raise HTTPException(status_code=404, detail="Movie not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
