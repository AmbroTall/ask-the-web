"""Test src/llm.py."""

import pytest
from unittest.mock import patch
from src.llm import generate_answer


@patch("src.llm.genai.GenerativeModel")
def test_generate_answer_success(mock_model):
    """Test successful answer generation with citations."""
    question = "What is meditation?"
    sources = [
        {"title": "Source 1", "url": "http://example.com"},
        {"title": "Source 2", "url": "http://example.com/2"},
    ]

    # Mock scrape_page
    with patch("src.llm.scrape_page") as mock_scrape:
        mock_scrape.return_value = "Meditation is a practice to reduce stress."

        # Mock LLM response
        mock_instance = mock_model.return_value
        mock_instance.generate_content.return_value.text = (
            "Meditation is a practice to reduce stress [1].\n\n"
            "Sources:\n"
            "[1] Source 1 - http://example.com\n"
            "[2] Source 2 - http://example.com/2"
        )

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("GEMINI_API_KEY", "test_key")
            answer, sources_md = generate_answer(question, sources)
            assert "Meditation is a practice to reduce stress [1]." in answer
            assert "[1] Source 1 - http://example.com" in sources_md
            assert "[2] Source 2 - http://example.com/2" in sources_md


@patch("src.llm.genai.GenerativeModel")
def test_generate_answer_no_content(mock_model):
    """Test handling of no scraped content."""
    question = "What is meditation?"
    sources = [{"title": "Source 1", "url": "http://example.com"}]

    # Mock scrape_page to return empty content
    with patch("src.llm.scrape_page") as mock_scrape:
        mock_scrape.return_value = ""

        with pytest.MonkeyPatch.context() as mp:
            mp.setenv("GEMINI_API_KEY", "test_key")
            with pytest.raises(
                    ValueError, match="No valid content could be scraped"
            ):
                generate_answer(question, sources)
