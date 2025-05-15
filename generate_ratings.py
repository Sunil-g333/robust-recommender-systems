import pandas as pd
import numpy as np

# Load the TMDb movie dataset
tmdb_path = "tmdb_5000_movies.csv"  # Ensure this is in your project directory
movies = pd.read_csv(tmdb_path)

# Clean and filter the dataset
movies = movies.dropna(subset=['id', 'popularity'])
movies = movies[movies['popularity'].astype(str).str.replace('.', '', 1).str.isnumeric()]
movies['id'] = movies['id'].astype(int)
movies['popularity'] = movies['popularity'].astype(float)

# Simulate 100 users
user_ids = np.arange(1, 101)

# Generate synthetic ratings from popularity + noise
ratings_list = []
for user_id in user_ids:
    sampled_movies = movies.sample(n=50, random_state=user_id)
    for _, row in sampled_movies.iterrows():
        movie_id = row['id']
        rating = min(5.0, row['popularity'] / 10.0 + np.random.normal(0, 0.5))
        rating = round(max(0.5, min(rating, 5.0)), 1)  # Clip to 0.5–5.0
        ratings_list.append([user_id, movie_id, rating])

# Save to CSV
ratings_df = pd.DataFrame(ratings_list, columns=['userId', 'movieId', 'rating'])
ratings_df.to_csv('ratings.csv', index=False)
