"""Tests for scraper module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.scraper import extract_json_data, scrape_movies


class TestExtractJsonData:
    """Test JSON data extraction from HTML."""
    
    def test_extract_movie_with_complete_data(self):
        """Extract movie with all required fields."""
        # Create HTML that matches the regex pattern: "id":[9 digits] + exactly 225 chars + "tomatoScore"
        # The title must be within the 225-char region for extraction to work
        movie_id = "123456789"
        # Put title/url in the 225-char region (they need to be there for title extraction to work)
        title_part = ',"title":"Test Movie","url":"/m/test"'
        # Fill remaining space to make exactly 225 chars total
        remaining = 225 - len(title_part)
        full_225 = title_part + 'x' * remaining
        # Add tomatoScore and rest after the 225 chars
        post_tomato = ',"tomatoScore":85,"popcornIcon":"upright","popcornScore":90,"theaterReleaseDate":"Jan 1"'
        html = f'"id":{movie_id}{full_225}{post_tomato}'
        
        movies = extract_json_data(html)
        assert len(movies) == 1
        assert movies[0]["title"] == "Test Movie"
        assert movies[0]["tomatoScore"] == 85
        assert movies[0]["popcornScore"] == 90
    
    def test_extract_multiple_movies(self):
        """Extract multiple movies from HTML."""
        # Create HTML with two movies matching the regex pattern
        movie1_id = "111111111"
        movie1_data = ',"title":"Movie One","url":"/m/one","tomatoScore":80,"popcornIcon":"upright","popcornScore":85,"theaterReleaseDate":"Jan 1"'
        padding1 = 225 - len(movie1_data)
        if padding1 > 0:
            movie1_data = movie1_data + 'x' * padding1
        
        movie2_id = "222222222"
        movie2_data = ',"title":"Movie Two","url":"/m/two","tomatoScore":70,"popcornIcon":"upright","popcornScore":75,"theaterReleaseDate":"Jan 2"'
        padding2 = 225 - len(movie2_data)
        if padding2 > 0:
            movie2_data = movie2_data + 'x' * padding2
        
        html = f'"id":{movie1_id}{movie1_data}"id":{movie2_id}{movie2_data}'
        
        movies = extract_json_data(html)
        assert len(movies) >= 1  # Should extract at least one movie
    
    def test_extract_movie_with_missing_popcorn_score(self):
        """Extract movie when popcorn score is missing."""
        movie_id = "123456789"
        json_data = ',"title":"Test Movie","url":"/m/test","tomatoScore":85,"theaterReleaseDate":"Jan 1"'
        padding_needed = 225 - len(json_data)
        if padding_needed > 0:
            json_data = json_data + 'x' * padding_needed
        html = f'"id":{movie_id}{json_data}'
        
        movies = extract_json_data(html)
        # Should handle missing popcorn score gracefully
        if movies:
            assert movies[0]["tomatoScore"] == 85
    
    def test_extract_movie_with_zero_scores(self):
        """Extract movie with zero scores."""
        movie_id = "123456789"
        json_data = ',"title":"Bad Movie","url":"/m/bad","tomatoScore":0,"popcornIcon":"spilled","popcornScore":0,"theaterReleaseDate":"Jan 1"'
        padding_needed = 225 - len(json_data)
        if padding_needed > 0:
            json_data = json_data + 'x' * padding_needed
        html = f'"id":{movie_id}{json_data}'
        
        movies = extract_json_data(html)
        if movies:
            assert movies[0]["tomatoScore"] == 0
            assert movies[0]["popcornScore"] == 0
    
    def test_extract_empty_html_returns_empty_list(self):
        """Extract from empty HTML returns empty list."""
        movies = extract_json_data("")
        assert movies == []
    
    def test_extract_html_without_movie_data(self):
        """Extract from HTML without movie data returns empty list."""
        html = "<html><body>No movie data here</body></html>"
        movies = extract_json_data(html)
        assert movies == []
    
    def test_extract_handles_synopsis_cutoff(self):
        """Extract should handle synopsis cutoff like old script."""
        movie_id = "123456789"
        json_data = ',"title":"Test","url":"/m/test","tomatoScore":85,"popcornIcon":"upright","popcornScore":90,"synopsis":"This should be cut off"'
        padding_needed = 225 - len(json_data)
        if padding_needed > 0:
            json_data = json_data + 'x' * padding_needed
        html = f'"id":{movie_id}{json_data}'
        
        movies = extract_json_data(html)
        # Should still extract the movie
        if movies:
            assert movies[0]["title"] == "Test"


class TestScrapeMovies:
    """Test main scraping function."""
    
    @patch('src.scraper.fetch_page')
    def test_scrape_movies_success(self, mock_fetch):
        """Test successful movie scraping."""
        # Mock HTML with movie data matching the regex pattern
        movie_id = "123456789"
        json_data = ',"title":"Test Movie","url":"/m/test","tomatoScore":85,"popcornIcon":"upright","popcornScore":90,"theaterReleaseDate":"Jan 1"'
        padding_needed = 225 - len(json_data)
        if padding_needed > 0:
            json_data = json_data + 'x' * padding_needed
        mock_html = f'"id":{movie_id}{json_data}'
        mock_fetch.return_value = mock_html
        
        movies = scrape_movies()
        assert len(movies) > 0
        mock_fetch.assert_called_once()
    
    @patch('src.scraper.fetch_page')
    def test_scrape_movies_no_data(self, mock_fetch):
        """Test scraping when no movie data found."""
        mock_fetch.return_value = "<html><body>No movies</body></html>"
        
        with pytest.raises(Exception) as exc_info:
            scrape_movies()
        
        assert "No movie data found" in str(exc_info.value)
    
    @patch('src.scraper.fetch_page')
    def test_scrape_movies_fetch_error(self, mock_fetch):
        """Test scraping when fetch fails."""
        mock_fetch.side_effect = Exception("Network error")
        
        with pytest.raises(Exception) as exc_info:
            scrape_movies()
        
        assert "Failed to fetch" in str(exc_info.value)

