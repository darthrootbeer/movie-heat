# AI Instructions for Movie Heat Project

This document provides context and guidance for AI assistants working on this project.

## Project Overview

Movie Heat is a Python scraper that fetches "Opening This Week" movie scores from Rotten Tomatoes and sends weekly email newsletters every Thursday at 12:00 PM Eastern via GitHub Actions.

## Architecture

### Core Components

1. **`src/scraper.py`**: Fetches HTML from Rotten Tomatoes and extracts movie data using regex patterns
2. **`src/formatter.py`**: Formats movie scores with emoji icons and proper padding
3. **`src/emailer.py`**: Sends formatted results via Gmail SMTP
4. **`src/main.py`**: Orchestrates scraping, formatting, and optional email sending
5. **`src/config.py`**: Centralized configuration settings

### Data Flow

```
Rotten Tomatoes URL → scraper.py → List[Dict] → formatter.py → Formatted String → emailer.py → Email
                                                                                      ↓
                                                                              Console Output
```

### Key Design Decisions

1. **Regex Pattern Matching**: Uses the same fragile regex pattern as the original bash scripts (`"id":[9 digits].{225}"tomatoScore"`). This is intentional to maintain compatibility but makes the scraper brittle.

2. **Dual Fetching Strategy**: 
   - First tries `requests` library (fast, no browser needed)
   - Falls back to Selenium if needed (handles JavaScript-rendered content)
   - This handles RT's dynamic content loading

3. **Email vs Console**: Controlled via environment variables:
   - `SEND_EMAIL=true` + `RECIPIENT_EMAIL` → sends email
   - Otherwise → prints to console

4. **Scheduling**: Handled by GitHub Actions cron, not application code. The `should_send_email()` function exists but isn't actively used.

## File Structure

```
movie-heat/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration constants
│   ├── scraper.py         # Web scraping logic
│   ├── formatter.py       # Output formatting
│   ├── emailer.py         # Email sending
│   └── main.py            # Entry point
├── tests/
│   ├── test_config.py
│   ├── test_formatter.py
│   ├── test_scraper.py
│   └── test_emailer.py
├── .github/
│   └── workflows/
│       └── weekly-newsletter.yml  # GitHub Actions workflow
├── rt_scraper.py          # CLI entry point
├── requirements.txt       # Python dependencies
├── pytest.ini            # Pytest configuration
├── pyproject.toml        # Tool configurations (black, ruff, mypy)
├── README.md             # User-facing documentation
├── ARCHITECT.md          # Architecture documentation
├── TODO.md               # Task tracking
└── VERSION               # Current version (SEMVER)
```

## Development Patterns

### Testing

- **Test-Driven Development**: Write tests for every new function before implementation
- **Test Location**: All tests in `tests/` directory mirroring `src/` structure
- **Test Naming**: `test_<module_name>.py` for module tests
- **Coverage**: Aim for comprehensive coverage, especially for core scraping logic

### Code Quality

- **Formatting**: Use `black` (configured in `pyproject.toml`)
- **Linting**: Use `ruff` (configured in `pyproject.toml`)
- **Type Checking**: Use `mypy` (configured in `pyproject.toml`)
- **Run checks**: `ruff check .`, `black .`, `mypy src/`

### Version Control

- **Branching**: Use `master` branch (no feature branches currently)
- **Commits**: Make commits for significant changes
- **Versioning**: SEMVER format in `VERSION` file
- **Tags**: Tag releases (e.g., `v0.2.0`)

### Dependencies

- **Core**: `requests`, `beautifulsoup4`, `lxml`, `selenium`, `webdriver-manager`, `pytz`
- **Testing**: `pytest`, `pytest-cov`
- **Dev Tools**: `black`, `ruff`, `mypy`

## Common Tasks

### Adding a New Feature

1. Create/update TODO in `TODO.md`
2. Write tests first (TDD approach)
3. Implement feature
4. Run tests: `pytest tests/ -v`
5. Fix linting: `ruff check . --fix`
6. Format code: `black .`
7. Commit with descriptive message
8. Update version if needed
9. Update README if user-facing

### Debugging Scraper Issues

1. **No movies found**: 
   - Check if RT page structure changed
   - Try Selenium fallback manually
   - Verify regex pattern still matches HTML structure
   - Check network connectivity

2. **Email not sending**:
   - Verify `GMAIL_USER` and `GMAIL_APP_PASSWORD` are set
   - Check Gmail app password is correct (16 characters)
   - Verify `RECIPIENT_EMAIL` is set
   - Check `SEND_EMAIL=true` is set

3. **GitHub Actions failing**:
   - Check secrets are configured in repo settings
   - Verify workflow file syntax
   - Check action logs for specific errors

### Extending the Project

#### Adding New Score Sources

1. Create new scraper function in `src/scraper.py`
2. Update movie dict structure if needed
3. Update `src/formatter.py` to handle new scores
4. Add tests for new functionality
5. Update `src/config.py` if new URLs/config needed

#### Adding New Output Formats

1. Add formatter function in `src/formatter.py`
2. Update `src/main.py` to support format selection
3. Add tests
4. Update README

#### Adding New Categories

1. Add URL to `src/config.py`
2. Update scraper to handle multiple categories
3. Update formatter to distinguish categories
4. Add tests
5. Update README

## Important Notes

### Regex Pattern Fragility

The regex pattern `"id":[9 digits].{225}"tomatoScore"` is very fragile:
- Requires exactly 225 characters between ID and tomatoScore
- Test data must precisely match this pattern
- If RT changes their HTML structure, this will break
- Consider this when modifying `extract_json_data()` in `scraper.py`

### Selenium Requirements

- Chrome/Chromium must be installed for Selenium to work
- ChromeDriver is auto-downloaded by `webdriver-manager`
- Selenium is optional (scraper falls back to it if requests fails)
- GitHub Actions runners have Chrome pre-installed

### Environment Variables

**For Local Development:**
- `GMAIL_USER`: Gmail address (optional, for email)
- `GMAIL_APP_PASSWORD`: Gmail app password (optional, for email)
- `RECIPIENT_EMAIL`: Email recipient (optional, for email)
- `SEND_EMAIL`: Set to "true" to enable email (optional)

**For GitHub Actions:**
- Set as repository secrets (Settings → Secrets and variables → Actions)
- Same variables as above

### Timezone Handling

- GitHub Actions cron uses UTC
- 12:00 PM Eastern = 17:00 UTC (during DST) or 16:00 UTC (standard time)
- Workflow uses 17:00 UTC as compromise
- `pytz` library handles timezone conversions in code

## Testing Patterns

### Mocking External Dependencies

- **Network calls**: Use `@patch('src.scraper.requests.get')` or `@patch('src.scraper.fetch_page')`
- **Email sending**: Use `@patch('src.emailer.smtplib.SMTP')`
- **DateTime**: Use `@patch('src.emailer.datetime')` (but be careful with timezone-aware datetimes)

### Test Data Construction

For scraper tests, test data must precisely match the regex pattern:
```python
movie_id = "123456789"
data_part = ',"title":"Test Movie","url":"/m/test","popcornScore":90,"theaterReleaseDate":"Jan 1"'
remaining = 225 - len(data_part)
full_225 = data_part + 'x' * remaining
post_tomato = '"tomatoScore":85,"popcornIcon":"upright"'
html = f'"id":{movie_id}{full_225}{post_tomato}'
```

## Code Style Guidelines

- **Type Hints**: Use type hints for all function signatures
- **Docstrings**: Use Google-style docstrings for all functions
- **Line Length**: 100 characters (configured in `pyproject.toml`)
- **Imports**: Group imports: stdlib, third-party, local
- **Error Handling**: Use try/except with descriptive error messages
- **Constants**: Use UPPER_CASE for constants in `config.py`

## Future Enhancements (from TODO.md)

- Add Cinemascore scores for each movie (`000001`)
- Add IMDB scores for each movie (`000002`)

When implementing these:
1. Research API/endpoints for these services
2. Add new scraper functions
3. Update movie dict structure
4. Update formatter to display new scores
5. Add comprehensive tests
6. Update README

## Questions to Ask

If you're unsure about something:

1. **Should I modify the regex pattern?** → Probably not, unless RT structure changed
2. **Should I add a new dependency?** → Check if it's necessary, update `requirements.txt`
3. **Should I change the output format?** → Check if it matches original script format
4. **Should I modify the email template?** → Yes, but keep it readable and professional
5. **Should I add error handling?** → Yes, always add error handling for external calls

## Key Files to Read First

1. `src/scraper.py` - Understand the scraping logic
2. `src/formatter.py` - Understand output formatting
3. `tests/test_scraper.py` - See how regex pattern matching works
4. `.github/workflows/weekly-newsletter.yml` - Understand GitHub Actions setup
5. `README.md` - User-facing documentation

## Common Commands

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Format code
black .

# Lint code
ruff check . --fix

# Type check
mypy src/

# Run scraper locally (console output)
python3 rt_scraper.py

# Run scraper with email
SEND_EMAIL=true RECIPIENT_EMAIL=test@example.com python3 rt_scraper.py
```

## Version History

- `0.2.0`: Added email functionality and GitHub Actions workflow
- `0.1.1`: Fixed tests, added development tools
- `0.1.0`: Initial release with scraping and formatting

## Contact & Resources

- Repository: https://github.com/darthrootbeer/movie-heat
- Original bash scripts: See `old/` directory (for reference only)
- Rotten Tomatoes: https://www.rottentomatoes.com

---

**Last Updated**: 2025-01-27
**Maintainer**: See git commit history

