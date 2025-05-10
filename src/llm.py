# llm.py
import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from .scrape import scrape_page
import streamlit as st

load_dotenv()

@st.cache_data
def generate_answer(question: str, sources: list[dict]) -> tuple[str, str]:
    """
    Generate answer with citations using Gemini.

    Args:
        question: The user's question
        sources: List of dictionaries containing title and url for each source

    Returns:
        tuple: (answer text with citations, markdown formatted sources)
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
            content = scrape_page(s['url'])
            if content:
                source_texts.append(f"[{i + 1}] Title: {s['title']}\nURL: {s['url']}\nContent: {content}")
            else:
                print(f"Warning: No content scraped from {s['url']}")
        except Exception as e:
            print(f"Error scraping {s['url']}: {e}")

    if not source_texts:
        raise ValueError("No valid content could be scraped from any sources.")

    prompt = f"""
    You are a precise research assistant. Answer the question below using ONLY the information from the provided sources.

    QUESTION: {question}

    SOURCES:
    {chr(10).join(source_texts)}

    INSTRUCTIONS:
    1. Answer in clear, concise paragraphs with a logical structure (e.g., definition, key features, uses, history).
    2. Use numbered citations like [1], [2], etc. after sentences or claims that require sourcing.
    3. Cite a source only once per paragraph for related claims; do not repeat the same citation multiple times for closely related points.
    4. Avoid redundancy by consolidating similar information (e.g., do not repeat the same feature or use in multiple sentences).
    5. Only make claims that are directly supported by the sources and relevant to the question.
    6. If the sources don't contain enough information to answer fully, acknowledge the limitations.
    7. Never make up information or use your general knowledge.
    8. Format citations as [n] where n is the source number.
    9. Always place citations OUTSIDE punctuation marks.

    Your response must follow this exact format:

    <answer with [n] citations after relevant sentences or claims>

    Sources:
    [1] Source Title - URL
    [2] Source Title - URL
    ...etc.
    """

    start_time = time.time()
    try:
        response = model.generate_content(prompt)
        answer_text = response.text
        print(f"LLM response time: {time.time() - start_time:.2f}s")

        if "Sources:" in answer_text:
            answer, sources_md = answer_text.split("Sources:", 1)
            return answer.strip(), "Sources:" + sources_md.strip()
        else:
            sources_list = "\n".join([f"[{i + 1}] {s['title']} - {s['url']}" for i, s in enumerate(sources)])
            return answer_text.strip(), f"Sources:\n{sources_list}"

    except Exception as e:
        print(f"LLM error: {e}")
        raise RuntimeError(f"Error generating answer: {str(e)}")