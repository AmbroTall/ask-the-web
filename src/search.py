import json
import os
import requests
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


@st.cache_data
def search_web(query: str) -> list[dict]:
    """
    Query a web search API and return up to 5 organic results with title and URL.

    Args:
        query: The search query

    Returns:
        list: List of dictionaries containing title and url for each result
    """
    api_key = os.getenv("SEARCH_API_KEY")
    url = os.getenv("URL")
    if not api_key:
        raise ValueError("SEARCH_API_KEY not set.")
    if not url:
        raise ValueError("URL not set in environment variables.")

    payload = json.dumps({"q": query, "gl": "ke"})
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        raw_results = response.json()
        results = raw_results.get("organic", [])
        parsed_results = [{"title": r["title"], "url": r["link"]} for r in results[:5]]
        return parsed_results
    except requests.RequestException as e:
        print(f"Search error: {e}")
        return []
