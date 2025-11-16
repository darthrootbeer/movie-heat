"""Formatting logic for movie scores and output."""


from .config import SCORE_THRESHOLD


def get_tomato_icon(score: int) -> str:
    """Get emoji icon for tomato score."""
    if score <= SCORE_THRESHOLD:
        return "🤢"
    return "🍅"


def get_popcorn_icon(score: int) -> str:
    """Get emoji icon for popcorn score."""
    if score <= 0:
        return "--"
    elif score <= SCORE_THRESHOLD:
        return "👎🏻"
    return "🍿"


def format_score(score: int) -> str:
    """Format score with proper padding and zero handling."""
    # Convert 0 to "00" for better sorting
    if score == 0:
        return "00"

    # Add trailing space for scores ≤99 to match 100 score width
    if score <= 99:
        return f"{score} "

    return str(score)


def format_movie_line(movie: dict) -> str:
    """Format a single movie entry matching the old script format."""
    # Extract scores, defaulting to 0 if missing
    try:
        tomato_score = int(movie.get("tomatoScore", 0) or 0)
    except (ValueError, TypeError):
        tomato_score = 0

    try:
        popcorn_score = int(movie.get("popcornScore", 0) or 0)
    except (ValueError, TypeError):
        popcorn_score = 0

    # Ensure scores are within valid range
    tomato_score = max(0, min(100, tomato_score))
    popcorn_score = max(0, min(100, popcorn_score))

    # Get icons
    tomato_icon = get_tomato_icon(tomato_score)
    popcorn_icon = get_popcorn_icon(popcorn_score)

    # Format scores
    tomato_formatted = format_score(tomato_score)
    popcorn_formatted = format_score(popcorn_score)

    # Get title and process ampersands (like old script)
    title = movie.get("title", "Unknown")
    title = title.replace("&", "and")

    # Format: 🍅 98  |  🍿 97  -  Movie Title
    return f"{tomato_icon} {tomato_formatted} |  {popcorn_icon} {popcorn_formatted} -  {title}"


def format_output(movies: list[dict], include_footer: bool = True) -> str:
    """Format complete output with header and optional footer."""
    from .config import OUTPUT_FOOTER_LINK, OUTPUT_HEADER

    lines = [OUTPUT_HEADER]
    lines.append("")  # Empty line after header

    # Format each movie
    for movie in movies:
        lines.append(format_movie_line(movie))

    # Add footer if requested
    if include_footer:
        lines.append("")
        lines.append(f"Link: {OUTPUT_FOOTER_LINK}")

    return "\n".join(lines)

