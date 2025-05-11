"""Test src/scrape.py."""

import pytest
import responses
from src.scrape import scrape_page


@pytest.fixture
def mock_html():
    """Fixture for sample HTML content."""
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <header>Header content</header>
            <nav>Navigation</nav>
            <article class="content">
                <p>This is the main content.</p>
                <p>Another paragraph.</p>
            </article>
            <script>var x = 1;</script>
            <footer>Footer content</footer>
        </body>
    </html>
    """


@responses.activate
def test_scrape_page_success(mock_html):
    """Test successful content extraction from a valid webpage."""
    responses.add(
        responses.GET,
        "http://example.com",
        body=mock_html,
        status=200,
        headers={"Content-Type": "text/html"},
    )
    result = scrape_page("http://example.com")
    assert "This is the main content" in result
    assert "Another paragraph" in result
    assert "Header content" not in result  # Header should be removed
    assert "Navigation" not in result  # Nav should be removed
    assert "var x" not in result  # Script should be removed
    assert len(result) <= 8000  # Content length limit


@responses.activate
def test_scrape_page_non_html():
    """Test handling of non-HTML content."""
    responses.add(
        responses.GET,
        "http://example.com/image.png",
        body="binary data",
        status=200,
        headers={"Content-Type": "image/png"},
    )
    result = scrape_page("http://example.com/image.png")
    assert result == ""  # Should return empty string for non-HTML


@responses.activate
def test_scrape_page_404_error():
    """Test handling of 404 HTTP error."""
    responses.add(
        responses.GET,
        "http://example3435.com",
        body="Not Found",
        status=404,
    )
    result = scrape_page("http://example3435.com")
    assert result == ""  # Should return empty string on HTTP error


def test_scrape_page_invalid_url():
    """Test handling of invalid URL."""
    result = scrape_page("invalid-url")
    assert result == ""  # Should return empty string for invalid URL


@responses.activate
def test_scrape_page_retry_timeout():
    """Test retry logic for connection timeout."""
    responses.add(
        responses.GET,
        "http://example.com",
        body=TimeoutError("Request timed out"),
        status=500,
    )
    result = scrape_page("http://example.com", max_retries=2)
    assert result == ""  # Should return empty string after retries
