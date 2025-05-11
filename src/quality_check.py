"""Citation validator for checking information against source texts."""

import os
import re
from typing import List, Tuple, Dict, Any

import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


def extract_citations(answer_text: str) -> List[Tuple[str, List[int]]]:
    """
    Extract sentences and their citations from the answer.

    Args:
        answer_text: The answer text with citations

    Returns:
        List of tuples (sentence, [citation_numbers])
    """
    sentences = re.split(r"(?<=[.!?])\s+", answer_text)
    results = []

    for sentence in sentences:
        if not sentence.strip():
            continue

        citations = []
        citation_matches = re.findall(r"\[(\d+)\]", sentence)

        for match in citation_matches:
            try:
                citations.append(int(match))
            except ValueError:
                pass

        results.append((sentence.strip(), citations))

    return results


@st.cache_data
def validate_citations(
    answer: str, sources_data: List[Dict[str, str]], scraped_texts: Dict[str, str]
) -> Dict[str, Any]:
    """
    Validate that citations in the answer are supported by the source texts.

    Args:
        answer: The answer text with citations
        sources_data: List of source dictionaries with 'title' and 'url'
        scraped_texts: Dictionary mapping source URLs to their scraped text

    Returns:
        Dictionary with overall score and per-citation validation
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set.")

    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print(f"Model initialization error for validator: {e}")
        return {"overall_score": "N/A", "validation_error": str(e), "citations": []}

    citations_data = extract_citations(answer)
    results = {"overall_score": "Pending", "citations": []}

    validation_prompt_parts = [
        "Task: Verify if the cited information is supported by the sources.\n"
    ]

    for idx, (sentence, citation_nums) in enumerate(citations_data):
        validation_prompt_parts.append(f"\nSentence {idx + 1}: {sentence}\n")

        for citation_num in citation_nums:
            source_idx = citation_num - 1
            if source_idx < 0 or source_idx >= len(sources_data):
                continue

            source_url = sources_data[source_idx]["url"]
            source_text = scraped_texts.get(source_url, "")
            validation_prompt_parts.append(
                f"Source [{citation_num}] content: {source_text[:2000]}\n"
            )

    validation_prompt_parts.append(
        """
    Instructions:
    1. For each sentence, analyze if the factual claims are directly supported
        by the cited sources.
    2. For each citation, answer YES or NO, followed by a brief explanation.
    3. Say YES only if the source directly supports ALL claims in the sentence.
    4. Say NO if any claim is unsupported, exaggerated, or contradicted.
    5. Format your response as:
        Sentence 1, Citation [n]: YES/NO - Explanation
        Sentence 1, Citation [m]: YES/NO - Explanation
        Sentence 2, Citation [p]: YES/NO - Explanation
    """
    )
    validation_prompt = "".join(validation_prompt_parts)

    try:
        response = model.generate_content(validation_prompt)
        validation_text = response.text
        validation_lines = validation_text.split("\n")

        for idx, (sentence, citation_nums) in enumerate(citations_data):
            sentence_validations = []

            for citation_num in citation_nums:
                source_idx = citation_num - 1
                if source_idx < 0 or source_idx >= len(sources_data):
                    sentence_validations.append(
                        {
                            "citation_num": citation_num,
                            "valid": False,
                            "reason": "Citation number out of range",
                        }
                    )
                    continue

                pattern = (
                    rf"Sentence {idx + 1}, Citation \[{citation_num}\]: "
                    r"(YES|NO) - (.*)"
                )

                for line in validation_lines:
                    match = re.match(pattern, line.strip())
                    if match:
                        verdict = match.group(1).upper()
                        explanation = match.group(2)
                        sentence_validations.append(
                            {
                                "citation_num": citation_num,
                                "valid": verdict == "YES",
                                "reason": explanation,
                            }
                        )
                        break
                else:
                    sentence_validations.append(
                        {
                            "citation_num": citation_num,
                            "valid": False,
                            "reason": "Validation not found",
                        }
                    )

            sentence_valid = any(v["valid"] for v in sentence_validations)
            results["citations"].append(
                {
                    "sentence": sentence,
                    "citations": citation_nums,
                    "validation": "Valid" if sentence_valid else "Invalid",
                    "details": sentence_validations,
                }
            )

        valid_sentences = sum(
            1 for c in results["citations"] if c["validation"] == "Valid"
        )
        total_sentences = len(results["citations"])

        if total_sentences > 0:
            score_pct = (valid_sentences / total_sentences) * 100

            if score_pct >= 90:
                rating = "Excellent"
            elif score_pct >= 75:
                rating = "Good"
            elif score_pct >= 50:
                rating = "Fair"
            else:
                rating = "Poor"

            results["overall_score"] = (
                f"{rating} ({valid_sentences}/{total_sentences} valid "
                f"citations, {score_pct:.1f}%)"
            )
        else:
            results["overall_score"] = "N/A (No citations found)"

        return results

    except Exception as e:
        print(f"Validation error: {e}")
        return {"overall_score": "N/A", "validation_error": str(e), "citations": []}
