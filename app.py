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

# Function to fetch movie details
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
    for i in distances[1:6]:  # Top 5 recommendations
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

# Function to search for actors and movies
def search(query):
    query = query.lower()
    movies_found = [movie for movie in movies_list if query in movie.lower()]
    actors_found = fetch_movies_by_actor(query) if query else []
    return movies_found, actors_found

# Streamlit configuration
st.set_page_config(page_title="🎥 Movie Recommender", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        .movie-row {
            display: flex;
            overflow-x: auto;
            gap: 20px;
            padding: 10px 0;
        }
        .movie-card {
            flex: 0 0 auto;
            background: #2c2c54;
            border-radius: 12px;
            padding: 10px;
            width: 200px;
            text-align: center;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
        }
        .movie-card img {
            border-radius: 8px;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# Search Section
st.title("🎥 Movie & Actor Search")
query = st.text_input("Search for movies or actors")
if query:
    movies_found, actors_found = search(query)
    if movies_found:
        st.subheader("Movies Found")
        st.markdown('<div class="movie-row">', unsafe_allow_html=True)
        for movie in movies_found:
            st.markdown(f"""
                <div class="movie-card">
                    <h4>{movie}</h4>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    if actors_found:
        st.subheader("Movies by Actor")
        st.markdown('<div class="movie-row">', unsafe_allow_html=True)
        for title, poster in actors_found:
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{poster}" alt="{title}">
                    <h4>{title}</h4>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Random Movies Section
st.header("🎲 Random Movies")
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
