"""Main entry point for Rotten Tomatoes scraper."""

import os
import sys

from .emailer import send_email, should_send_email
from .formatter import format_output
from .scraper import scrape_movies


def main():
    """Main function to orchestrate scraping and output."""
    try:
        # Scrape movies
        movies = scrape_movies()

        # Format output
        output = format_output(movies, include_footer=True)

        # Check if email should be sent
        send_email_flag = os.getenv("SEND_EMAIL", "false").lower() == "true"
        recipient_email = os.getenv("RECIPIENT_EMAIL")

        if send_email_flag and recipient_email:
            # Send email
            try:
                send_email(output, recipient_email)
            except Exception as e:
                print(f"Warning: Failed to send email: {e}", file=sys.stderr)
                # Continue to print to console even if email fails
                print(output)
                return 1
        else:
            # Print to console
            print(output)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

