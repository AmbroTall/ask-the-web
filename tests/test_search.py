"""Test src/search.py."""

import pytest
import responses
from src.search import search_web


@responses.activate
def test_search_web_success():
    """Test successful search API call."""
    mock_response = {
        "organic": [
            {"title": "Result 1", "link": "http://example.com/1"},
            {"title": "Result 2", "link": "http://example.com/2"},
        ]
    }
    responses.add(
        responses.POST,
        "https://google.serper.dev/search",
        json=mock_response,
        status=200,
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("SEARCH_API_KEY", "test_key")
        mp.setenv("URL", "https://google.serper.dev/search")
        results = search_web("test query")
        assert len(results) == 2
        assert results[0]["title"] == "Result 1"
        assert results[0]["url"] == "http://example.com/1"


@responses.activate
def test_search_web_empty():
    """Test empty search results."""
    responses.add(
        responses.POST,
        "https://google.serper.dev/search",
        json={"organic": []},
        status=200,
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("SEARCH_API_KEY", "test_key")
        mp.setenv("URL", "https://google.serper.dev/search")
        results = search_web("test streamlit")
        assert results == []


@responses.activate
def test_search_web_error():
    """Test handling of API errors."""
    responses.add(
        responses.POST,
        "https://google.serper.dev/search",
        status=500,
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("SEARCH_API_KEY", "test_key")
        mp.setenv("URL", "https://google.serper.dev/search")
        results = search_web("test streamlit")
        assert results == []
