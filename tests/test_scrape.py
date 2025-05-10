import pytest
from unittest.mock import patch, MagicMock
from ask_the_web.src.scrape import scrape_page
import requests
from bs4 import BeautifulSoup


@pytest.fixture
def mock_response():
    """Create a mock response object."""
    mock = MagicMock()
    mock.text = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <style>
            body { font-family: Arial; }
        </style>
        <script>
            console.log("This should be removed");
        </script>
    </head>
    <body>
        <header>
            <h1>Site Header</h1>
            <nav>Navigation links</nav>
        </header>
        <main>
            <article>
                <h2>Main Article Title</h2>
                <p>This is the first paragraph of content.</p>
                <p>This is the second paragraph with more details about the topic.</p>
            </article>
            <aside>Sidebar content</aside>
        </main>
        <footer>
            <p>Copyright information</p>
        </footer>
    </body>
    </html>
    """
    mock.headers = {'Content-Type': 'text/html'}
    mock.raise_for_status = MagicMock()
    return mock


def test_scrape_page_successful(mock_response):
    """Test successful scraping of a page."""
    with patch('requests.get', return_value=mock_response):
        result = scrape_page('https://example.com')

        # Check that the content includes main article text
        assert "Main Article Title" in result
        assert "This is the first paragraph of content." in result
        assert "This is the second paragraph with more details about the topic." in result

        # Check that unwanted elements are removed
        assert "Site Header" not in result
        assert "Navigation links" not in result
        assert "Copyright information" not in result
        assert "console.log" not in result
        assert "Sidebar content" not in result


def test_scrape_page_connection_error():
    """Test handling of connection error."""
    with patch('requests.get', side_effect=requests.ConnectionError("Connection refused")):
        result = scrape_page('https://example.com')
        assert result == ""


def test_scrape_page_timeout():
    """Test handling of timeout."""
    with patch('requests.get', side_effect=requests.Timeout("Request timed out")):
        result = scrape_page('https://example.com')
        assert result == ""


def test_scrape_page_http_error():
    """Test handling of HTTP error."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Client Error")
    mock_response.status_code = 404

    with patch('requests.get', return_value=mock_response):
        result = scrape_page('https://example.com')
        assert result == ""


def test_scrape_page_invalid_url():
    """Test handling of invalid URL."""
    result = scrape_page('not-a-valid-url')
    assert result == ""


def test_scrape_page_non_html_content():
    """Test handling of non-HTML content."""
    mock_response = MagicMock()
    mock_response.headers = {'Content-Type': 'application/pdf'}

    with patch('requests.get', return_value=mock_response):
        result = scrape_page('https://example.com/document.pdf')
        assert result == ""