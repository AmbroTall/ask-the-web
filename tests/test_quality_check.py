"""Test src/quality_check.py."""

from unittest.mock import patch
from src.quality_check import extract_citations, validate_citations


def test_extract_citations():
    """Test citation extraction from answer text."""
    answer = (
        "Meditation reduces stress [1]. It also improves focus [2][3]. "
        "No citation here."
    )
    citations = extract_citations(answer)
    expected = [
        ("Meditation reduces stress [1].", [1]),
        ("It also improves focus [2][3].", [2, 3]),
        ("No citation here.", []),
    ]
    assert citations == expected


def test_extract_citations_empty():
    """Test citation extraction with no citations."""
    answer = "This is a sentence without citations."
    citations = extract_citations(answer)
    assert citations == [("This is a sentence without citations.", [])]


def test_extract_citations_invalid():
    """Test handling of invalid citation formats."""
    answer = "This has an invalid citation [abc]."
    citations = extract_citations(answer)
    assert citations == [("This has an invalid citation [abc].", [])]


@patch("src.quality_check.genai.GenerativeModel")
def test_validate_citations_success(mock_model):
    """Test citation validation with mocked LLM response."""
    answer = "Meditation reduces stress [1]."
    sources_data = [{"title": "Source 1", "url": "http://example.com"}]
    scraped_texts = {"http://example.com": "Meditation helps reduce stress."}

    # Mock LLM response
    mock_instance = mock_model.return_value
    mock_instance.generate_content.return_value.text = (
        "Sentence 1, Citation [1]: YES - The source explicitly mentions stress"
        " reduction."
    )

    result = validate_citations(answer, sources_data, scraped_texts)
    assert result["overall_score"].startswith("Excellent")
    assert len(result["citations"]) == 1
    assert result["citations"][0]["validation"] == "Valid"
    assert result["citations"][0]["details"][0]["valid"] is True


@patch("src.quality_check.genai.GenerativeModel")
def test_validate_citations_invalid(mock_model):
    """Test citation validation with unsupported claim."""
    answer = "Meditation cures cancer [1]."
    sources_data = [{"title": "Source 1", "url": "http://example.com"}]
    scraped_texts = {"http://example.com": "Meditation helps reduce stress."}

    # Mock LLM response
    mock_instance = mock_model.return_value
    mock_instance.generate_content.return_value.text = (
        "Sentence 1, Citation [1]: NO - The source does not mention curing"
        " cancer."
    )

    result = validate_citations(answer, sources_data, scraped_texts)
    assert result["overall_score"].startswith("Poor")
    assert len(result["citations"]) == 1
    assert result["citations"][0]["validation"] == "Invalid"
    assert result["citations"][0]["details"][0]["valid"] is False
