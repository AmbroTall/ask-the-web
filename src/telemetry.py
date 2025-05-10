import os
import tiktoken
from typing import Dict, List, Any, Optional

from dotenv import load_dotenv

load_dotenv()


# Initialize encoder for token counting
def get_tokenizer():
    """Get the appropriate tokenizer based on environment variable or default to cl100k_base"""
    model_name = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    try:
        return tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Default to cl100k_base if model specific encoding is not found
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """
    Count tokens accurately using tiktoken library

    Args:
        text: The text to count tokens for

    Returns:
        int: Number of tokens in the text
    """
    if not text:
        return 0

    try:
        encoder = get_tokenizer()
        return len(encoder.encode(text))
    except Exception as e:
        # Fallback to approximation if tiktoken fails
        print(f"Token counting error: {e}")
        return len(text) // 4  # Rough approximation (1 token ≈ 4 chars)


def track_telemetry(
    question: str,
    sources: List[Dict[str, str]],
    scraped_texts: Dict[str, str],
    answer: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Track tokens and latency for a query with accurate token counting.

    Args:
        question: The user's question
        sources: List of dictionaries containing title and url for each source
        scraped_texts: Dictionary mapping source URLs to their scraped text
        answer: The generated answer text (optional)

    Returns:
        dict: Dictionary with token counts and other telemetry data
    """
    # Calculate input tokens
    input_text = question
    input_tokens = count_tokens(input_text)

    # Add tokens from scraped content
    source_tokens = 0
    for source in sources:
        url = source.get("url", "")
        if url in scraped_texts and scraped_texts[url]:
            source_tokens += count_tokens(scraped_texts[url])

    # Calculate output tokens
    output_tokens = count_tokens(answer) if answer else 0

    return {
        "input_tokens": input_tokens,
        "source_tokens": source_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + source_tokens + output_tokens,
        "latency": 0.0,  # Will be filled in by the caller
        "source_count": len(sources),
        "question_length": len(question),
        "answer_length": len(answer) if answer else 0,
    }
