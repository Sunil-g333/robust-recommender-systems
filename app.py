import streamlit as st
import pickle
import requests
import bcrypt
import json
import os
from surprise import SVD
import pandas as pd

with open("svd_model.pkl", "rb") as f:
    svd_model = pickle.load(f)

ratings = pd.read_csv("ratings.csv")


USERS_FILE = "users.json"
HISTORY_FILE = "user_activities.json"

# Load and Save JSON Utilities
def load_json(file):
    if os.path.exists(file):
        try:
            with open(file, "r") as f:
                content = f.read().strip()
                if content == "":
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            return {}
    return {}

def save_json(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# Password utilities
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


# App session state init
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'role' not in st.session_state:
    st.session_state.role = ""

users = load_json(USERS_FILE)
activity_history = load_json(HISTORY_FILE)

# Poster & Recommendation functions
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', "")
    return "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else ""

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    names, posters = [], []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        posters.append(fetch_poster(movie_id))
        names.append(movies.iloc[i[0]].title)
    return names, posters

def recommend_svd(user_id, n=5):
    movie_ids = movies['movie_id'].values
    seen = ratings[ratings['userId'] == user_id]['movieId'].tolist()
    unseen = [m for m in movie_ids if m not in seen]

    predictions = [(movie_id, svd_model.predict(user_id, movie_id).est) for movie_id in unseen]
    top_n = sorted(predictions, key=lambda x: x[1], reverse=True)[:n]

    names, posters = [], []
    for mid, _ in top_n:
        title = movies[movies['movie_id'] == mid]['title'].values[0]
        names.append(title)
        posters.append(fetch_poster(mid))
    return names, posters

# Login/Register UI
if not st.session_state.logged_in:
    st.title("🔐 Login or Register")
    login_tab, register_tab = st.tabs(["🔑 Login", "📝 Register"])

    with login_tab:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if username in users and check_password(password, users[username]['password']):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = users[username].get('role', 'user')
                st.success("✅ Login successful!")
                st.write(f"Role after login: {st.session_state.role}")  # Debugging line
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    with register_tab:
        new_user = st.text_input("Choose a username", key="reg_user")
        email = st.text_input("Email (simulated)", key="reg_email")
        pw1 = st.text_input("Password", type="password", key="reg_pass1")
        pw2 = st.text_input("Confirm Password", type="password", key="reg_pass2")
        if st.button("Register"):
            if new_user in users:
                st.warning("⚠️ Username already exists.")
            elif pw1 != pw2:
                st.warning("⚠️ Passwords do not match.")
            elif new_user.strip() == "" or pw1.strip() == "":
                st.warning("⚠️ Fields cannot be empty.")
            else:
                users[new_user] = {
                    "password": hash_password(pw1),
                    "role": "user",
                    "email": email
                }
                save_json(users, USERS_FILE)
                st.success("✅ Registered successfully. Please login.")

# Main App
else:
    st.sidebar.success(f"👋 Welcome, {st.session_state.username} ({st.session_state.role})")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))

    st.title("🎬 Movie Recommender System")
    method = st.selectbox("Choose recommendation method", ["Content-Based", "Matrix Factorization"])

    if method == "Content-Based":
        selected_movie = st.selectbox("Choose a movie", movies['title'].values)
    else:
        user_id = st.number_input("Enter your user ID (1–100)", min_value=1, max_value=100, step=1)

    if st.button("Show Recommendation"):
        if method == "Content-Based":
            names, posters = recommend(selected_movie)

            # Save to history
            user = st.session_state.username
            if user not in activity_history:
                activity_history[user] = []
            activity_history[user].append(selected_movie)
            save_json(activity_history, HISTORY_FILE)
        else:
            names, posters = recommend_svd(user_id)

        # Display posters
        cols = st.columns(5)
        for i in range(len(names)):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])


    st.subheader("📜 My History")
    user_history = activity_history.get(st.session_state.username, [])
    if user_history:
        for item in reversed(user_history[-10:]):
            st.markdown(f"- {item}")
    else:
        st.write("No history yet.")

# Admin Panel for Role Management and User Deletion
if st.session_state.role == "admin":
    st.subheader("🔧 Admin Panel: Manage User Roles and Delete Users")

    # Load users from the users.json file
    users = load_json(USERS_FILE)
    
    # List of usernames (excluding current admin user)
    usernames = [u for u in users if u != st.session_state.username]
    
    # Select user for role assignment or deletion
    selected_user = st.selectbox("Select user", usernames)
    
    # Role assignment functionality
    new_role = st.radio("Assign role", ["user", "admin"], index=0)
    
    if st.button("Update Role"):
        users[selected_user]["role"] = new_role
        save_json(users, USERS_FILE)
        st.success(f"✅ Updated {selected_user}'s role to {new_role}")
    
    # Delete user functionality
    if st.button("Delete User"):
        if selected_user != st.session_state.username:  # Prevent deleting the logged-in admin
            del users[selected_user]
            save_json(users, USERS_FILE)
            st.success(f"✅ Deleted user: {selected_user}")
        else:
            st.error("❌ You cannot delete your own account.")
