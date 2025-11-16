# Movie Heat

A Python scraper for Rotten Tomatoes "Opening This Week" movies that sends weekly email newsletters every Thursday at 12 noon Eastern.

## How It Works

1. **Scraping**: Fetches movie data from Rotten Tomatoes using regex pattern matching (same approach as the original bash scripts)
2. **Formatting**: Formats scores with emoji indicators (🍅 for good scores, 🤢 for bad)
3. **Email**: Sends formatted results via Gmail SMTP
4. **Scheduling**: Runs automatically via GitHub Actions every Thursday at 12:00 PM Eastern

## Features

- Scrapes "Opening This Week" movies from Rotten Tomatoes
- Extracts tomato scores (Tomatometer) and popcorn scores (Audience Score)
- Formats output with emoji indicators matching the original script format
- Email delivery via Gmail SMTP
- Automated weekly scheduling via GitHub Actions
- Error handling and retry logic
- Optional Selenium support for JavaScript-rendered content

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Local Console Output

```bash
python3 rt_scraper.py
```

### Email Delivery

Set environment variables and run:

```bash
export GMAIL_USER="your-email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="recipient@example.com"
export SEND_EMAIL="true"
python3 rt_scraper.py
```

**Gmail Setup**: You need a Gmail App Password (not your regular password):
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: Google Account → Security → App Passwords
3. Use the 16-character app password as `GMAIL_APP_PASSWORD`

## Output Format

```
🍅 Rotten Tomatoes Opening This Week

🍅 98  |  🍿 97  -  Movie Title
🤢 45  |  🍿 62  -  Another Movie
🍅 85  |  -- 00  -  Movie Without Popcorn Score

Link: https://bit.ly/2A0na2e
```

**Score Icons**:
- Tomato: 🍅 if >59, 🤢 if ≤59
- Popcorn: 🍿 if >59, 👎🏻 if 1-59, "--" if 0

## GitHub Actions Setup

The project includes a GitHub Actions workflow that runs every Thursday at 12:00 PM Eastern.

### Required Secrets

Set these in your GitHub repository settings (Settings → Secrets and variables → Actions):

- `GMAIL_USER`: Your Gmail address
- `GMAIL_APP_PASSWORD`: Your Gmail app password (16 characters)
- `RECIPIENT_EMAIL`: Email address to send newsletters to

### Workflow File

The workflow is defined in `.github/workflows/weekly-newsletter.yml` and runs:
- Every Thursday at 17:00 UTC (12:00 PM Eastern)
- Can be manually triggered via `workflow_dispatch`

## Project Structure

```
movie-heat/
├── src/
│   ├── config.py      # Configuration settings
│   ├── scraper.py     # Core scraping logic
│   ├── formatter.py   # Score formatting and emoji logic
│   ├── emailer.py     # Email sending functionality
│   └── main.py        # Entry point
├── .github/
│   └── workflows/
│       └── weekly-newsletter.yml  # GitHub Actions workflow
├── tests/             # Unit tests
├── rt_scraper.py      # Command-line script
└── requirements.txt   # Python dependencies
```

## Configuration

Edit `src/config.py` to customize:
- `RT_OPENING_URL`: Rotten Tomatoes URL to scrape
- `SCORE_THRESHOLD`: Score threshold for emoji icons (default: 59)
- `REQUEST_TIMEOUT`: HTTP request timeout (default: 30 seconds)
- `REQUEST_RETRIES`: Number of retry attempts (default: 3)

## Testing

```bash
pytest tests/ -v
```

## Known Limitations

Rotten Tomatoes loads movie data dynamically via JavaScript. The scraper:
1. First tries `requests` library
2. Falls back to Selenium if needed (requires Chrome/Chromium)
3. Uses regex pattern matching (same as original bash scripts)

If scraping fails, RT's page structure may have changed.

## License

This project is for personal use. Please respect Rotten Tomatoes' Terms of Service when scraping.
