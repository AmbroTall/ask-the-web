"""Test src/telementry.py"""

from src.telemetry import count_tokens, track_telemetry


def test_count_tokens():
    """Test token counting with tiktoken."""
    text = "This is a test sentence."
    tokens = count_tokens(text)
    assert tokens > 0  # Exact count depends on tokenizer
    assert isinstance(tokens, int)


def test_count_tokens_empty():
    """Test token counting with empty text."""
    tokens = count_tokens("")
    assert tokens == 0


def test_track_telemetry():
    """Test telemetry tracking."""
    question = "What is meditation?"
    sources = [{"title": "Source 1", "url": "http://example.com"}]
    scraped_texts = {"http://example.com": "Meditation reduces stress."}
    answer = "Meditation is a practice [1]."

    telemetry = track_telemetry(question, sources, scraped_texts, answer)
    assert telemetry["input_tokens"] > 0
    assert telemetry["source_tokens"] > 0
    assert telemetry["output_tokens"] > 0
    assert telemetry["total_tokens"] == (
        telemetry["input_tokens"]
        + telemetry["source_tokens"]
        + telemetry["output_tokens"]
    )
    assert telemetry["source_count"] == 1
    assert telemetry["question_length"] == len(question)
    assert telemetry["answer_length"] == len(answer)
