import pandas as pd

# Disable chained assignment warnings
pd.options.mode.chained_assignment = None

# Load raw dataset
data = pd.read_csv("raw_movies.csv")

# Impute missing values if needed (optional based on your original logic)
data = data.fillna('')

# Handle durations separately
tv_data = data[data.type == 'TV Show']
tv_data['duration'] = tv_data['duration'].str.replace(' Season', '')
tv_data['duration'] = tv_data['duration'].str.replace('s', '')
tv_data['duration'] = tv_data['duration'].astype(str).astype(int)

movie_data = data[data.type == 'Movie']
movie_data['duration'] = movie_data['duration'].str.replace(' min', '').str.strip()
movie_data = movie_data[movie_data['duration'] != '']  
movie_data['duration'] = movie_data['duration'].astype(int)


# Combine back if you want to use full data
data = pd.concat([movie_data, tv_data], axis=0)

# Feature cleaning for recommender
def clean_data(x):
    return str.lower(x.replace(' ', ''))

features = ['title', 'director', 'cast', 'listed_in', 'description']
train_data = data[features].fillna('')

for feature in features:
    train_data[feature] = train_data[feature].apply(clean_data)

# Save cleaned data to CSV
train_data.to_csv("cleaned_data.csv", index=False)

print("✅ Data cleaning complete. Saved as cleaned_data.csv")
