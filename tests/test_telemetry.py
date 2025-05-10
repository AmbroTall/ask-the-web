# tests/test_telemetry.py

import pytest
from unittest.mock import patch
from ask_the_web.src.telemetry import track_telemetry


@pytest.fixture
def mock_search_results():
    """Create mock search results."""
    return [
        {"title": "Python Programming", "url": "https://example.com/python"},
        {"title": "Learn Python", "url": "https://example.com/learn-python"},
    ]


@pytest.fixture
def mock_scraped_texts():
    """Create mock scraped texts."""
    return {
        "https://example.com/python": "Python is a programming language.",
        "https://example.com/learn-python": "Learn Python basics.",
    }


def test_track_telemetry_success(mock_search_results, mock_scraped_texts):
    """Test successful telemetry tracking."""
    question = "What is Python?"
    answer = "Python is a programming language [1]."

    with patch("ask_the_web.src.telemetry.count_tokens") as mock_count_tokens:
        mock_count_tokens.side_effect = lambda text: len(
            text.split()
        )  # Mock token counting as word count

        telemetry = track_telemetry(
            question, mock_search_results, mock_scraped_texts, answer
        )

        assert telemetry["input_tokens"] == 3  # "What is Python?"
        assert (
            telemetry["output_tokens"] == 6
        )  # "Python is a programming language [1]."
        assert telemetry["total_tokens"] == 9  # input + output
        assert "latency" in telemetry
        assert (
            telemetry["latency"] == 0
        )  # Since latency is passed from app.py, mock as 0


def test_track_telemetry_empty_inputs(mock_search_results, mock_scraped_texts):
    """Test telemetry with empty inputs."""
    question = ""
    answer = ""

    with patch("ask_the_web.src.telemetry.count_tokens") as mock_count_tokens:
        mock_count_tokens.side_effect = lambda text: len(text.split())

        telemetry = track_telemetry(
            question, mock_search_results, mock_scraped_texts, answer
        )

        assert telemetry["input_tokens"] == 0
        assert telemetry["output_tokens"] == 0
        assert telemetry["total_tokens"] == 0
        assert telemetry["latency"] == 0


def test_track_telemetry_no_search_results(mock_scraped_texts):
    """Test telemetry with no search results."""
    question = "What is Python?"
    answer = "No information available."

    with patch("ask_the_web.src.telemetry.count_tokens") as mock_count_tokens:
        mock_count_tokens.side_effect = lambda text: len(text.split())

        telemetry = track_telemetry(question, [], mock_scraped_texts, answer)

        assert telemetry["input_tokens"] == 3
        assert telemetry["output_tokens"] == 3
        assert telemetry["total_tokens"] == 6
        assert telemetry["latency"] == 0


def test_track_telemetry_no_scraped_texts(mock_search_results):
    """Test telemetry with no scraped texts."""
    question = "What is Python?"
    answer = "Python is a programming language [1]."

    with patch("ask_the_web.src.telemetry.count_tokens") as mock_count_tokens:
        mock_count_tokens.side_effect = lambda text: len(text.split())

        telemetry = track_telemetry(question, mock_search_results, {}, answer)

        assert telemetry["input_tokens"] == 3
        assert telemetry["output_tokens"] == 6
        assert telemetry["total_tokens"] == 9
        assert telemetry["latency"] == 0
