import streamlit as st
import pickle
import requests
import random

# Load the data
movies = pickle.load(open("movies_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))
movies_list = movies["title"].values

# TMDB API key
API_KEY = "30c33629725f632ec3ee2e1d59030dab"

# Function to fetch movie posters and details
def fetch_movie_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path', None)
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            poster_url = "https://via.placeholder.com/500x750?text=No+Image"
        return {
            "poster": poster_url,
            "overview": data.get("overview", "No overview available."),
            "rating": data.get("vote_average", "N/A"),
            "release_date": data.get("release_date", "Unknown"),
            "genres": ", ".join([genre['name'] for genre in data.get('genres', [])])
        }
    except Exception:
        return {
            "poster": "https://via.placeholder.com/500x750?text=Error",
            "overview": "No overview available.",
            "rating": "N/A",
            "release_date": "Unknown",
            "genres": "Unknown"
        }

# Function to fetch random movies
def get_random_movies(num_movies=5):
    random_indices = random.sample(range(len(movies)), num_movies)
    random_movies = []
    for idx in random_indices:
        movie_id = movies.iloc[idx].id
        details = fetch_movie_details(movie_id)
        random_movies.append({
            "title": movies.iloc[idx].title,
            "poster": details["poster"],
            "overview": details["overview"],
            "rating": details["rating"],
            "release_date": details["release_date"],
            "genres": details["genres"]
        })
    return random_movies

# Function to recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    recommended_movies = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].id
        details = fetch_movie_details(movie_id)
        recommended_movies.append({
            "title": movies.iloc[i[0]].title,
            "poster": details["poster"],
            "overview": details["overview"],
            "rating": details["rating"],
            "release_date": details["release_date"],
            "genres": details["genres"]
        })
    return recommended_movies

# Function to fetch movies by actor
def fetch_movies_by_actor(actor_name):
    try:
        url = f"https://api.themoviedb.org/3/search/person?api_key={API_KEY}&query={actor_name}"
        response = requests.get(url).json()
        if response['results']:
            known_for = response['results'][0].get('known_for', [])
            movies = [(movie.get('title', 'Unknown Title'), fetch_movie_details(movie.get('id', 0))['poster']) for movie in known_for]
            return movies
        else:
            return []
    except Exception:
        return []

# Streamlit layout settings
st.set_page_config(page_title="🎥 Movie Recommender", layout="wide")

# Inject custom CSS for advanced UI
def add_custom_css():
    st.markdown("""
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background: linear-gradient(135deg, #1f1c2c, #928dab);
                color: white;
            }

            .header {
                text-align: center;
                padding: 40px 20px;
                background: linear-gradient(to right, #ff7e5f, #feb47b);
                color: white;
                border-radius: 8px;
                margin-bottom: 30px;
            }

            .movie-row {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 30px;
            }

            .movie-card {
                flex: 0 0 200px;
                background: #2c2c54;
                border-radius: 12px;
                padding: 10px;
                text-align: center;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }

            .movie-card:hover {
                transform: scale(1.1);
                box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.4);
            }

            .movie-card img {
                border-radius: 8px;
                width: 100%;
                height: auto;
            }

            .movie-card h4 {
                margin: 10px 0;
                font-size: 1rem;
                color: #ffcc00;
            }

            .movie-card p {
                font-size: 0.85rem;
                color: #d9d9d9;
            }
        </style>
    """, unsafe_allow_html=True)

add_custom_css()

# Header Section
st.markdown("""
<div class="header">
    <h1>🎥 Welcome to the Movie Recommender System</h1>
    <p>Get personalized recommendations or explore random movies below!</p>
</div>
""", unsafe_allow_html=True)

# Search bar for movie recommendations
st.header("🔍 Search for Movie Recommendations")
movie_query = st.text_input("Enter movie title")
if movie_query:
    recommended_movies = recommend(movie_query)
    st.subheader(f"Movies Similar to {movie_query}")
    st.markdown('<div class="movie-row">', unsafe_allow_html=True)
    for movie in recommended_movies:
        st.markdown(f"""
            <div class="movie-card">
                <img src="{movie['poster']}" alt="{movie['title']}">
                <h4>{movie['title']}</h4>
                <p>Rating: {movie['rating']}<br>Genres: {movie['genres']}</p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


st.header("🎲 Explore Random Movies")
random_movies = get_random_movies()
st.markdown('<div class="movie-row">', unsafe_allow_html=True)
for movie in random_movies:
    st.markdown(f"""
        <div class="movie-card">
            <img src="{movie['poster']}" alt="{movie['title']}">
            <h4>{movie['title']}</h4>
            <p>Rating: {movie['rating']}<br>Genres: {movie['genres']}</p>
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
