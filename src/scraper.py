"""Core scraping logic for Rotten Tomatoes."""

import re
import time

import requests

# Selenium imports (optional, for JavaScript rendering)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from .config import REQUEST_RETRIES, REQUEST_TIMEOUT, RT_OPENING_URL


def fetch_page_with_selenium(url: str) -> str:
    """Fetch HTML content using Selenium to render JavaScript."""
    if not SELENIUM_AVAILABLE:
        raise Exception("Selenium is not available. Install it with: pip install selenium webdriver-manager")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        # Wait for page to load (wait for any element that indicates content loaded)
        time.sleep(3)  # Give JavaScript time to execute
        html = driver.page_source
        return html
    finally:
        driver.quit()


def fetch_page(url: str) -> str | None:
    """Fetch HTML content from URL with retry logic.
    
    First tries requests, then falls back to Selenium if needed.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
    }

    last_error = None
    for attempt in range(REQUEST_RETRIES):
        try:
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            # RT sometimes returns 404 but still serves content, so check if we got content
            if response.status_code == 404 and len(response.text) > 1000:
                # Likely a false 404, return the content anyway
                return response.text
            response.raise_for_status()
            return response.text
        except requests.exceptions.Timeout as e:
            last_error = f"Request timeout: {e}"
            if attempt < REQUEST_RETRIES - 1:
                continue
        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection error: {e}"
            if attempt < REQUEST_RETRIES - 1:
                continue
        except requests.exceptions.HTTPError as e:
            last_error = f"HTTP error {e.response.status_code}: {e}"
            # Don't retry on 4xx errors
            raise Exception(last_error)
        except requests.exceptions.RequestException as e:
            last_error = f"Request error: {e}"
            if attempt < REQUEST_RETRIES - 1:
                continue

    # If requests failed, try Selenium as fallback
    try:
        return fetch_page_with_selenium(url)
    except Exception as selenium_error:
        raise Exception(f"Failed to fetch page after {REQUEST_RETRIES} attempts and Selenium fallback: {last_error}. Selenium error: {selenium_error}")


def extract_json_data(html: str) -> list[dict]:
    """Extract movie data from embedded JSON in HTML.
    
    Uses the same regex pattern as the old bash script:
    - Find "id":[0-9]{9,9} followed by exactly 225 characters
    - Then look for "tomatoScore":[0-9]{1,3} within that region
    - Extract title, scores from that matched region
    """
    movies = []

    # Use the exact pattern from the old bash script
    # Pattern: "id":[0-9]{9,9} followed by exactly 225 characters, then tomatoScore
    # The old script: egrep -o "\"id\"\:[0-9]{9,9}.{225,225}" | egrep "\"tomatoScore\"\:[0-9]{1,3}"
    # Note: {225,225} means exactly 225 characters, the ? makes it non-greedy but doesn't change exact match
    pattern = r'"id"\s*:\s*(\d{9}).{225}"tomatoScore"\s*:\s*(\d{1,3})'
    matches = re.finditer(pattern, html)

    for match in matches:
        movie_id = match.group(1)
        tomato_score = int(match.group(2))

        # Extract the matched region (id + 225 chars)
        match_region = match.group(0)

        # Remove synopsis and everything after (like the old script: sed 's/synopsis.*//')
        match_region = re.sub(r'synopsis.*', '', match_region)

        # Extract title: "title":"...","url"
        title_match = re.search(r'"title"\s*:\s*"([^"]{2,64})"\s*,\s*"url"', match_region)
        if not title_match:
            continue
        title = title_match.group(1)

        # Extract popcorn score: "popcornScore":[0-9]{1,3},"theaterReleaseDate"
        popcorn_match = re.search(r'"popcornScore"\s*:\s*(\d{1,3})\s*,\s*"theaterReleaseDate"', match_region)
        popcorn_score = int(popcorn_match.group(1)) if popcorn_match else 0

        # Extract URL if available
        url_match = re.search(r'"url"\s*:\s*"([^"]+)"', match_region)
        movie_url = url_match.group(1) if url_match else None

        movies.append({
            "id": movie_id,
            "title": title,
            "tomatoScore": tomato_score,
            "popcornScore": popcorn_score,
            "url": movie_url,
        })

    return movies


def scrape_movies() -> list[dict]:
    """Main function to scrape movies from Rotten Tomatoes."""
    try:
        # Try requests first, fall back to Selenium if needed
        html = fetch_page(RT_OPENING_URL)
    except Exception as e:
        raise Exception(f"Failed to fetch Rotten Tomatoes page: {e}")

    try:
        movies = extract_json_data(html)
    except Exception as e:
        raise Exception(f"Failed to parse movie data: {e}")

    if not movies:
        # If no movies found with requests, try Selenium
        try:
            html = fetch_page_with_selenium(RT_OPENING_URL)
            movies = extract_json_data(html)
        except Exception as selenium_error:
            raise Exception(f"No movie data found on page. Tried both requests and Selenium. Selenium error: {selenium_error}")

    if not movies:
        raise Exception("No movie data found on page. The page structure may have changed.")

    return movies

