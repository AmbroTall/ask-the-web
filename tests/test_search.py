# tests/test_search.py

import pytest
from unittest.mock import patch, MagicMock
from ask_the_web.src.search import search_web
import requests


@pytest.fixture
def mock_search_results():
    """Create mock search results."""
    return [
        {"title": "Python Programming", "url": "https://example.com/python", "snippet": "Python is a programming language."},
        {"title": "Learn Python", "url": "https://example.com/learn-python", "snippet": "Learn Python basics."},
        {"title": "Python Docs", "url": "https://example.com/python-docs", "snippet": "Official Python documentation."},
    ]


def test_search_web_successful(mock_search_results):
    """Test successful web search."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": mock_search_results}
        mock_get.return_value = mock_response

        results = search_web("What is Python?")
        assert len(results) == 3
        assert results[0]["title"] == "Python Programming"
        assert results[0]["url"] == "https://example.com/python"
        assert results[0]["snippet"] == "Python is a programming language."


def test_search_web_no_results():
    """Test web search with no results."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        results = search_web("Non-existent query")
        assert len(results) == 0
        assert results == []


def test_search_web_connection_error():
    """Test handling of connection error during web search."""
    with patch('requests.get', side_effect=requests.ConnectionError("Connection refused")):
        results = search_web("What is Python?")
        assert results == []


def test_search_web_http_error():
    """Test handling of HTTP error during web search."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        mock_get.return_value = mock_response

        results = search_web("What is Python?")
        assert results == []


def test_search_web_invalid_response():
    """Test handling of invalid JSON response."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        results = search_web("What is Python?")
        assert results == []