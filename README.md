# Robust Movie Recommendation System

This is a Streamlit-based Movie Recommender System that uses a **hybrid recommendation approach**—combining **content-based filtering** (via cosine similarity) and **collaborative filtering** (via SVD model predictions). It includes user authentication (login and registration) with hashed passwords, user-specific recommendations, and movie posters fetched from the TMDB API.
A content based movie recommender system using cosine similarity
models used:content based,matrix factorization and hybrid

## Dataset:

### https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata

## API:

### https://www.themoviedb.org/?language=en-AU

## Library Docs:

### https://docs.streamlit.io/deploy/concepts

---

## Features

- User Authentication (Login/Register with hashed passwords)
- Hybrid Movie Recommendations:
  - Content-based filtering using movie similarity
  - Collaborative filtering with SVD model predictions
- Movie posters via TMDB API
- User-specific recommendations based on past ratings
- JSON-based user management (user accounts, roles, email simulation)

---

## Project Structure

├── app.py # Main Streamlit app
├── movie_list.pkl # Pickled movie data (IDs, titles)
├── similarity.pkl # Pickled similarity matrix
├── ratings.csv # Movie ratings data (userId, movieId, rating)
├── svd_preds.csv # Predicted ratings from SVD model
├── users.json # User data (auto-generated after registration)
├── user_activities.json # User activity data (optional, auto-generated)
├── requirements.txt # Python dependencies
└── README.md # Project documentation

---

## Requirements

### Python Version

- **Python 3.10.0** (⚠️ **Required** — older or newer versions may cause issues)

---

## Setting Up the Environment

### Install Python 3.10.0

#### Download Python 3.10.0:

- [Windows installer](https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe)
- [macOS installer](https://www.python.org/ftp/python/3.10.0/python-3.10.0-macos11.pkg)
- [Linux tarball](https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz)

Or use **pyenv** (Linux/macOS):

```bash
pyenv install 3.10.0
pyenv global 3.10.0

python --version

python -m venv venv

### On Windows:
venv\Scripts\activate

### On macOS/Linux:
source venv/bin/activate

### Install Dependencies

pip install -r requirements.txt
```
