import requests
from bs4 import BeautifulSoup
import time
from typing import Optional
import re
from urllib.parse import urlparse
import streamlit as st


@st.cache_data
def scrape_page(
    url: str, max_retries: int = 3, backoff_factor: float = 1.5
) -> Optional[str]:
    """
    Extract main text content from a webpage with robust error handling and retries.

    Args:
        url: The URL to scrape
        max_retries: Maximum number of retry attempts
        backoff_factor: Factor to increase wait time between retries

    Returns:
        str: Extracted text content or empty string if extraction fails
    """
    # Validate URL
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            print(f"Invalid URL format: {url}")
            return ""
    except Exception:
        print(f"URL parsing error: {url}")
        return ""

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    # Retry logic with exponential backoff
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url, headers=headers, timeout=10, allow_redirects=True
            )
            response.raise_for_status()

            # Check if content is HTML
            content_type = response.headers.get("Content-Type", "").lower()
            if (
                "text/html" not in content_type
                and "application/xhtml+xml" not in content_type
            ):
                print(f"Skipping non-HTML content: {content_type} for {url}")
                return ""

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unwanted elements
            for element in soup(
                [
                    "script",
                    "style",
                    "nav",
                    "footer",
                    "header",
                    "aside",
                    "noscript",
                    "iframe",
                    "svg",
                    "form",
                ]
            ):
                element.decompose()

            # Try to get main content elements
            main_content = ""

            # Try method 1: Find article or main tags
            content_elements = soup.find_all(
                ["article", "main", "div"],
                class_=re.compile(r"(content|article|post|entry|text)"),
            )
            if content_elements:
                for element in content_elements:
                    main_content += element.get_text(separator=" ", strip=True) + " "

            # If main content sections weren't found, use paragraphs
            if not main_content:
                paragraphs = soup.find_all("p")
                main_content = " ".join(
                    p.get_text(strip=True)
                    for p in paragraphs
                    if len(p.get_text(strip=True)) > 40
                )

            # If still no content, try getting all text
            if not main_content:
                main_content = soup.get_text(separator=" ", strip=True)

            # Clean up the text
            main_content = re.sub(
                r"\s+", " ", main_content
            )  # Replace multiple spaces with single space
            main_content = re.sub(
                r"[\n\r\t]+", " ", main_content
            )  # Remove newlines and tabs

            # Limit content length to avoid token issues
            MAX_CHARS = 8000
            if len(main_content) > MAX_CHARS:
                main_content = main_content[:MAX_CHARS] + "..."

            return main_content

        except requests.exceptions.HTTPError as e:
            if hasattr(e, "response") and e.response.status_code in [
                403,
                404,
                429,
                500,
                502,
                503,
            ]:
                print(f"HTTP error {e.response.status_code} for {url}: {str(e)}")
                if attempt == max_retries - 1:
                    return ""
            else:
                print(f"HTTP error for {url}: {str(e)}")
                if attempt == max_retries - 1:
                    return ""

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects,
        ) as e:
            print(f"Connection error for {url}: {str(e)}")
            if attempt == max_retries - 1:
                return ""

        except Exception as e:
            print(f"Unexpected error scraping {url}: {str(e)}")
            return ""

        # Wait before retrying with exponential backoff
        wait_time = backoff_factor * (2**attempt)
        print(
            f"Retrying {url} in {wait_time:.1f} seconds... (Attempt {attempt + 1}/{max_retries})"
        )
        time.sleep(wait_time)

    return ""
