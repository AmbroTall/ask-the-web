# tests/test_quality_check.py

import pytest
from ask_the_web.src.quality_check import validate_citations


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
        "https://example.com/learn-python": "Learn Python basics. It is easy to learn.",
    }


def test_validate_citations_all_valid(mock_search_results, mock_scraped_texts):
    """Test validation when all citations are valid."""
    answer = "Python is a programming language [1]. It is easy to learn [2]."
    quality_results = validate_citations(
        answer, mock_search_results, mock_scraped_texts
    )

    assert quality_results["overall_score"] == "Excellent (2/2 valid citations, 100.0%)"
    assert len(quality_results["citations"]) == 2
    assert quality_results["citations"][0]["details"][0]["citation_num"] == 1
    assert quality_results["citations"][0]["details"][0]["valid"] == True
    assert quality_results["citations"][1]["details"][0]["citation_num"] == 2
    assert quality_results["citations"][1]["details"][0]["valid"] == True


def test_validate_citations_some_invalid(mock_search_results, mock_scraped_texts):
    """Test validation when some citations are invalid."""
    answer = "Python is a programming language [1]. Java is the best [2]."
    quality_results = validate_citations(
        answer, mock_search_results, mock_scraped_texts
    )

    assert quality_results["overall_score"] == "Fair (1/2 valid citations, 50.0%)"
    assert len(quality_results["citations"]) == 2
    assert quality_results["citations"][0]["details"][0]["citation_num"] == 1
    assert quality_results["citations"][0]["details"][0]["valid"] == True
    assert quality_results["citations"][1]["details"][0]["citation_num"] == 2
    assert quality_results["citations"][1]["details"][0]["valid"] == False


def test_validate_citations_no_citations(mock_search_results, mock_scraped_texts):
    """Test validation when there are no citations."""
    answer = "Python is a programming language."
    quality_results = validate_citations(
        answer, mock_search_results, mock_scraped_texts
    )

    assert quality_results["overall_score"] == "No citations to evaluate"
    assert len(quality_results["citations"]) == 0


def test_validate_citations_missing_scraped_texts(mock_search_results):
    """Test validation when scraped texts are missing."""
    answer = "Python is a programming language [1]."
    scraped_texts = {}
    quality_results = validate_citations(answer, mock_search_results, scraped_texts)

    assert quality_results["overall_score"] == "Poor (0/1 valid citations, 0.0%)"
    assert len(quality_results["citations"]) == 1
    assert quality_results["citations"][0]["details"][0]["valid"] == False


def test_validate_citations_invalid_citation_numbers(
    mock_search_results, mock_scraped_texts
):
    """Test validation with out-of-range citation numbers."""
    answer = "Python is a programming language [10]."
    quality_results = validate_citations(
        answer, mock_search_results, mock_scraped_texts
    )

    assert quality_results["overall_score"] == "Poor (0/1 valid citations, 0.0%)"
    assert len(quality_results["citations"]) == 1
    assert quality_results["citations"][0]["details"][0]["citation_num"] == 10
    assert quality_results["citations"][0]["details"][0]["valid"] == False
