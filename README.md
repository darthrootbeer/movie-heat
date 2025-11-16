# Movie Heat - Rotten Tomatoes Scraper

A modernized Python scraper for Rotten Tomatoes "Opening This Week" movies, replacing the old bash-based regex scraping scripts.

## Features

- Scrapes "Opening This Week" movies from Rotten Tomatoes
- Extracts tomato scores and popcorn scores
- Formats output with emoji indicators matching the original script format
- Console output (email support planned for future)
- Error handling and retry logic
- Optional Selenium support for JavaScript-rendered content

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Note: If you need Selenium support (for JavaScript-rendered pages), Chrome/Chromium must be installed on your system. Selenium will automatically download the ChromeDriver.

## Usage

Run the scraper:
```bash
python3 rt_scraper.py
```

Or make it executable and run directly:
```bash
chmod +x rt_scraper.py
./rt_scraper.py
```

## Output Format

The scraper outputs formatted text matching the original script:

```
🍅 Rotten Tomatoes Opening This Week

🍅 98  |  🍿 97  -  Movie Title
🤢 45  |  🍿 62  -  Another Movie
🍅 85  |  -- 00  -  Movie Without Popcorn Score

Link: https://bit.ly/2A0na2e
```

### Score Icons

- **Tomato Score**: 🍅 if >59, 🤢 if ≤59
- **Popcorn Score**: 🍿 if >59, 👎🏻 if 1-59, "--" if 0

## Project Structure

```
movie-heat/
├── src/
│   ├── __init__.py
│   ├── config.py      # Configuration settings
│   ├── scraper.py     # Core scraping logic
│   ├── formatter.py   # Score formatting and emoji logic
│   └── main.py        # Entry point
├── rt_scraper.py      # Command-line script
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Configuration

Edit `src/config.py` to customize:

- `RT_OPENING_URL`: The Rotten Tomatoes URL to scrape
- `SCORE_THRESHOLD`: Score threshold for emoji icons (default: 59)
- `REQUEST_TIMEOUT`: HTTP request timeout (default: 30 seconds)
- `REQUEST_RETRIES`: Number of retry attempts (default: 3)

## Known Limitations

**Important**: Rotten Tomatoes has changed their page structure and now loads movie data dynamically via JavaScript. The scraper includes Selenium support as a fallback, but:

1. Chrome/Chromium must be installed for Selenium to work
2. The regex patterns may need adjustment if RT changes their data format
3. RT may return 404 status codes but still serve content (handled automatically)

If the scraper doesn't find movies, RT's page structure may have changed. Check the error message for details.

## Future Enhancements

- Email delivery support
- Multiple category support (Box Office, Home Releases)
- Pushover notifications
- Configurable output formats
- Caching to reduce API calls

## Migration from Old Scripts

The old bash scripts (`rt_scores_limited.sh`, `rt_top.sh`) used regex to extract JSON data embedded in HTML. This Python version:

- Uses proper JSON parsing where possible
- Falls back to regex matching (same pattern as old script)
- Includes Selenium fallback for JavaScript-rendered content
- Better error handling and logging
- More maintainable code structure

## License

This project is for personal use. Please respect Rotten Tomatoes' Terms of Service when scraping.

