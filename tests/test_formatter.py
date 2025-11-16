"""Tests for formatter module."""

import pytest
from src.formatter import (
    get_tomato_icon,
    get_popcorn_icon,
    format_score,
    format_movie_line,
    format_output,
)


class TestGetTomatoIcon:
    """Test tomato icon selection based on score."""
    
    def test_high_score_returns_tomato(self):
        """Score > 59 should return 🍅."""
        assert get_tomato_icon(60) == "🍅"
        assert get_tomato_icon(100) == "🍅"
        assert get_tomato_icon(75) == "🍅"
    
    def test_low_score_returns_puke(self):
        """Score ≤ 59 should return 🤢."""
        assert get_tomato_icon(59) == "🤢"
        assert get_tomato_icon(0) == "🤢"
        assert get_tomato_icon(30) == "🤢"


class TestGetPopcornIcon:
    """Test popcorn icon selection based on score."""
    
    def test_zero_score_returns_dash(self):
        """Score 0 should return --."""
        assert get_popcorn_icon(0) == "--"
    
    def test_low_score_returns_thumbs_down(self):
        """Score 1-59 should return 👎🏻."""
        assert get_popcorn_icon(1) == "👎🏻"
        assert get_popcorn_icon(59) == "👎🏻"
        assert get_popcorn_icon(30) == "👎🏻"
    
    def test_high_score_returns_popcorn(self):
        """Score > 59 should return 🍿."""
        assert get_popcorn_icon(60) == "🍿"
        assert get_popcorn_icon(100) == "🍿"
        assert get_popcorn_icon(75) == "🍿"


class TestFormatScore:
    """Test score formatting with padding."""
    
    def test_zero_score_formats_to_double_zero(self):
        """Score 0 should format to '00'."""
        assert format_score(0) == "00"
    
    def test_low_scores_get_trailing_space(self):
        """Scores ≤ 99 should get trailing space for alignment."""
        assert format_score(1) == "1 "
        assert format_score(50) == "50 "
        assert format_score(99) == "99 "
    
    def test_hundred_score_no_trailing_space(self):
        """Score 100 should not have trailing space."""
        assert format_score(100) == "100"


class TestFormatMovieLine:
    """Test movie line formatting."""
    
    def test_complete_movie_data(self):
        """Format movie with all data."""
        movie = {
            "title": "Test Movie",
            "tomatoScore": 85,
            "popcornScore": 90,
        }
        result = format_movie_line(movie)
        assert "🍅" in result
        assert "🍿" in result
        assert "Test Movie" in result
        assert "85" in result
        assert "90" in result
    
    def test_movie_with_zero_scores(self):
        """Format movie with zero scores."""
        movie = {
            "title": "Bad Movie",
            "tomatoScore": 0,
            "popcornScore": 0,
        }
        result = format_movie_line(movie)
        assert "🤢" in result
        assert "--" in result
        assert "00" in result
        assert "Bad Movie" in result
    
    def test_movie_with_missing_scores(self):
        """Format movie with missing scores defaults to 0."""
        movie = {
            "title": "Unknown Movie",
        }
        result = format_movie_line(movie)
        assert "Unknown Movie" in result
        # Should handle missing scores gracefully
        assert "00" in result or "--" in result
    
    def test_movie_with_ampersand_in_title(self):
        """Ampersands in title should be converted to 'and'."""
        movie = {
            "title": "Tom & Jerry",
            "tomatoScore": 80,
            "popcornScore": 75,
        }
        result = format_movie_line(movie)
        assert "Tom and Jerry" in result
        assert "Tom & Jerry" not in result
    
    def test_movie_score_boundaries(self):
        """Test score boundaries (59 threshold)."""
        # Tomato score at threshold
        movie_59 = {
            "title": "Threshold Movie",
            "tomatoScore": 59,
            "popcornScore": 59,
        }
        result_59 = format_movie_line(movie_59)
        assert "🤢" in result_59  # ≤59
        assert "👎🏻" in result_59  # 1-59
        
        # Tomato score above threshold
        movie_60 = {
            "title": "Good Movie",
            "tomatoScore": 60,
            "popcornScore": 60,
        }
        result_60 = format_movie_line(movie_60)
        assert "🍅" in result_60  # >59
        assert "🍿" in result_60  # >59
    
    def test_movie_with_invalid_scores(self):
        """Test handling of invalid score values."""
        # Negative scores should be clamped
        movie_neg = {
            "title": "Negative Movie",
            "tomatoScore": -10,
            "popcornScore": -5,
        }
        result_neg = format_movie_line(movie_neg)
        assert "Negative Movie" in result_neg
        
        # Scores > 100 should be clamped
        movie_high = {
            "title": "High Score Movie",
            "tomatoScore": 150,
            "popcornScore": 200,
        }
        result_high = format_movie_line(movie_high)
        assert "High Score Movie" in result_high


class TestFormatOutput:
    """Test complete output formatting."""
    
    def test_format_output_with_movies(self):
        """Format output with multiple movies."""
        movies = [
            {
                "title": "Movie One",
                "tomatoScore": 85,
                "popcornScore": 90,
            },
            {
                "title": "Movie Two",
                "tomatoScore": 45,
                "popcornScore": 50,
            },
        ]
        result = format_output(movies, include_footer=True)
        
        assert "🍅 Rotten Tomatoes Opening This Week" in result
        assert "Movie One" in result
        assert "Movie Two" in result
        assert "Link:" in result
    
    def test_format_output_without_footer(self):
        """Format output without footer."""
        movies = [
            {
                "title": "Test Movie",
                "tomatoScore": 80,
                "popcornScore": 75,
            },
        ]
        result = format_output(movies, include_footer=False)
        
        assert "🍅 Rotten Tomatoes Opening This Week" in result
        assert "Test Movie" in result
        assert "Link:" not in result
    
    def test_format_output_empty_list(self):
        """Format output with empty movie list."""
        result = format_output([], include_footer=True)
        assert "🍅 Rotten Tomatoes Opening This Week" in result
        assert "Link:" in result

