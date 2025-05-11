"""
Module to generate answers using Gemini LLM based on scraped content.
"""

import os
import time
from typing import List, Dict, Tuple, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from .scrape import scrape_page
import streamlit as st

load_dotenv()


@st.cache_data
def generate_answer(
    question: str, sources: List[Dict[str, str]]
) -> Tuple[str, Optional[str]]:
    """
    Generate answer with citations using Gemini.

    Args:
        question: The user's question
        sources: List of dictionaries containing title and url for each source

    Returns:
        Tuple of (answer text with citations, markdown-formatted sources or None)
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in environment variables.")

    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print(f"Model initialization error: {e}")
        raise RuntimeError(f"Failed to initialize LLM: {str(e)}")

    source_texts = []
    for i, s in enumerate(sources):
        try:
            content = scrape_page(s["url"])
            if content:
                source_texts.append(
                    f"[{i + 1}] Title: {s['title']}\n"
                    f"URL: {s['url']}\n"
                    f"Content: {content}"
                )
            else:
                print(f"Warning: No content scraped from {s['url']}")
        except Exception as e:
            print(f"Error scraping {s['url']}: {e}")

    if not source_texts:
        raise ValueError("No valid content could be scraped from any sources.")

    # Build prompt with proper line breaks
    prompt = (
        f"You are a precise research assistant. Answer the question below "
        f"using ONLY the information from the provided sources.\n\n"
        f"QUESTION: {question}\n\n"
        f"SOURCES:\n{chr(10).join(source_texts)}\n\n"
        f"INSTRUCTIONS:\n"
        f"1. Answer in clear, concise paragraphs with a logical structure "
        f"(e.g., definition, key features, uses, history).\n"
        f"2. Use numbered citations like [1], [2], etc. after sentences or "
        f"claims that require sourcing.\n"
        f"3. Cite a source only once per paragraph for related claims; do not"
        f" repeat the same citation multiple times for closely related points."
        f"\n"
        f"4. Avoid redundancy by consolidating similar information (e.g., do "
        f"not repeat the same feature or use in multiple sentences).\n"
        f"5. Only make claims that are directly supported by the sources and "
        f"relevant to the question.\n"
        f"6. If the sources don't contain enough information to answer fully, "
        f"acknowledge the limitations.\n"
        f"7. Never make up information or use your general knowledge.\n"
        f"8. Format citations as [n] where n is the source number.\n"
        f"9. Always place citations OUTSIDE punctuation marks.\n\n"
        f"Your response must follow this exact format:\n\n"
        f"<answer with [n] citations after relevant sentences or claims>\n\n"
        f"Sources:\n"
        f"[1] Source Title - URL\n"
        f"[2] Source Title - URL\n"
        f"...etc."
    )

    start_time = time.time()
    try:
        response = model.generate_content(prompt)
        answer_text = response.text
        print(f"LLM response time: {time.time() - start_time:.2f}s")

        if "Sources:" in answer_text:
            answer, sources_md = answer_text.split("Sources:", 1)
            return answer.strip(), "Sources:" + sources_md.strip()
        else:
            sources_list = "\n".join(
                [f"[{i + 1}] {s['title']} - {s['url']}" for i, s in enumerate(sources)]
            )
            return answer_text.strip(), (
                f"Sources:\n{sources_list}" if sources_list else None
            )

    except Exception as e:
        print(f"LLM error: {e}")
        raise RuntimeError(f"Error generating answer: {str(e)}")
