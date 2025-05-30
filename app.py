import streamlit as st
import pickle
import pandas as pd
import requests
import bcrypt
import json
import os

# Load data
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
ratings = pd.read_csv("ratings.csv")

# Load SVD predictions
preds_df = pd.read_csv("svd_preds.csv")

# User data
user_data_file = 'users.json'
activity_file = 'user_activities.json'

# Helper functions
def load_user_data():
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r') as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(user_data_file, 'w') as f:
        json.dump(data, f, indent=4)

def load_user_activities():
    if os.path.exists(activity_file):
        with open(activity_file, 'r') as f:
            return json.load(f)
    return {}

def save_user_activities(data):
    with open(activity_file, 'w') as f:
        json.dump(data, f, indent=4)

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()
        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    except:
        pass
    return None 


def recommend_hybrid(movie, user_id):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)
        title = movies.iloc[i[0]].title
        # Check if prediction exists
        svd_score = preds_df[(preds_df['userId'] == user_id) & (preds_df['movieId'] == movie_id)]["rating_pred"].values
        score = svd_score[0] if len(svd_score) > 0 else 0
        recommended_movies.append(f"{title} (Score: {score:.2f})")
        recommended_posters.append(poster)
    return recommended_movies, recommended_posters

# Streamlit app
st.set_page_config(page_title="Movie Recommender", layout="wide")

# Session state setup
if 'user' not in st.session_state:
    st.session_state.user = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

users = load_user_data()

# Authentication page before showing main app
# Init session state
# Initialize session
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    # Page heading
    st.markdown("<h2 style='text-align:center;'>🔐 Welcome</h2>", unsafe_allow_html=True)

    # Outer layout to center everything
    left, center, right = st.columns([1, 2, 1])
    with center:
        # Tabs inside the centered column
        login_tab, register_tab = st.tabs(["🔑 Login", "📝 Register"])

        with login_tab:
            st.write("")
            username = st.text_input("", placeholder="Username", key="login_user")
            password = st.text_input("", placeholder="Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True):
                if username not in users:
                    st.error("User does not exist.")
                elif not bcrypt.checkpw(password.encode(), users[username]['password'].encode()):
                    st.error("Incorrect password.")
                else:
                    st.session_state.user = username
                    st.session_state.user_id = users[username]['user_id']
                    st.success(f"Welcome, {username}!")
                    st.rerun()

        with register_tab:
            st.write("")
            new_user = st.text_input("", placeholder="Choose username", key="reg_user")
            email = st.text_input("", placeholder="Email (optional)", key="reg_email")
            pw = st.text_input("", placeholder="Password", type="password", key="reg_pass")
            pw_confirm = st.text_input("", placeholder="Confirm password", type="password", key="reg_confirm_pass")
            if st.button("Register", use_container_width=True):
                if not new_user or not pw or not pw_confirm:
                    st.error("All required fields must be filled.")
                elif email and ("@" not in email or "." not in email):
                    st.error("Invalid email.")
                elif pw != pw_confirm:
                    st.error("Passwords don't match.")
                elif len(pw) < 6:
                    st.error("Password too short.")
                elif new_user in users:
                    st.error("User already exists.")
                else:
                    user_id = len(users) + 1
                    hashed_pw = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
                    users[new_user] = {
                        "password": hashed_pw,
                        "user_id": user_id,
                        "role": "user",
                        "email": email,
                        "email_verified": False if email else True
                    }
                    save_user_data(users)
                    st.success("Registered! Check email (simulated)." if email else "Registered successfully.")
# Main app after login
if st.session_state.user:
    st.title("🎬 Movie Recommender System")
    username = st.session_state.user
    user_id = st.session_state.user_id

    st.sidebar.success(f"👋 Logged in as: {username}")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.user_id = None
        st.rerun()

    st.subheader(f"Hello, {username} (User ID: {user_id})")

    # Initialize session state for hybrid recommendations
    if 'hybrid_titles' not in st.session_state:
        st.session_state.hybrid_titles = []
    if 'hybrid_posters' not in st.session_state:
        st.session_state.hybrid_posters = []

    # Movie selection dropdown
    st.markdown("### 🔍 Search Movie you like")
    movie_name = st.selectbox("Choose a movie", movies['title'].values)

    # Recommend button
    if st.button("Recommend"):
        recommended_movies, posters = recommend_hybrid(movie_name, user_id)
        st.session_state.hybrid_titles = recommended_movies
        st.session_state.hybrid_posters = posters

    # Display recommendations (SVD or hybrid if available)
    st.markdown("### 🎯 Recommended For You")
    cols = st.columns(5)
    default_poster = "https://placehold.co/?text=No+Image"

    if st.session_state.hybrid_titles and st.session_state.hybrid_posters:
        for i in range(len(st.session_state.hybrid_titles)):
            poster = st.session_state.hybrid_posters[i] or default_poster
            cols[i % 5].image(poster, width=150)
            cols[i % 5].caption(st.session_state.hybrid_titles[i])
    else:
        user_preds = preds_df[preds_df['userId'] == user_id].sort_values(by='rating_pred', ascending=False).head(5)
        for idx, row in enumerate(user_preds.itertuples()):
            title = movies[movies['movie_id'] == row.movieId]['title'].values
            if len(title) > 0:
                poster = fetch_poster(row.movieId) or default_poster
                cols[idx % 5].image(poster, width=150)
                cols[idx % 5].caption(f"{title[0]} ({row.rating_pred:.2f})")
