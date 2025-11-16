"""Configuration settings for Rotten Tomatoes scraper."""

# Rotten Tomatoes browse URL for "Opening This Week"
# Using the same URL as the old script (even if it returns 404, it serves content)
RT_OPENING_URL = (
    "https://www.rottentomatoes.com/browse/opening"
    "?minTomato=0&maxTomato=100"
    "&genres=1;2;4;5;6;8;9;10;11;13;18;14"
    "&sortBy=release"
)

# Score threshold for emoji icons (≤59 = bad, >59 = good)
SCORE_THRESHOLD = 59

# Genre IDs (for reference)
# 1=Action, 2=Animation, 4=Comedy, 5=Documentary, 6=Drama, 8=Horror,
# 9=Kids & Family, 10=Mystery & Suspense, 11=Romance, 13=Sci-Fi, 18=Thriller, 14=Western

# Output formatting
OUTPUT_HEADER = "🍅 Rotten Tomatoes Opening This Week"
OUTPUT_FOOTER_LINK = "https://bit.ly/2A0na2e"

# Request settings
REQUEST_TIMEOUT = 30
REQUEST_RETRIES = 3

