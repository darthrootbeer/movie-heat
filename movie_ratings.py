#!/usr/bin/env python3
"""
Movie Ratings Checker
Fetches latest movie releases and displays ratings from multiple sources:
- IMDB (via OMDb API)
- Rotten Tomatoes - Tomatometer (via RT web scraping)
- Rotten Tomatoes - Popcornmeter/Audience Score (via RT web scraping)
- Metacritic (via OMDb API)
- TMDB (The Movie Database)
- CinemaScore (via CinemaScore API)
"""

import os
import sys
import json
import re
import requests
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional


def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # Only set if not already in environment
                    if key and not os.getenv(key):
                        os.environ[key] = value


# Load .env file first
load_env_file()

# API Configuration
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '')
OMDB_API_KEY = os.getenv('OMDB_API_KEY', '')

TMDB_BASE_URL = 'https://api.themoviedb.org/3'
OMDB_BASE_URL = 'http://www.omdbapi.com/'


def normalize_score(value: str, score_type: str) -> str:
    """
    Normalize different score formats to 0-100 integer scale.
    Returns string representation of normalized score or '-'.
    """
    if not value or value == 'N/A' or value == '-':
        return '-'

    try:
        if score_type == 'imdb':
            # Format: "8.5/10" -> 85
            score = float(value.split('/')[0])
            return str(int(score * 10))

        elif score_type == 'tomato' or score_type == 'popcorn' or score_type == 'letterboxd':
            # Format: "92%" -> 92
            return value.rstrip('%')

        elif score_type == 'metacritic':
            # Format: "73/100" -> 73
            return value.split('/')[0]

        elif score_type == 'tmdb':
            # Format: "8.2" or "8.2/10" -> 82
            if '/' in value:
                score = float(value.split('/')[0])
            else:
                score = float(value)
            return str(int(score * 10))

        elif score_type == 'cinemascore':
            # Letter grades to percentage using 2025 school grading scale
            grade_map = {
                'A+': '98', 'A': '95', 'A-': '92',
                'B+': '88', 'B': '85', 'B-': '82',
                'C+': '78', 'C': '75', 'C-': '72',
                'D+': '68', 'D': '65', 'D-': '62',
                'F': '50'
            }
            return grade_map.get(value.upper(), '-')

        else:
            return '-'

    except (ValueError, IndexError, AttributeError):
        return '-'


def check_api_keys():
    """Verify that required API keys are set."""
    missing = []
    if not TMDB_API_KEY:
        missing.append('TMDB_API_KEY')
    if not OMDB_API_KEY:
        missing.append('OMDB_API_KEY')

    if missing:
        print("Error: Missing required API keys:", ', '.join(missing))
        print("\nTo get free API keys:")
        print("1. TMDB: https://www.themoviedb.org/settings/api")
        print("2. OMDb: http://www.omdbapi.com/apikey.aspx")
        print("\nSet them as environment variables or create a .env file:")
        print("  export TMDB_API_KEY='your_key_here'")
        print("  export OMDB_API_KEY='your_key_here'")
        sys.exit(1)


def get_movie_details(movie_id: int) -> Dict:
    """Fetch detailed movie info from TMDB including credits."""
    try:
        # Get movie details
        details_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
        credits_url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits"
        releases_url = f"{TMDB_BASE_URL}/movie/{movie_id}/release_dates"

        params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}

        details = requests.get(details_url, params=params, timeout=10).json()
        credits = requests.get(credits_url, params=params, timeout=10).json()
        releases = requests.get(releases_url, params=params, timeout=10).json()

        # Extract crew info
        crew = credits.get('crew', [])
        director = next((c['name'] for c in crew if c['job'] == 'Director'), 'N/A')
        writer = next((c['name'] for c in crew if c['job'] in ['Writer', 'Screenplay']), 'N/A')
        producer = next((c['name'] for c in crew if c['job'] == 'Producer'), 'N/A')

        # Extract top billed actors (1-5 based on availability)
        cast = credits.get('cast', [])[:5]
        actors = ', '.join(c['name'] for c in cast) if cast else 'N/A'

        # Extract genres (top 3)
        genres = ', '.join(g['name'] for g in details.get('genres', [])[:3]) or 'N/A'

        # Runtime
        runtime = f"{details.get('runtime', 0)} min" if details.get('runtime') else 'N/A'

        # MPA rating
        us_releases = next((r for r in releases.get('results', []) if r['iso_3166_1'] == 'US'), {})
        rating = next((r['certification'] for r in us_releases.get('release_dates', []) if r['certification']), 'NR')

        # Release type (wide vs limited)
        release_type = next((r['type'] for r in us_releases.get('release_dates', []) if r['certification']), 3)
        release_label = 'Wide' if release_type >= 3 else 'Limited'

        # Studio
        studios = details.get('production_companies', [])
        studio = studios[0]['name'] if studios else 'N/A'

        return {
            'director': director,
            'writer': writer,
            'producer': producer,
            'actors': actors,
            'genres': genres,
            'runtime': runtime,
            'mpa_rating': rating,
            'release_type': release_label,
            'studio': studio,
            'overview': details.get('overview', 'N/A')
        }
    except:
        return {
            'director': 'N/A', 'writer': 'N/A', 'producer': 'N/A',
            'actors': 'N/A', 'genres': 'N/A', 'runtime': 'N/A',
            'mpa_rating': 'NR', 'release_type': 'N/A', 'studio': 'N/A',
            'overview': 'N/A'
        }


def get_latest_releases(limit=15) -> List[Dict]:
    """
    Fetch movies released in the last 7 days (excluding today).
    Uses TMDB discover endpoint with date filtering.
    """
    url = f"{TMDB_BASE_URL}/discover/movie"

    # Calculate date range: 7 days ago through yesterday
    today = datetime.now().date()
    end_date = today - timedelta(days=1)  # Yesterday (exclude today)
    start_date = end_date - timedelta(days=6)  # 7 days total (yesterday + 6 days before)

    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US',
        'region': 'US',
        'sort_by': 'popularity.desc',  # Major releases first
        'primary_release_date.gte': start_date.strftime('%Y-%m-%d'),
        'primary_release_date.lte': end_date.strftime('%Y-%m-%d'),
        'with_release_type': '2|3',  # Theatrical releases only (Limited=2, Wide=3)
        'with_runtime.gte': 40,  # Features only (40+ min), no short films
        'vote_count.gte': 5,  # Movies with basic indexing/metadata
        'page': 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        movies = []
        for movie in data.get('results', [])[:limit]:
            release_date = movie.get('release_date', '')
            movies.append({
                'id': movie.get('id'),
                'title': movie.get('title', 'Unknown'),
                'release_date': release_date,
                'year': release_date[:4] if release_date else '',
                'tmdb_rating': movie.get('vote_average', 0)
            })
        return movies

    except requests.RequestException as e:
        print(f"Error fetching from TMDB: {e}")
        return []


def get_omdb_ratings(title: str, year: str) -> Dict[str, Optional[str]]:
    """
    Fetch IMDB and Metacritic ratings from OMDb API.
    Returns dict with imdb_rating and metacritic.
    """
    params = {
        'apikey': OMDB_API_KEY,
        't': title,
        'y': year,
        'type': 'movie'
    }

    result = {
        'imdb_rating': 'N/A',
        'metacritic': 'N/A'
    }

    try:
        response = requests.get(OMDB_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('Response') == 'True':
            # IMDB Rating
            imdb = data.get('imdbRating', 'N/A')
            if imdb != 'N/A':
                result['imdb_rating'] = f"{imdb}/10"

            # Metacritic score
            metascore = data.get('Metascore', 'N/A')
            if metascore != 'N/A':
                result['metacritic'] = f"{metascore}/100"

        return result

    except requests.RequestException:
        return result


def get_rt_scores(title: str, year: str) -> Dict[str, str]:
    """
    Scrape both Tomatometer and Popcornmeter from Rotten Tomatoes website.
    Returns dict with 'tomatometer' and 'popcornmeter' scores.
    """
    result = {
        'tomatometer': 'N/A',
        'popcornmeter': 'N/A'
    }

    # Format title for RT URL (lowercase, replace spaces with underscores)
    rt_title = title.lower().replace(' ', '_').replace(':', '').replace("'", '').replace('-', '_')
    # Remove special characters
    rt_title = re.sub(r'[^\w_]', '', rt_title)

    # Try common URL patterns
    url_patterns = [
        f"https://www.rottentomatoes.com/m/{rt_title}",
        f"https://www.rottentomatoes.com/m/{rt_title}_{year}",
    ]

    for url in url_patterns:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                continue

            html = response.text

            # Look for embedded JSON with score data
            json_pattern = r'<script[^>]*type="application/(?:ld\+)?json"[^>]*>(.*?)</script>'
            matches = re.findall(json_pattern, html, re.DOTALL)

            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, dict) and 'audienceScore' in data and 'criticsScore' in data:
                        # Extract Tomatometer (critics score)
                        critics = data.get('criticsScore', {})
                        if 'score' in critics:
                            result['tomatometer'] = f"{critics['score']}%"

                        # Extract Popcornmeter (audience score)
                        audience = data.get('audienceScore', {})
                        if 'score' in audience:
                            result['popcornmeter'] = f"{audience['score']}%"

                        return result
                except (json.JSONDecodeError, KeyError):
                    continue

            # If we got this far and found at least one score, return it
            if result['tomatometer'] != 'N/A' or result['popcornmeter'] != 'N/A':
                return result

        except requests.RequestException:
            continue

    return result


def get_letterboxd_rating(title: str, year: str) -> str:
    """
    Scrape Letterboxd rating for a movie.
    Returns rating as percentage (0-100) or 'N/A'.
    """
    # Format title for Letterboxd URL (lowercase, hyphens, no special chars)
    lb_title = title.lower().replace(' ', '-').replace(':', '').replace("'", '').replace('.', '')
    lb_title = re.sub(r'[^\w-]', '', lb_title)

    # Try common URL patterns
    url_patterns = [
        f"https://letterboxd.com/film/{lb_title}/",
        f"https://letterboxd.com/film/{lb_title}-{year}/",
    ]

    for url in url_patterns:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                continue

            html = response.text

            # Look for rating in meta tag
            rating_pattern = r'<meta name="twitter:data2" content="([\d.]+) out of 5"'
            match = re.search(rating_pattern, html)

            if match:
                rating_5 = float(match.group(1))
                # Convert from 5-star to percentage
                rating_pct = round((rating_5 / 5.0) * 100)
                return f"{rating_pct}%"

        except requests.RequestException:
            continue

    return 'N/A'


def get_cinemascore(title: str, year: str) -> str:
    """
    Fetch CinemaScore from CinemaScore's public API.
    Returns letter grade (A+, A, B+, etc.) or 'N/A'.
    """
    try:
        # Try to search for the movie using their search API
        # Base64 encode the search term
        import base64
        search_term = base64.b64encode(title.encode()).decode()
        search_url = f"https://webapp.cinemascore.com/guest/search/title/{search_term}"

        response = requests.get(search_url, timeout=10)
        if response.status_code != 200:
            return 'N/A'

        data = response.json()

        # Look for a match with the same title and year
        for movie in data:
            movie_title = movie.get('TITLE', '').upper()
            movie_year = str(movie.get('YEAR', ''))
            grade = movie.get('GRADE', 'N/A')

            # Check if title matches (case insensitive) and year matches
            if title.upper() in movie_title and movie_year == year:
                return grade
            # Also try exact match on normalized title
            if movie_title.replace(':', '').replace("'", '') == title.upper().replace(':', '').replace("'", ''):
                if movie_year == year:
                    return grade

        # If no exact match found but we have results, try first result if year matches
        if data and len(data) > 0:
            first = data[0]
            if str(first.get('YEAR', '')) == year:
                return first.get('GRADE', 'N/A')

        return 'N/A'

    except (requests.RequestException, json.JSONDecodeError, KeyError):
        return 'N/A'


def format_ratings_text(movies: List[Dict], normalize: bool = False) -> str:
    """Format movie ratings as plain text string."""
    if not movies:
        return "No movies to display."

    output = []
    output.append("\n" + "="*80)
    output.append("Latest Movie Releases".center(80))
    output.append("="*80 + "\n")

    for i, movie in enumerate(movies, 1):
        # Title
        output.append(f"{movie['title']}")

        # Written by • Directed by • Produced by
        output.append(f"Written by: {movie.get('writer', 'N/A')} • Directed by: {movie.get('director', 'N/A')} • Produced by: {movie.get('producer', 'N/A')}")

        # Starring
        output.append(f"Starring: {movie.get('actors', 'N/A')}")

        # Release date
        release_date = movie.get('release_date', 'N/A')
        release_type = movie.get('release_type', 'N/A')
        output.append(f"Release: {release_date} ({release_type})")

        # Genres • Runtime • MPA Rating
        genres = movie.get('genres', 'N/A')
        runtime = movie.get('runtime', 'N/A')
        rating = movie.get('mpa_rating', 'NR')
        output.append(f"Genres: {genres} • {runtime} • {rating}")

        # Studio
        output.append(f"Studio: {movie.get('studio', 'N/A')}")

        # Logline/Overview
        overview = movie.get('overview', 'N/A')
        if len(overview) > 200:
            overview = overview[:197] + '...'
        output.append(f"Logline: {overview}")

        # Separator
        output.append("---")

        # Helper to format ratings
        def fmt(value, default='-'):
            v = str(value) if value else default
            return default if v == 'N/A' else v

        # Ratings
        output.append(f"imdb: {fmt(movie.get('imdb_rating'))}")
        output.append(f"tomato: {fmt(movie.get('tomatometer'))}")
        output.append(f"popcorn: {fmt(movie.get('popcornmeter'))}")
        output.append(f"meta: {fmt(movie.get('metacritic'))}")
        output.append(f"tmdb: {fmt(movie.get('tmdb_rating'))}")
        output.append(f"cinemascore: {fmt(movie.get('cinemascore'))}")
        output.append(f"boxd: {fmt(movie.get('letterboxd'))}")

        # Add spacing between movies
        if i < len(movies):
            output.append("\n" + "="*80 + "\n")

    return "\n".join(output) + "\n"


def format_ratings_html(movies: List[Dict], normalize: bool = False) -> str:
    """Format movie ratings as HTML string."""
    if not movies:
        return "<p>No movies to display.</p>"

    html = []
    html.append("""
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .movie { margin-bottom: 30px; padding: 15px; border-bottom: 2px solid #ddd; }
            .title { font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
            .info { color: #666; font-size: 14px; margin: 5px 0; }
            .ratings { margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee; }
            .rating { display: inline-block; margin-right: 15px; font-size: 14px; }
            .rating-label { font-weight: bold; color: #555; }
        </style>
    </head>
    <body>
        <h1>Latest Movie Releases</h1>
    """)

    for movie in movies:
        html.append('<div class="movie">')
        html.append(f'<div class="title">{movie["title"]}</div>')
        
        # Movie info
        html.append(f'<div class="info">Written by: {movie.get("writer", "N/A")} • Directed by: {movie.get("director", "N/A")} • Produced by: {movie.get("producer", "N/A")}</div>')
        html.append(f'<div class="info">Starring: {movie.get("actors", "N/A")}</div>')
        
        release_date = movie.get('release_date', 'N/A')
        release_type = movie.get('release_type', 'N/A')
        html.append(f'<div class="info">Release: {release_date} ({release_type})</div>')
        
        genres = movie.get('genres', 'N/A')
        runtime = movie.get('runtime', 'N/A')
        rating = movie.get('mpa_rating', 'NR')
        html.append(f'<div class="info">Genres: {genres} • {runtime} • {rating}</div>')
        html.append(f'<div class="info">Studio: {movie.get("studio", "N/A")}</div>')
        
        overview = movie.get('overview', 'N/A')
        if len(overview) > 200:
            overview = overview[:197] + '...'
        html.append(f'<div class="info">Logline: {overview}</div>')
        
        # Ratings
        html.append('<div class="ratings">')
        
        def fmt(value, default='-'):
            v = str(value) if value else default
            return default if v == 'N/A' else v
        
        ratings = [
            ('imdb', movie.get('imdb_rating')),
            ('tomato', movie.get('tomatometer')),
            ('popcorn', movie.get('popcornmeter')),
            ('meta', movie.get('metacritic')),
            ('tmdb', movie.get('tmdb_rating')),
            ('cinemascore', movie.get('cinemascore')),
            ('boxd', movie.get('letterboxd'))
        ]
        
        for label, value in ratings:
            html.append(f'<span class="rating"><span class="rating-label">{label}:</span> {fmt(value)}</span>')
        
        html.append('</div>')
        html.append('</div>')

    html.append("</body></html>")
    return "\n".join(html)


def send_email(movies: List[Dict], normalize: bool = False):
    """Send movie ratings via email using Gmail SMTP."""
    gmail_user = os.getenv('GMAIL_USER', '')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD', '')
    recipient = os.getenv('RECIPIENT_EMAIL', gmail_user)

    if not gmail_user or not gmail_password:
        print("Warning: Email credentials not set. Skipping email send.")
        return False

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Movie Ratings - {datetime.now().strftime("%B %d, %Y")}'
        msg['From'] = gmail_user
        msg['To'] = recipient

        # Create plain text and HTML versions
        text_content = format_ratings_text(movies, normalize)
        html_content = format_ratings_html(movies, normalize)

        # Attach parts
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(gmail_user, gmail_password)
            server.send_message(msg)

        print(f"\nEmail sent successfully to {recipient}")
        return True

    except Exception as e:
        print(f"\nError sending email: {e}")
        return False


def display_ratings(movies: List[Dict], normalize: bool = False):
    """Display movie ratings in sequential text format."""
    text = format_ratings_text(movies, normalize)
    print(text)


def main():
    """Main execution flow."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Movie Ratings Checker - Fetch and compare ratings from multiple sources'
    )
    parser.add_argument(
        '-n', '--normalize',
        action='store_true',
        help='Normalize all scores to 0-100 scale (removes %%, /10, /100 suffixes)'
    )
    parser.add_argument(
        '--email',
        action='store_true',
        help='Send results via email (requires GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL env vars)'
    )
    args = parser.parse_args()

    print("Movie Ratings Checker")
    print("Fetching latest movie releases...\n")

    # Check for API keys
    check_api_keys()

    # Get latest releases from TMDB
    movies = get_latest_releases(limit=15)

    if not movies:
        print("Failed to fetch movies from TMDB.")
        return

    print(f"Found {len(movies)} movies. Fetching ratings...\n")

    # Enrich with ratings and details from various sources
    for i, movie in enumerate(movies):
        print(f"Processing {i+1}/{len(movies)}: {movie['title']} ({movie['year']})...", end=' ')

        # Get detailed movie info from TMDB
        details = get_movie_details(movie['id'])
        movie.update(details)

        # Get IMDB and Metacritic from OMDb
        omdb_data = get_omdb_ratings(movie['title'], movie['year'])
        movie['imdb_rating'] = omdb_data['imdb_rating']
        movie['metacritic'] = omdb_data['metacritic']

        # Get Tomatometer and Popcornmeter from Rotten Tomatoes
        rt_scores = get_rt_scores(movie['title'], movie['year'])
        movie['tomatometer'] = rt_scores['tomatometer']
        movie['popcornmeter'] = rt_scores['popcornmeter']

        # Get CinemaScore from CinemaScore API
        movie['cinemascore'] = get_cinemascore(movie['title'], movie['year'])

        # Get Letterboxd rating
        movie['letterboxd'] = get_letterboxd_rating(movie['title'], movie['year'])

        print("Done")

    # Display results
    display_ratings(movies, normalize=args.normalize)

    # Send email if requested
    if args.email:
        send_email(movies, normalize=args.normalize)


if __name__ == '__main__':
    main()
