"""Main entry point for Rotten Tomatoes scraper."""

import sys

from .formatter import format_output
from .scraper import scrape_movies


def main():
    """Main function to orchestrate scraping and output."""
    try:
        # Scrape movies
        movies = scrape_movies()

        # Format output
        output = format_output(movies, include_footer=True)

        # Print to console
        print(output)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

