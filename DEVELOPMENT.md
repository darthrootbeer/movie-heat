# Development Guide

This guide is for developers (human and AI) working on the Movie Heat project.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/darthrootbeer/movie-heat.git
cd movie-heat
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run scraper locally
python3 rt_scraper.py
```

## Project Setup

### Prerequisites

- Python 3.13+
- pip
- Chrome/Chromium (for Selenium fallback)
- Git

### Virtual Environment

Always work in a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Development Workflow

### 1. Making Changes

1. **Write tests first** (TDD approach)
2. **Implement feature**
3. **Run tests**: `pytest tests/ -v`
4. **Fix linting**: `ruff check . --fix`
5. **Format code**: `black .`
6. **Type check**: `mypy src/`
7. **Commit**: `git commit -m "descriptive message"`

### 2. Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_scraper.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_scraper.py::TestExtractJsonData::test_extract_movie_with_complete_data -v
```

### 3. Code Quality

```bash
# Format code
black .

# Lint code (auto-fix)
ruff check . --fix

# Type check
mypy src/

# Run all checks
black . && ruff check . --fix && mypy src/ && pytest tests/ -v
```

### 4. Version Management

- Update `VERSION` file with SEMVER format
- Commit version bump separately
- Tag releases: `git tag -a v0.2.0 -m "Release message"`

## Testing the Scraper

### Console Output (Default)

```bash
python3 rt_scraper.py
```

### Email Output (Local Testing)

```bash
export GMAIL_USER="your-email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
export RECIPIENT_EMAIL="recipient@example.com"
export SEND_EMAIL="true"
python3 rt_scraper.py
```

### GitHub Actions Testing

1. Push code to repository
2. Go to Actions tab
3. Select "Weekly Movie Heat Newsletter"
4. Click "Run workflow" → "Run workflow"
5. Monitor logs for errors

## Common Issues

### Scraper Returns No Movies

**Symptoms**: `Error: No movie data found on page`

**Possible Causes**:
1. Rotten Tomatoes page structure changed
2. Network connectivity issues
3. RT blocking requests

**Solutions**:
1. Check RT website manually
2. Verify regex pattern still matches HTML
3. Try Selenium fallback manually
4. Check network/firewall settings

### Email Not Sending

**Symptoms**: Email function fails silently or with error

**Check**:
1. `GMAIL_USER` is set correctly
2. `GMAIL_APP_PASSWORD` is 16-character app password (not regular password)
3. `RECIPIENT_EMAIL` is set
4. `SEND_EMAIL=true` is set
5. Gmail account has 2FA enabled

**Debug**:
```python
# Add debug prints in emailer.py
print(f"Gmail user: {gmail_user}")
print(f"Recipient: {recipient_email}")
```

### Tests Failing

**Common Issues**:
1. **Regex pattern mismatch**: Test data doesn't match exact 225-character pattern
2. **Mocking issues**: DateTime/timezone mocking can be tricky
3. **Import errors**: Make sure virtual environment is activated

**Fix**:
1. Check test data construction matches regex pattern exactly
2. Verify mocks are set up correctly
3. Run `pytest tests/ -v` to see detailed error messages

## Adding New Features

### Example: Adding IMDB Scores

1. **Research**: Find IMDB API or scraping method
2. **Update TODO**: Mark task as in progress
3. **Write Tests**: Create test cases first
4. **Update Scraper**: Add IMDB score extraction
5. **Update Formatter**: Add IMDB score display
6. **Update Config**: Add IMDB-related settings if needed
7. **Run Tests**: Ensure all tests pass
8. **Update README**: Document new feature
9. **Commit**: Make descriptive commit

### Example: Adding New Category

1. **Add URL**: Update `RT_OPENING_URL` or add new URL in `config.py`
2. **Update Scraper**: Modify `scrape_movies()` to handle multiple categories
3. **Update Formatter**: Add category headers in output
4. **Add Tests**: Test new category scraping
5. **Update README**: Document new category

## Code Structure

### Module Responsibilities

- **`config.py`**: All configuration constants
- **`scraper.py`**: Web scraping and data extraction
- **`formatter.py`**: Output formatting and emoji logic
- **`emailer.py`**: Email sending functionality
- **`main.py`**: Orchestration and entry point

### Adding a New Module

1. Create file in `src/`
2. Add `__init__.py` imports if needed
3. Write tests in `tests/test_<module>.py`
4. Update `main.py` to use new module
5. Update README

## Git Workflow

### Commit Messages

Use descriptive commit messages:

```
feat: add email functionality
fix: correct regex pattern matching
test: add emailer tests
docs: update README with setup instructions
chore: bump version to 0.2.0
```

### Branching

Currently using `master` branch directly. For larger features, consider:
- Feature branches: `feature/add-imdb-scores`
- Bug fixes: `fix/regex-pattern`

### Tags

Tag releases:
```bash
git tag -a v0.2.0 -m "v0.2.0: Email functionality added"
git push origin v0.2.0
```

## GitHub Actions

### Workflow File

Located at `.github/workflows/weekly-newsletter.yml`

### Testing Workflow Locally

Use [act](https://github.com/nektos/act) to test GitHub Actions locally:

```bash
# Install act
brew install act  # macOS
# or download from https://github.com/nektos/act/releases

# Test workflow
act -s GMAIL_USER=test@example.com -s GMAIL_APP_PASSWORD=test -s RECIPIENT_EMAIL=test@example.com
```

### Debugging Workflow

1. Check Actions tab in GitHub
2. Click on failed workflow run
3. Expand failed step
4. Check logs for specific errors
5. Verify secrets are set correctly

## Dependencies

### Adding a New Dependency

1. Add to `requirements.txt`
2. Install: `pip install <package>`
3. Update version constraints if needed
4. Test that everything still works
5. Commit changes

### Updating Dependencies

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade requests

# Generate new requirements.txt
pip freeze > requirements.txt
```

## Documentation

### Updating README

- Keep it user-focused
- Include setup instructions
- Document all features
- Keep examples up-to-date

### Updating AI_INSTRUCTIONS.md

- Document new patterns
- Add common issues and solutions
- Update code examples
- Keep architecture diagrams current

### Updating ARCHITECT.md

- Document architectural decisions
- Update component descriptions
- Keep data flow diagrams current

## Performance Considerations

- **Scraping**: Uses retry logic (3 attempts) with 30s timeout
- **Selenium**: Only used as fallback (slower, requires browser)
- **Email**: Synchronous sending (acceptable for weekly newsletter)
- **Caching**: Not currently implemented (could reduce RT requests)

## Security Considerations

- **Secrets**: Never commit secrets to repository
- **Gmail**: Use app passwords, not regular passwords
- **GitHub Actions**: Use repository secrets for sensitive data
- **Dependencies**: Keep dependencies updated for security patches

## Troubleshooting

### Python Version Issues

```bash
# Check Python version
python3 --version  # Should be 3.13+

# Use specific version
python3.13 rt_scraper.py
```

### Virtual Environment Issues

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Import Errors

```bash
# Verify virtual environment is activated
which python  # Should point to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Resources

- [Python Documentation](https://docs.python.org/3/)
- [Pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Rotten Tomatoes](https://www.rottentomatoes.com)

---

**Last Updated**: 2025-01-27

