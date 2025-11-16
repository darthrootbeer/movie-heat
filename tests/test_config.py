"""Tests for config module."""

from src import config


class TestConfig:
    """Test configuration settings."""

    def test_rt_opening_url_is_string(self):
        """RT_OPENING_URL should be a string."""
        assert isinstance(config.RT_OPENING_URL, str)
        assert len(config.RT_OPENING_URL) > 0

    def test_score_threshold_is_integer(self):
        """SCORE_THRESHOLD should be an integer."""
        assert isinstance(config.SCORE_THRESHOLD, int)
        assert config.SCORE_THRESHOLD == 59

    def test_request_timeout_is_positive(self):
        """REQUEST_TIMEOUT should be a positive number."""
        assert isinstance(config.REQUEST_TIMEOUT, int)
        assert config.REQUEST_TIMEOUT > 0

    def test_request_retries_is_positive(self):
        """REQUEST_RETRIES should be a positive integer."""
        assert isinstance(config.REQUEST_RETRIES, int)
        assert config.REQUEST_RETRIES > 0

    def test_output_header_is_string(self):
        """OUTPUT_HEADER should be a string."""
        assert isinstance(config.OUTPUT_HEADER, str)
        assert len(config.OUTPUT_HEADER) > 0

    def test_output_footer_link_is_string(self):
        """OUTPUT_FOOTER_LINK should be a string."""
        assert isinstance(config.OUTPUT_FOOTER_LINK, str)
        assert len(config.OUTPUT_FOOTER_LINK) > 0

