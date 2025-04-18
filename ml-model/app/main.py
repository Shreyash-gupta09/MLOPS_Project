from fastapi import FastAPI
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import os
import pickle
import joblib
import gdown

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

# Base directory: same as where main.py is
base_dir = os.path.dirname(os.path.abspath(__file__))
notebooks_dir = base_dir  # You can change to another directory if needed

# Google Drive File IDs
PKL_FILES = {
    "cosine_sim2.pkl": "1cFuoDQOKzyHKawDZF_6kiIghS4jWDS2X",
    "df2.pkl": "1M8j_fLvveEyvQvnWOrRPZTmOr-Dtm79p",
    "indices.pkl": "1Batss1ibIUw_8arhrE5JcjM-huxHyTMQ",
    "svd_model.pkl": "1OblWzoQ6PSKluX132c4l-l3pyqVF_o3t"
}

# Download helper
def gdrive_download_if_missing(filename, file_id):
    filepath = os.path.join(notebooks_dir, filename)
    if not os.path.exists(filepath):
        print(f"Downloading {filename} from Google Drive...")
        gdown.download(f"https://drive.google.com/uc?id={file_id}", filepath, quiet=False)
    return filepath

# Load files (auto-download if not found)
cosine_sim = pickle.load(open(gdrive_download_if_missing("cosine_sim2.pkl", PKL_FILES["cosine_sim2.pkl"]), 'rb'))
df2 = pickle.load(open(gdrive_download_if_missing("df2.pkl", PKL_FILES["df2.pkl"]), 'rb'))
indices = pickle.load(open(gdrive_download_if_missing("indices.pkl", PKL_FILES["indices.pkl"]), 'rb'))
svd_model = joblib.load(gdrive_download_if_missing("svd_model.pkl", PKL_FILES["svd_model.pkl"]))


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

