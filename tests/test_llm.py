# tests/test_llm.py

import pytest
from unittest.mock import patch, MagicMock
from ask_the_web.src.llm import generate_answer


@pytest.fixture
def mock_search_results():
    """Create mock search results."""
    return [
        {"title": "Python Programming", "url": "https://example.com/python", "snippet": "Python is a programming language."},
        {"title": "Learn Python", "url": "https://example.com/learn-python", "snippet": "Learn Python basics."},
    ]


def test_generate_answer_successful(mock_search_results):
    """Test successful answer generation."""
    with patch('ask_the_web.src.llm.call_llm') as mock_llm:
        mock_llm.return_value = (
            "Python is a programming language [1]. It is easy to learn [2].",
            "Sources:\n[1] - https://example.com/python\n[2] - https://example.com/learn-python"
        )

        answer, sources_md = generate_answer("What is Python?", mock_search_results)
        assert answer == "Python is a programming language [1]. It is easy to learn [2]."
        assert sources_md == "Sources:\n[1] - https://example.com/python\n[2] - https://example.com/learn-python"
        assert "[1]" in answer
        assert "[2]" in answer


def test_generate_answer_no_search_results():
    """Test answer generation with no search results."""
    with patch('ask_the_web.src.llm.call_llm') as mock_llm:
        mock_llm.return_value = ("No information available.", "Sources:\n")

        answer, sources_md = generate_answer("What is Python?", [])
        assert answer == "No information available."
        assert sources_md == "Sources:\n"


def test_generate_answer_llm_error():
    """Test handling of LLM error."""
    with patch('ask_the_web.src.llm.call_llm', side_effect=Exception("LLM failed")):
        answer, sources_md = generate_answer("What is Python?", mock_search_results)
        assert answer == "Error generating answer."
        assert sources_md == "Sources:\n"


def test_generate_answer_invalid_response_format():
    """Test handling of invalid LLM response format."""
    with patch('ask_the_web.src.llm.call_llm') as mock_llm:
        # Return a single string instead of a tuple
        mock_llm.return_value = "Invalid response"

        answer, sources_md = generate_answer("What is Python?", mock_search_results)
        assert answer == "Error generating answer."
        assert sources_md == "Sources:\n"


def test_generate_answer_citations_missing():
    """Test answer generation when citations are missing in the answer."""
    with patch('ask_the_web.src.llm.call_llm') as mock_llm:
        mock_llm.return_value = (
            "Python is a programming language.",
            "Sources:\n[1] - https://example.com/python\n[2] - https://example.com/learn-python"
        )

        answer, sources_md = generate_answer("What is Python?", mock_search_results)
        assert answer == "Python is a programming language."
        assert sources_md == "Sources:\n[1] - https://example.com/python\n[2] - https://example.com/learn-python"