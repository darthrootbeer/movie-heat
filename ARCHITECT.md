# Architecture

## Overview

Movie Heat is a Python-based scraper for Rotten Tomatoes movie scores. It replaces the old bash-based regex scraping scripts with a more maintainable, modular Python implementation.

## System Architecture

### Components

```
movie-heat/
├── src/
│   ├── config.py      # Configuration and settings
│   ├── scraper.py     # Web scraping logic (requests + Selenium)
│   ├── formatter.py   # Output formatting and emoji logic
│   └── main.py        # Application entry point
├── rt_scraper.py      # CLI executable script
└── requirements.txt   # Python dependencies
```

### Data Flow

1. **Configuration** (`config.py`)
   - Defines RT URL endpoints
   - Score thresholds and formatting rules
   - Request settings (timeout, retries)

2. **Scraping** (`scraper.py`)
   - Fetches HTML from Rotten Tomatoes
   - Attempts requests library first
   - Falls back to Selenium for JavaScript-rendered content
   - Extracts movie data using regex patterns (matching old script)
   - Returns structured movie data (list of dicts)

3. **Formatting** (`formatter.py`)
   - Converts scores to emoji icons based on thresholds
   - Formats scores with proper padding
   - Handles edge cases (missing scores, zero scores)
   - Generates formatted output lines

4. **Output** (`main.py`)
   - Orchestrates scraping and formatting
   - Outputs to console (stdout)
   - Handles errors and exits with appropriate codes

### Key Design Decisions

**Dual Fetching Strategy:**
- Primary: `requests` library for fast HTTP fetching
- Fallback: Selenium for JavaScript-rendered content
- Handles RT's 404-but-serves-content behavior

**Regex-Based Extraction:**
- Maintains compatibility with old script's regex patterns
- Extracts JSON-like data embedded in HTML
- Pattern: `"id":[0-9]{9,9}` followed by 225 chars, then `"tomatoScore"`

**Modular Structure:**
- Separation of concerns (scraping, formatting, config)
- Easy to extend with new data sources (Cinemascore, IMDB)
- Configurable without code changes

**Error Handling:**
- Retry logic for network errors
- Graceful degradation (Selenium fallback)
- Clear error messages

## Future Extensibility

### Adding New Score Sources

To add Cinemascore or IMDB scores:

1. **Extend `scraper.py`:**
   - Add functions to fetch from new sources
   - Parse and extract scores
   - Return structured data

2. **Update `formatter.py`:**
   - Add formatting logic for new scores
   - Update output format to include new columns

3. **Modify `config.py`:**
   - Add URLs/endpoints for new sources
   - Add configuration options

4. **Update data structure:**
   - Movie dicts can include: `cinemascore`, `imdb_score`
   - Formatter handles missing scores gracefully

### Output Format Extensions

Current format:
```
🍅 98  |  🍿 97  -  Movie Title
```

Extended format (example):
```
🍅 98  |  🍿 97  |  A+  |  8.5  -  Movie Title
```

## Dependencies

**Core:**
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `lxml` - HTML parser backend

**Optional:**
- `selenium` - JavaScript rendering (fallback)
- `webdriver-manager` - ChromeDriver management

## Configuration

All configuration is centralized in `src/config.py`:

- `RT_OPENING_URL` - Rotten Tomatoes endpoint
- `SCORE_THRESHOLD` - Emoji threshold (default: 59)
- `REQUEST_TIMEOUT` - HTTP timeout (default: 30s)
- `REQUEST_RETRIES` - Retry attempts (default: 3)

## Error Handling Strategy

1. **Network Errors:**
   - Retry up to `REQUEST_RETRIES` times
   - Different handling for timeout vs connection errors
   - Fallback to Selenium if requests fail

2. **Parsing Errors:**
   - Try multiple extraction methods
   - Graceful handling of missing fields
   - Default values for missing scores

3. **Selenium Errors:**
   - Optional dependency (fails gracefully if not installed)
   - Requires Chrome/Chromium to be installed
   - Timeout protection

## Testing Considerations

- RT's page structure may change (requires regex pattern updates)
- Selenium requires Chrome/Chromium installation
- Network-dependent (requires internet connection)
- Rate limiting: RT may throttle requests

## Performance

- **Requests method:** Fast (~1-2 seconds)
- **Selenium method:** Slower (~5-10 seconds, includes browser startup)
- **Regex extraction:** Efficient for embedded JSON patterns

## Security Considerations

- Respects RT's Terms of Service
- Uses standard User-Agent headers
- No authentication required (public data)
- No sensitive data stored

