"""Tests for emailer module."""

import os
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest
import pytz

from src.emailer import create_email_content, send_email, should_send_email


class TestCreateEmailContent:
    """Test email content creation."""

    def test_create_email_content_returns_html_and_text(self):
        """create_email_content returns both HTML and plain text."""
        movies_text = "🍅 98  |  🍿 97  -  Test Movie"
        html, text = create_email_content(movies_text)

        assert isinstance(html, str)
        assert isinstance(text, str)
        assert len(html) > 0
        assert len(text) > 0
        assert "Movie Heat" in html
        assert movies_text in html
        assert movies_text in text

    def test_create_email_content_includes_movies_text(self):
        """Email content includes the provided movies text."""
        movies_text = "🍅 85  |  🍿 90  -  Another Movie"
        html, text = create_email_content(movies_text)

        assert movies_text in html
        assert movies_text in text


class TestSendEmail:
    """Test email sending functionality."""

    @patch("src.emailer.smtplib.SMTP")
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        movies_text = "🍅 98  |  🍿 97  -  Test Movie"
        send_email(
            movies_text,
            "test@example.com",
            gmail_user="sender@gmail.com",
            gmail_password="app_password",
        )

        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("sender@gmail.com", "app_password")
        mock_server.send_message.assert_called_once()

    def test_send_email_missing_credentials(self):
        """Test send_email raises error when credentials missing."""
        movies_text = "🍅 98  |  🍿 97  -  Test Movie"

        with pytest.raises(ValueError, match="Gmail credentials not provided"):
            send_email(movies_text, "test@example.com", gmail_user=None, gmail_password=None)

    def test_send_email_missing_recipient(self):
        """Test send_email raises error when recipient missing."""
        with pytest.raises(ValueError, match="Recipient email address not provided"):
            send_email("test", "", gmail_user="sender@gmail.com", gmail_password="pass")

    @patch.dict(os.environ, {"GMAIL_USER": "env_user@gmail.com", "GMAIL_APP_PASSWORD": "env_pass"})
    @patch("src.emailer.smtplib.SMTP")
    def test_send_email_uses_env_vars(self, mock_smtp):
        """Test send_email uses environment variables when credentials not provided."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        movies_text = "🍅 98  |  🍿 97  -  Test Movie"
        send_email(movies_text, "test@example.com")

        mock_server.login.assert_called_once_with("env_user@gmail.com", "env_pass")


class TestShouldSendEmail:
    """Test email scheduling logic."""

    def test_should_send_email_function_exists(self):
        """Test that should_send_email function exists and is callable."""
        # Just verify the function exists and can be called
        # Actual scheduling is handled by GitHub Actions cron
        result = should_send_email()
        assert isinstance(result, bool)

