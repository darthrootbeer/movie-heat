# Movie Heat

A Python tool that fetches movie ratings from multiple sources and formats them for email delivery. Currently in transition from v1.0 (multi-API approach) to v2.0 (single MDB List API source).

## Version 2.0 (In Development)

Version 2.0 uses the MDB List API as a single source for all movie ratings and metadata, eliminating the need for multiple API calls and web scraping. The output is formatted as an HTML email matching the MDB List website's card layout.

### MVP Status

- ✅ HTML layout matching MDB List design
- ✅ Two-column responsive grid
- ✅ Color-coded ratings with clickable source links
- 🚧 API endpoint discovery (currently using sample data)
- 🚧 Email-safe HTML formatting

Run the MVP: `python3 mdb_mvp.py` (generates `movies_preview.html`)

## Version 1.0 (Stable)

A minimal Python script that fetches the latest movie releases and displays ratings from multiple sources in a clean comparison table.

## Rating Sources

- **IMDB**: Industry-standard ratings (x/10)
- **Rotten Tomatoes - Tomatometer**: Critics' score (%)
- **Rotten Tomatoes - Audience Score**: General audience rating (%)
- **TMDB**: The Movie Database community rating (x/10)
- **CinemaScore**: Opening night audience poll grade (A+, A, B+, etc.)

## Features

- Minimal dependencies (only `requests`)
- Fast and lean (~200 lines of code)
- Clean terminal output
- Free API tier usage
- Automatic fallback to "N/A" for missing ratings

## Requirements

- Python 3.6+
- `requests` library

## Setup

### 1. Install Dependencies

**Option A: Using a Virtual Environment (Recommended)**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install requests
pip install requests
```

**Option B: System-wide Installation**

```bash
pip install requests
# or
pip3 install requests --user
```

### 2. Get Free API Keys

You'll need two free API keys:

#### TMDB (The Movie Database)
1. Create a free account at https://www.themoviedb.org/
2. Go to https://www.themoviedb.org/settings/api
3. Request an API key (choose "Developer" option)
4. Copy your API key (v3 auth)

#### OMDb (Open Movie Database)
1. Go to http://www.omdbapi.com/apikey.aspx
2. Select the FREE tier (1,000 daily requests)
3. Enter your email and activate your key
4. Copy your API key from the confirmation email

### 3. Configure API Keys

Set your API keys as environment variables:

```bash
export TMDB_API_KEY='your_tmdb_api_key_here'
export OMDB_API_KEY='your_omdb_api_key_here'
```

Or create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
# Edit .env and add your API keys
```

If using a `.env` file, load it before running:

```bash
export $(cat .env | xargs)
```

## Usage

If using a virtual environment, activate it first:

```bash
source venv/bin/activate  # On macOS/Linux
```

Then run the script:

```bash
python movie_ratings.py
```

Or make it executable and run directly:

```bash
chmod +x movie_ratings.py
./movie_ratings.py
```

## Example Output

```
Movie Ratings Checker
Fetching latest movie releases...

Found 15 movies. Fetching ratings...

Processing 1/15: Dune: Part Two (2024)... Done
Processing 2/15: Poor Things (2024)... Done
...

====================================================================================================
                               Latest Movie Releases - Ratings Comparison
====================================================================================================

Movie Title                    Year  IMDB     RT-Critics  RT-Audience  TMDB     CinemaScore
----------------------------------------------------------------------------------------------------
Dune: Part Two                 2024  8.5/10   92%         95%          8.2      A
Poor Things                    2024  7.9/10   87%         73%          7.8      B
The Zone of Interest           2024  7.5/10   93%         68%          7.4      N/A
...
```

## How It Works

1. **Fetches latest releases** from TMDB API
2. **Queries OMDb** for each movie to get IMDB and both Rotten Tomatoes scores
3. **Scrapes Wikipedia** to find CinemaScore grades (when available)
4. **Displays results** in a formatted table

## Limitations

- **CinemaScore**: No public API available, so we scrape from Wikipedia. Not all movies have CinemaScore grades, especially smaller releases.
- **Rotten Tomatoes**: Both scores come via OMDb, which may not always have complete data for very recent releases.
- **API Limits**: TMDB free tier allows 50 requests/second. OMDb free tier allows 1,000 requests/day.
- **Title Matching**: Occasionally, movies with special characters or alternate titles may not match perfectly between services.

## Troubleshooting

### "Error: Missing required API keys"
Make sure you've set both `TMDB_API_KEY` and `OMDB_API_KEY` environment variables.

### "Failed to fetch movies from TMDB"
- Check your TMDB API key is valid
- Verify you have internet connectivity
- Ensure you haven't exceeded API rate limits

### Most ratings show "N/A"
- Check your OMDb API key is valid and activated
- For very recent releases, ratings may not be available yet
- CinemaScore is only assigned to major theatrical releases

## License

Free to use and modify.
