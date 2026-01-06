#!/usr/bin/env python3
"""
MDB List API MVP
Fetches movies from MDB List API and generates a local HTML page
matching the MDB List website layout.
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional


def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and not os.getenv(key):
                        os.environ[key] = value


# Load .env file
load_env_file()

MDBLIST_API_KEY = os.getenv('MDBLIST_API_KEY', '')
MDBLIST_API_URL = 'https://api.mdblist.com'
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'


def fetch_movies(limit=10) -> List[Dict]:
    """
    Fetch movies from MDB List API.
    Returns list of movies with ratings.
    """
    if not MDBLIST_API_KEY:
        print("Error: MDBLIST_API_KEY not found in environment")
        return []

    # API uses query parameter, not headers
    params_base = {'apikey': MDBLIST_API_KEY}
    
    movies = []
    
    # Try different endpoint patterns
    endpoints_to_try = [
        # Try getting a list by ID (using a common/public list ID)
        (f'{MDBLIST_API_URL}/list/1', {'limit': limit}),
        (f'{MDBLIST_API_URL}/list/popular', {'limit': limit}),
        (f'{MDBLIST_API_URL}/list/latest', {'limit': limit}),
        # Try media endpoint
        (f'{MDBLIST_API_URL}/media', {'type': 'movie', 'limit': limit, 'year': datetime.now().year}),
        # Try user's lists
        (f'{MDBLIST_API_URL}/user/lists', {}),
    ]
    
    for endpoint, extra_params in endpoints_to_try:
        try:
            params = {**params_base, **extra_params}
            print(f"Trying endpoint: {endpoint}")
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Response type: {type(data)}")
                
                # Handle different response structures
                if isinstance(data, list):
                    # If it's a list of lists, get items from first list
                    if data and isinstance(data[0], dict):
                        if 'items' in data[0]:
                            movies = data[0]['items']
                        elif 'id' in data[0] or 'list_id' in data[0]:
                            # Got a list, now fetch its items
                            list_id = data[0].get('id') or data[0].get('list_id')
                            list_response = requests.get(
                                f'{MDBLIST_API_URL}/list/{list_id}',
                                params={'apikey': MDBLIST_API_KEY, 'limit': limit},
                                timeout=10
                            )
                            if list_response.status_code == 200:
                                list_data = list_response.json()
                                if 'items' in list_data:
                                    movies = list_data['items']
                                elif isinstance(list_data, list):
                                    movies = list_data
                        else:
                            # Might be movies directly
                            movies = data
                elif isinstance(data, dict):
                    if 'items' in data:
                        movies = data['items']
                    elif 'results' in data:
                        movies = data['results']
                    elif 'movies' in data:
                        movies = data['movies']
                    elif 'data' in data:
                        movies = data['data']
                
                if movies:
                    print(f"Found {len(movies)} items")
                    break
            else:
                print(f"  Status {response.status_code}: {response.text[:100]}")
        except Exception as e:
            print(f"  Error: {e}")
            continue

    # If still no movies, try alternative approaches
    if not movies:
        print("\nTrying alternative endpoints...")
        # Try with list ID from URL pattern (MDB List URLs are like /list/12345)
        # We'll need to find a public list ID, but for now try some patterns
        alternative_endpoints = [
            (f'{MDBLIST_API_URL}/list/1/items', {}),
            (f'{MDBLIST_API_URL}/lists/1', {}),
        ]
        
        for endpoint, extra_params in alternative_endpoints:
            try:
                params = {**params_base, **extra_params}
                response = requests.get(endpoint, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        movies = data
                    elif isinstance(data, dict) and 'items' in data:
                        movies = data['items']
                    if movies:
                        break
            except:
                continue

    # Filter to only movies with ratings
    movies_with_ratings = []
    for movie in movies:
        if not isinstance(movie, dict):
            continue
            
        # Check if movie has any ratings
        has_rating = False
        rating_fields = ['imdb', 'imdb_rating', 'tmdb', 'tmdb_rating', 'rt_critics', 'rt_audience', 
                        'metacritic', 'letterboxd', 'trakt', 'overall_score', 'score', 'rating']
        for field in rating_fields:
            value = movie.get(field)
            if value is not None and value != '' and value != 'N/A':
                has_rating = True
                break
        
        if has_rating:
            movies_with_ratings.append(movie)
        
        if len(movies_with_ratings) >= limit:
            break

    return movies_with_ratings


def get_score_color(score: Optional[float]) -> str:
    """Get color class for score badge based on value."""
    if score is None:
        return 'gray'
    if score >= 75:
        return 'green'
    elif score >= 60:
        return 'yellow'
    elif score >= 40:
        return 'orange'
    else:
        return 'red'


def get_poster_url(movie: Dict, title: str, year: str) -> str:
    """Get poster URL, with fallback to TMDB if missing."""
    poster_url = movie.get('poster') or movie.get('poster_url') or movie.get('poster_path') or ''
    
    # If no poster, try to get from TMDB
    if not poster_url and TMDB_API_KEY:
        try:
            search_url = f'{TMDB_BASE_URL}/search/movie'
            params = {
                'api_key': TMDB_API_KEY,
                'query': title,
                'year': year,
                'language': 'en-US'
            }
            response = requests.get(search_url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    poster_path = data['results'][0].get('poster_path')
                    if poster_path:
                        poster_url = f'https://image.tmdb.org/t/p/w500{poster_path}'
        except:
            pass
    
    return poster_url or 'https://via.placeholder.com/120x180?text=No+Poster'


def get_source_color(source: str, score: Optional[float]) -> str:
    """Get color for source name based on source and score. Default is blue."""
    if score is None:
        return 'color: #5b9bd5;'  # Default blue
    
    # High scores get colored source names (matching MDB List colors)
    if source == 'tomato' and score >= 60:  # Certified Fresh
        return 'color: #FF4500; text-shadow: 0px 0px 1px #FFD700;'  # Orange with gold shadow
    elif source == 'popcorn' and score >= 80:  # High audience score
        return 'color: #6cbdb4; text-shadow: 0px 0px 1px #FFD700;'  # Teal/cyan with gold shadow
    elif source == 'metacritic' and score >= 70:  # High metacritic
        return 'color: #ffb74d;'  # Gold-ish
    
    # Default blue
    return 'color: #5b9bd5;'


def format_rating_with_votes(value, votes, source: str, popularity_rank: Optional[int] = None) -> tuple:
    """Format rating value and votes. Returns (formatted_score, vote_count_str, source_color_style, popularity_html)."""
    if value is None or value == '':
        return ('-', '', 'color: #5b9bd5;', '')
    
    # Format score (always white)
    if isinstance(value, (int, float)):
        if source in ['imdb', 'tmdb', 'letterboxd', 'roger_ebert']:
            score_str = f"{value:.1f}"
        else:
            score_str = f"{int(value)}"
    else:
        score_str = str(value)
    
    # Format popularity rank for IMDb (light green, 2-3px smaller than IMDb text which is 8px, so 5-6px)
    popularity_html = ''
    if popularity_rank and source == 'imdb':
        popularity_html = f'<span class="imdb-popularity">{popularity_rank}</span>'
    
    # Format votes (white, 1-2px smaller than 8px, so 6-7px, using 6px)
    vote_str = f"/{votes}/" if votes else ""
    
    # Get source color (only affects source name, not score)
    source_color_style = get_source_color(source, float(value) if isinstance(value, (int, float)) else None)
    
    return (score_str, vote_str, source_color_style, popularity_html)




def generate_html(movies: List[Dict]) -> str:
    """Generate HTML page matching MDB List layout (Song Sung Blue style)."""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movie Heat - Latest Releases</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #1a1a1a;
            color: #e0e0e0;
            padding: 20px;
            line-height: 1.2;
            font-size: 16px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        h1 {
            color: #fff;
            margin-bottom: 30px;
            font-size: 1.75em;
        }
        
        .movies-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }
        
        @media (max-width: 768px) {
            .movies-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .movie-card {
            background-color: #2a2a2a;
            border-radius: 0.5em;
            padding: 0.75em;
            display: flex;
            flex-direction: column;
            gap: 0.75em;
            border: 1px solid #3a3a3a;
        }
        
        .movie-top-section {
            display: flex;
            gap: 0.75em;
        }
        
        .movie-poster-container {
            flex-shrink: 0;
            min-width: 60%;
            width: 60%;
        }
        
        .movie-poster {
            width: 100%;
            height: auto;
            object-fit: contain;
            border-radius: 0.25em;
            background-color: #1a1a1a;
            display: block;
        }
        
        .movie-content {
            flex: 1;
            min-width: 0;
            width: 40%;
            display: flex;
            flex-direction: column;
        }
        
        .movie-header {
            display: flex;
            align-items: flex-start;
            justify-content: center;
            margin-bottom: 0.5em;
        }
        
        .movie-title-section {
            width: 100%;
            padding-top: 0.5em;
        }
        
        .movie-title {
            font-size: 1.4em;
            font-weight: 600;
            color: #fff;
            margin-bottom: 0.25em;
        }
        
        .movie-synopsis {
            font-size: 0.85em;
            color: #b0b0b0;
            line-height: 1.4;
        }
        
        .score-badge {
            width: 2.5em;
            height: 2.5em;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 200;
            font-size: 2.6em;
            line-height: 1;
            font-family: 'Nunito', 'Quicksand', 'Varela Round', 'Comfortaa', 'Mukta', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            flex-shrink: 0;
        }
        
        .score-badge.green {
            background-color: #4caf50;
            color: #fff;
        }
        
        .score-badge.yellow {
            background-color: #ffb74d;
            color: #fff;
        }
        
        .score-badge.orange {
            background-color: #ff9800;
            color: #fff;
        }
        
        .score-badge.red {
            background-color: #f44336;
            color: #fff;
        }
        
        .score-badge.gray {
            background-color: #666;
            color: #fff;
        }
        
        .ratings-table {
            margin-top: 0.5em;
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95em;
            line-height: 1.3;
        }
        
        .ratings-table td {
            padding: 0.15em 0.2em;
            vertical-align: baseline;
        }
        
        .rating-source {
            text-align: left;
            white-space: nowrap;
            padding-right: 0.3em;
        }
        
        .rating-source a {
            text-decoration: none;
        }
        
        .rating-source a:hover {
            text-decoration: underline;
        }
        
        .rating-score {
            color: #fff;
            text-align: center;
            white-space: nowrap;
            padding: 0 0.25em;
        }
        
        .rating-votes {
            color: #999;
            text-align: right;
            white-space: nowrap;
            font-size: 0.8em;
            padding-left: 0.25em;
        }
        
        .imdb-popularity {
            color: #81c784;
            font-size: 0.75em;
            margin-left: 0.15em;
        }
        
        .movie-meta {
            margin-top: 0.4em;
            font-size: 0.9em;
            color: #888;
        }
        
        .age-rating {
            color: #bbb;
            border: 1px solid #bbb;
            border-radius: 3px;
            padding: 0.15em 0.4em;
            display: inline-block;
            background: transparent;
            font-size: 1em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Latest Movie Releases</h1>
        <div class="movies-grid">
"""
    
    for movie in movies:
        # Extract movie data
        title = movie.get('title', 'Unknown')
        year = movie.get('year') or movie.get('release_date', '')[:4] if movie.get('release_date') else ''
        synopsis = movie.get('overview') or movie.get('synopsis') or movie.get('description') or 'No synopsis available.'
        
        # Get poster URL with fallback
        poster_url = get_poster_url(movie, title, year)
        
        # Get overall score
        overall_score = movie.get('overall_score') or movie.get('score') or movie.get('rating')
        if overall_score is None:
            # Try to calculate from available ratings
            scores = []
            if movie.get('imdb'):
                scores.append(float(movie.get('imdb', 0)) * 10)
            elif movie.get('imdb_rating'):
                scores.append(float(movie.get('imdb_rating', 0)) * 10)
            if movie.get('tmdb'):
                scores.append(float(movie.get('tmdb', 0)) * 10)
            elif movie.get('tmdb_rating'):
                scores.append(float(movie.get('tmdb_rating', 0)) * 10)
            if movie.get('rt_critics'):
                scores.append(float(movie.get('rt_critics', 0)))
            if movie.get('metacritic'):
                scores.append(float(movie.get('metacritic', 0)))
            if scores:
                overall_score = sum(scores) / len(scores)
        
        score_color = get_score_color(overall_score)
        score_display = f"{int(overall_score)}" if overall_score else "-"
        
        # Get ratings with votes and popularity
        imdb_score = movie.get('imdb') or movie.get('imdb_rating') or movie.get('imdbRating')
        imdb_votes = movie.get('imdb_votes') or movie.get('imdbVotes') or movie.get('imdbvotes')
        imdb_popularity = movie.get('imdb_popularity') or movie.get('imdbPopularity') or movie.get('imdbpopular')
        
        trakt_score = movie.get('trakt') or movie.get('trakt_rating') or movie.get('traktRating')
        trakt_votes = movie.get('trakt_votes') or movie.get('traktVotes')
        
        tmdb_score = movie.get('tmdb') or movie.get('tmdb_rating') or movie.get('tmdbRating') or movie.get('vote_average')
        tmdb_votes = movie.get('tmdb_votes') or movie.get('tmdbVotes') or movie.get('vote_count')
        
        letterboxd_score = movie.get('letterboxd') or movie.get('letterboxd_rating') or movie.get('letterboxdRating')
        letterboxd_votes = movie.get('letterboxd_votes') or movie.get('letterboxdVotes')
        
        rt_critics_score = movie.get('rt_critics') or movie.get('tomatometer') or movie.get('rt_critics_score') or movie.get('rtCritics')
        rt_critics_votes = movie.get('rt_critics_votes') or movie.get('rtCriticsVotes')
        
        rt_audience_score = movie.get('rt_audience') or movie.get('popcornmeter') or movie.get('rt_audience_score') or movie.get('rtAudience')
        rt_audience_votes = movie.get('rt_audience_votes') or movie.get('rtAudienceVotes')
        
        metacritic_score = movie.get('metacritic') or movie.get('metacritic_score') or movie.get('metacriticScore')
        metacritic_votes = movie.get('metacritic_votes') or movie.get('metacriticVotes')
        
        roger_ebert_score = movie.get('roger_ebert') or movie.get('ebert') or movie.get('rogerEbert')
        
        # Age rating
        age_rating = movie.get('age_rating') or movie.get('mpa_rating') or movie.get('certification') or ''
        
        # Truncate synopsis
        if len(synopsis) > 120:
            synopsis = synopsis[:117] + '...'
        
        # Build ratings table
        ratings_rows = []
        
        # IMDb
        imdb_score_str, imdb_votes_str, imdb_color, imdb_popularity_html = format_rating_with_votes(
            imdb_score, imdb_votes, 'imdb', imdb_popularity
        )
        ratings_rows.append(('IMDb', imdb_score_str, imdb_votes_str, imdb_color, imdb_popularity_html))
        
        # Trakt
        trakt_score_str, trakt_votes_str, trakt_color, _ = format_rating_with_votes(
            trakt_score, trakt_votes, 'trakt'
        )
        ratings_rows.append(('Trakt', trakt_score_str, trakt_votes_str, trakt_color, ''))
        
        # TMDb
        tmdb_score_str, tmdb_votes_str, tmdb_color, _ = format_rating_with_votes(
            tmdb_score, tmdb_votes, 'tmdb'
        )
        ratings_rows.append(('TMDb', tmdb_score_str, tmdb_votes_str, tmdb_color, ''))
        
        # Letterboxd
        letterboxd_score_str, letterboxd_votes_str, letterboxd_color, _ = format_rating_with_votes(
            letterboxd_score, letterboxd_votes, 'letterboxd'
        )
        ratings_rows.append(('Letterboxd', letterboxd_score_str, letterboxd_votes_str, letterboxd_color, ''))
        
        # Tomato (Rotten Tomatoes Critics)
        rt_critics_score_str, rt_critics_votes_str, rt_critics_color, _ = format_rating_with_votes(
            rt_critics_score, rt_critics_votes, 'tomato'
        )
        ratings_rows.append(('Tomato', rt_critics_score_str, rt_critics_votes_str, rt_critics_color, ''))
        
        # Popcorn (Rotten Tomatoes Audience)
        rt_audience_score_str, rt_audience_votes_str, rt_audience_color, _ = format_rating_with_votes(
            rt_audience_score, rt_audience_votes, 'popcorn'
        )
        ratings_rows.append(('Popcorn', rt_audience_score_str, rt_audience_votes_str, rt_audience_color, ''))
        
        # Metacritic
        metacritic_score_str, metacritic_votes_str, metacritic_color, _ = format_rating_with_votes(
            metacritic_score, metacritic_votes, 'metacritic'
        )
        ratings_rows.append(('Metacritic', metacritic_score_str, metacritic_votes_str, metacritic_color, ''))
        
        # Roger Ebert
        roger_ebert_score_str, roger_ebert_votes_str, roger_ebert_color, _ = format_rating_with_votes(
            roger_ebert_score, None, 'roger_ebert'
        )
        ratings_rows.append(('RogerEbert', roger_ebert_score_str, roger_ebert_votes_str, roger_ebert_color, ''))
        
        # Build ratings table HTML with links
        def get_source_url(source: str, movie: Dict) -> str:
            """Get URL for rating source based on movie data."""
            imdb_id = movie.get('imdb_id') or movie.get('imdbId') or movie.get('imdb')
            tmdb_id = movie.get('tmdb_id') or movie.get('tmdbId') or movie.get('tmdb_id')
            title_slug = title.lower().replace(' ', '-').replace(':', '').replace("'", '').replace('.', '')
            title_slug = ''.join(c for c in title_slug if c.isalnum() or c == '-')
            
            if source == 'IMDb' and imdb_id:
                return f'https://www.imdb.com/title/{imdb_id}'
            elif source == 'Trakt':
                return f'https://trakt.tv/movies/{title_slug}-{year}'
            elif source == 'TMDb' and tmdb_id:
                return f'https://www.themoviedb.org/movie/{tmdb_id}'
            elif source == 'Letterboxd' and imdb_id:
                return f'https://letterboxd.com/imdb/{imdb_id}'
            elif source == 'Tomato':
                return f'https://www.rottentomatoes.com/m/{title_slug}_{year}'
            elif source == 'Popcorn':
                return f'https://www.rottentomatoes.com/m/{title_slug}_{year}'
            elif source == 'Metacritic':
                return f'https://www.metacritic.com/movie/{title_slug}-{year}'
            elif source == 'RogerEbert':
                # Roger Ebert URLs are harder to construct, might need title search
                return '#'
            return '#'
        
        ratings_table_html = '<table class="ratings-table">'
        for source, score, votes, source_color_style, popularity_html in ratings_rows:
            if score != '-' or votes:
                source_url = get_source_url(source, movie)
                source_link = f'<a href="{source_url}" target="_blank" style="text-decoration: none; {source_color_style}">{source}</a>' if source_url != '#' else f'<span style="{source_color_style}">{source}</span>'
                ratings_table_html += f'''
                <tr>
                    <td class="rating-source">{source_link}{popularity_html}</td>
                    <td class="rating-score">{score}</td>
                    <td class="rating-votes">{votes}</td>
                </tr>'''
        ratings_table_html += '</table>'
        
        html += f"""
            <div class="movie-card">
                <div class="movie-top-section">
                    <div class="movie-poster-container">
                        <img src="{poster_url}" alt="{title}" class="movie-poster">
                    </div>
                    <div class="movie-content">
                        <div class="movie-header">
                            <div class="score-badge {score_color}">{score_display}</div>
                        </div>
                        {ratings_table_html}
                        {f'<div class="movie-meta"><span class="age-rating">{age_rating}+</span></div>' if age_rating else ''}
                    </div>
                </div>
                <div class="movie-title-section">
                    <div class="movie-title">{title}{f' ({year})' if year else ''}</div>
                    <div class="movie-synopsis">{synopsis}</div>
                </div>
            </div>
"""
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    
    return html


def get_sample_movies() -> List[Dict]:
    """Return sample movie data for testing HTML layout."""
    return [
        {
            'title': 'Dune: Part Two',
            'year': 2024,
            'poster': 'https://image.tmdb.org/t/p/w500/d5NXSklXo0qyUYgeFZHZwr7Gp9e.jpg',
            'overview': 'Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.',
            'overall_score': 85,
            'imdb': 8.5,
            'imdb_votes': 154502,
            'imdb_popularity': 20,
            'tmdb': 8.2,
            'tmdb_votes': 1541,
            'letterboxd': 4.2,
            'letterboxd_votes': 118,
            'trakt': 85,
            'trakt_votes': 140,
            'rt_critics': 92,
            'rt_critics_votes': 118,
            'rt_audience': 95,
            'rt_audience_votes': 799,
            'metacritic': 80,
            'metacritic_votes': 45,
            'roger_ebert': 4.0,
            'age_rating': 'PG-13'
        },
        {
            'title': 'Poor Things',
            'year': 2023,
            'poster': 'https://image.tmdb.org/t/p/w500/kCGlIMHnOm8JPXq3rXM6c5wMxcT.jpg',
            'overview': 'Brought back to life by an unorthodox scientist, a young woman runs off with a lawyer on a whirlwind adventure across the continents.',
            'overall_score': 82,
            'imdb': 7.9,
            'imdb_votes': 125000,
            'tmdb': 7.8,
            'tmdb_votes': 1200,
            'letterboxd': 4.0,
            'letterboxd_votes': 95000,
            'trakt': 82,
            'trakt_votes': 95,
            'rt_critics': 87,
            'rt_critics_votes': 350,
            'rt_audience': 73,
            'rt_audience_votes': 5000,
            'metacritic': 87,
            'metacritic_votes': 52,
            'roger_ebert': 4.5,
            'age_rating': 'R'
        },
        {
            'title': 'The Zone of Interest',
            'year': 2023,
            'poster': 'https://image.tmdb.org/t/p/w500/h4wj1xX7qZ7QdH1Z3Y9J8lZ5Y5N.jpg',
            'overview': 'The commandant of Auschwitz, Rudolf Höss, and his wife Hedwig strive to build a dream life for their family in a house and garden next to the camp.',
            'overall_score': 88,
            'imdb': 7.5,
            'imdb_votes': 85000,
            'tmdb': 7.4,
            'tmdb_votes': 800,
            'letterboxd': 4.1,
            'letterboxd_votes': 75000,
            'trakt': 88,
            'trakt_votes': 78,
            'rt_critics': 93,
            'rt_critics_votes': 280,
            'rt_audience': 68,
            'rt_audience_votes': 2500,
            'metacritic': 91,
            'metacritic_votes': 48,
            'roger_ebert': 4.0,
            'age_rating': 'PG-13'
        },
        {
            'title': 'Oppenheimer',
            'year': 2023,
            'poster': 'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg',
            'overview': 'The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.',
            'overall_score': 90,
            'imdb': 8.3,
            'imdb_votes': 450000,
            'imdb_popularity': 5,
            'tmdb': 8.1,
            'tmdb_votes': 8500,
            'letterboxd': 4.3,
            'letterboxd_votes': 285000,
            'trakt': 90,
            'trakt_votes': 320,
            'rt_critics': 93,
            'rt_critics_votes': 450,
            'rt_audience': 91,
            'rt_audience_votes': 10000,
            'metacritic': 88,
            'metacritic_votes': 62,
            'roger_ebert': 4.5,
            'age_rating': 'R'
        },
        {
            'title': 'Killers of the Flower Moon',
            'year': 2023,
            'poster': 'https://image.tmdb.org/t/p/w500/dB6Krk806zeqd0YNp2ngQ9zXteH.jpg',
            'overview': 'When oil is discovered in 1920s Oklahoma under Osage Nation land, the Osage people are murdered one by one.',
            'overall_score': 84,
            'imdb': 7.7,
            'imdb_votes': 180000,
            'tmdb': 7.6,
            'tmdb_votes': 2100,
            'letterboxd': 4.0,
            'letterboxd_votes': 120000,
            'trakt': 84,
            'trakt_votes': 180,
            'rt_critics': 93,
            'rt_critics_votes': 380,
            'rt_audience': 84,
            'rt_audience_votes': 5000,
            'metacritic': 89,
            'metacritic_votes': 55,
            'roger_ebert': 4.0,
            'age_rating': 'R'
        },
        {
            'title': 'Barbie',
            'year': 2023,
            'poster': 'https://image.tmdb.org/t/p/w500/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg',
            'overview': 'Barbie suffers a crisis that leads her to question her world and her existence.',
            'overall_score': 75,
            'imdb': 6.9,
            'imdb_votes': 520000,
            'imdb_popularity': 3,
            'tmdb': 7.0,
            'tmdb_votes': 12000,
            'letterboxd': 3.6,
            'letterboxd_votes': 450000,
            'trakt': 75,
            'trakt_votes': 450,
            'rt_critics': 88,
            'rt_critics_votes': 420,
            'rt_audience': 83,
            'rt_audience_votes': 25000,
            'metacritic': 80,
            'metacritic_votes': 68,
            'roger_ebert': 3.5,
            'age_rating': 'PG-13'
        },
        {
            'title': 'Past Lives',
            'year': 2023,
            'poster': 'https://image.tmdb.org/t/p/w500/k3wa1V6eq0Y4xO4G3u5F3qH8Z5N.jpg',
            'overview': 'Nora and Hae Sung, two deeply connected childhood friends, are wrested apart after Nora\'s family emigrates from South Korea.',
            'overall_score': 86,
            'imdb': 8.0,
            'imdb_votes': 95000,
            'tmdb': 8.1,
            'tmdb_votes': 1500,
            'letterboxd': 4.2,
            'letterboxd_votes': 180000,
            'trakt': 86,
            'trakt_votes': 120,
            'rt_critics': 96,
            'rt_critics_votes': 280,
            'rt_audience': 91,
            'rt_audience_votes': 5000,
            'metacritic': 94,
            'metacritic_votes': 45,
            'roger_ebert': 4.0,
            'age_rating': 'PG-13'
        },
        {
            'title': 'Anatomy of a Fall',
            'year': 2023,
            'poster': 'https://image.tmdb.org/t/p/w500/kQs6keheMwCxJxrzV83VUwFtHkB.jpg',
            'overview': 'A woman is suspected of her husband\'s murder, and their blind son faces a moral dilemma as the sole witness.',
            'overall_score': 87,
            'imdb': 7.8,
            'imdb_votes': 110000,
            'tmdb': 7.7,
            'tmdb_votes': 1800,
            'letterboxd': 4.1,
            'letterboxd_votes': 220000,
            'trakt': 87,
            'trakt_votes': 95,
            'rt_critics': 96,
            'rt_critics_votes': 320,
            'rt_audience': 88,
            'rt_audience_votes': 2500,
            'metacritic': 86,
            'metacritic_votes': 48,
            'roger_ebert': 4.0,
            'age_rating': 'R'
        },
        {
            'title': 'The Holdovers',
            'year': 2023,
            'poster': 'https://image.tmdb.org/t/p/w500/6g49v3lNhEMs3VC9Vlf7x1ePwQ.jpg',
            'overview': 'A curmudgeonly instructor at a New England prep school is forced to remain on campus during Christmas break to babysit a handful of students.',
            'overall_score': 83,
            'imdb': 7.9,
            'imdb_votes': 88000,
            'tmdb': 7.8,
            'tmdb_votes': 1200,
            'letterboxd': 4.0,
            'letterboxd_votes': 150000,
            'trakt': 83,
            'trakt_votes': 88,
            'rt_critics': 97,
            'rt_critics_votes': 290,
            'rt_audience': 92,
            'rt_audience_votes': 5000,
            'metacritic': 81,
            'metacritic_votes': 42,
            'roger_ebert': 4.0,
            'age_rating': 'R'
        },
        {
            'title': 'Spider-Man: Across the Spider-Verse',
            'year': 2023,
            'poster': 'https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61eNJ51NqUn2Z.jpg',
            'overview': 'Miles Morales catapults across the multiverse, where he encounters a team of Spider-People charged with protecting its very existence.',
            'overall_score': 88,
            'imdb': 8.7,
            'imdb_votes': 380000,
            'imdb_popularity': 8,
            'tmdb': 8.6,
            'tmdb_votes': 9500,
            'letterboxd': 4.4,
            'letterboxd_votes': 320000,
            'trakt': 88,
            'trakt_votes': 280,
            'rt_critics': 95,
            'rt_critics_votes': 380,
            'rt_audience': 94,
            'rt_audience_votes': 15000,
            'metacritic': 86,
            'metacritic_votes': 58,
            'roger_ebert': 4.5,
            'age_rating': 'PG'
        }
    ]


def main():
    """Main execution."""
    print("MDB List API MVP")
    print("Fetching movies...\n")
    
    movies = fetch_movies(limit=10)
    
    if not movies:
        print("⚠️  Could not fetch from API (endpoint structure may differ)")
        print("Using sample data to demonstrate HTML layout...\n")
        movies = get_sample_movies()
        print(f"Generated {len(movies)} sample movies for preview")
    else:
        print(f"✅ Successfully fetched {len(movies)} movies from API")
    
    print(f"Found {len(movies)} movies with ratings")
    print("\nGenerating HTML...")
    
    html_content = generate_html(movies)
    
    output_file = 'movies_preview.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nHTML file generated: {output_file}")
    print(f"Open it in your browser to view the results!")
    print(f"\nFull path: {os.path.abspath(output_file)}")


if __name__ == '__main__':
    main()
