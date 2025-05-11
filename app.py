import streamlit as st
import time
import re
from typing import Dict, List, Optional, cast
from src.search import search_web
from src.scrape import scrape_page
from src.llm import generate_answer
from src.telemetry import track_telemetry
from src.quality_check import validate_citations

# Set page configuration
st.set_page_config(
    page_title="Ask the Web - Citation-backed Answers",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.6rem;
        color: #FFFFFF;
        font-weight: 600;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    }
    .citation {
        background-color: #E3F2FD;
        border-radius: 3px;
        padding: 2px 4px;
        font-weight: bold;
        color: #1565C0;
    }
    .source-item {
        background-color: #F5F5F5;
        border-left: 3px solid #1E88E5;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-radius: 0px 5px 5px 0px;
    }
    .stButton button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
        transition: background-color 0.2s ease, color 0.2s ease;
        width: 100%;
        box-sizing: border-box;
    }
    .stButton button:hover {
        background-color: #1565C0;
        border: none;
        color: #E0E0E0;
    }
    button[kind="formSubmit"] {
        width: 100% !important;
    }
    button[kind="formSubmit"][value="Clear"] {
        background-color: #B0BEC5 !important;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none !important;
        transition: background-color 0.2s ease, color 0.2s ease;
        width: 100% !important;
        box-sizing: border-box;
    }
    button[kind="formSubmit"][value="Clear"]:hover {
        background-color: #90A4AE !important;
        border: none !important;
        color: #E0E0E0;
    }
    .telemetry-card {
        background-color: #F5F5F5;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .metric-label {
        color: #616161;
        font-size: 0.9rem;
    }
    .metric-value {
        color: #1E88E5;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .error-message {
        background-color: #FFEBEE;
        color: #C62828;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .answer-container {
        background-color: #FAFAFA;
        border-radius: 5px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        color: #212121 !important;
    }
    .quality-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 12px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .quality-excellent {
        background-color: #C8E6C9;
        color: #2E7D32;
    }
    .quality-good {
        background-color: #DCEDC8;
        color: #33691E;
    }
    .quality-fair {
        background-color: #FFF9C4;
        color: #F57F17;
    }
    .quality-poor {
        background-color: #FFCCBC;
        color: #BF360C;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px 0;
        background-color: #262730;
        color: white;
        z-index: 9999;
    }
    main {
        padding-bottom: 60px;
    }
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    .fullScreenFrame > div:first-child {
        height: 100%;
    }
    .stForm [data-testid="stFormSubmitButton"] {
        width: 100% !important;
    }
    [data-testid="column"] [data-testid="stFormSubmitButton"] {
        width: 100% !important;
    }
    .stTextInput > div > div > input:focus {
        box-shadow: none !important;
        outline: none !important;
        border-color: #90A4AE !important;
    }
    [data-testid="stHorizontalBlock"] [data-testid="column"] {
        width: 100% !important;
        padding: 0 5px;
    }
    .stForm [data-testid="stFormSubmitButton"] button {
        width: 100% !important;
        display: inline-block;
        margin: 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state variables
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "scraped_texts" not in st.session_state:
    st.session_state.scraped_texts = {}
if "quality_score" not in st.session_state:
    st.session_state.quality_score = None
if "input_value" not in st.session_state:
    st.session_state.input_value = ""
if "show_quality_check" not in st.session_state:
    st.session_state.show_quality_check = False

# Title and description
st.markdown("<h1 class='main-header'>🔍 Ask the Web</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='sub-header'>Get citation-backed answers to your questions using web search and AI</p>",
    unsafe_allow_html=True,
)

# Sidebar with info
with st.sidebar:
    st.markdown(
        "<div style='text-align: center; font-size: 5rem;'>🔍</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h2 style='text-align: center;'>Ask the Web</h2>", unsafe_allow_html=True
    )

    st.markdown("### About")
    st.write(
        "Ask the Web uses search APIs to find relevant sources, extracts key information, and generates answers with proper citations."
    )

    st.markdown("### How it works")
    st.markdown(
        """
    1. Enter your question
    2. We search the web for relevant sources
    3. AI generates an answer with citations
    4. Results are displayed with source links
    """
    )

    # Telemetry section in sidebar (initially empty)
    st.markdown("### Telemetry")
    telemetry_container = st.container()

    # Options section
    st.markdown("### Options")
    st.session_state.show_quality_check = st.checkbox(
        "Show Citation Quality Check", value=st.session_state.show_quality_check
    )
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.rerun()

# Main content - use a container for better layout
main_container = st.container()
with main_container:
    st.markdown("<div style='width: 100%;'>", unsafe_allow_html=True)
    with st.form("question_form", clear_on_submit=False):
        question = st.text_input(
            "Your Question",
            placeholder="Example: What are the benefits of meditation?",
            key="question_input",
            value=st.session_state.input_value,
        )

        cols = st.columns([1, 1], gap="small")
        with cols[0]:
            submit = st.form_submit_button("🔍 Ask", use_container_width=True)
        with cols[1]:
            clear = st.form_submit_button("Clear", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Update input_value on form submission
    if submit or clear:
        st.session_state.input_value = st.session_state.question_input

    # Clear form if clear button is pressed
    if clear:
        st.session_state.input_value = ""
        st.session_state.search_results = None
        st.session_state.scraped_texts = {}
        st.session_state.quality_score = None
        st.rerun()

# Results section
if submit and question:
    try:
        start_time = time.time()

        # Progress bar with steps
        progress_text = "Operation in progress. Please wait."
        progress_bar = st.progress(0, text=progress_text)

        # Search
        progress_bar.progress(10, text="Searching the web...")
        search_results = search_web(question)
        st.session_state.search_results = search_results

        if not search_results:
            st.error("No search results found. Please try a different question.")
            st.stop()

        # Limit search results to 5
        search_results = search_results[:5]

        # Scrape content from each source
        progress_bar.progress(30, text="Scraping content from sources...")
        scraped_texts: Dict[str, Optional[str]] = {}
        for source in search_results:
            scraped_texts[source["url"]] = scrape_page(source["url"])
        st.session_state.scraped_texts = scraped_texts

        # Generate answer
        progress_bar.progress(50, text="Analyzing sources and generating answer...")
        answer, sources_md = generate_answer(question, search_results)

        # Run quality check
        progress_bar.progress(80, text="Validating citation quality...")
        st.session_state.quality_score = None  # Reset to avoid stale data
        # Convert scraped_texts to Dict[str, str] by replacing None with ""
        scraped_texts_non_null = {
            k: v if v is not None else "" for k, v in scraped_texts.items()
        }
        quality_results = validate_citations(
            answer, search_results, scraped_texts_non_null
        )

        # Recompute quality score based on unique   unique citations in the answer
        actual_citations = sorted(
            set(re.findall(r"\[\d+\]", answer)), key=lambda x: int(x.strip("[]"))
        )
        total_citations = len(actual_citations)
        valid_citations = 0
        seen_citations = set()
        for citation in quality_results["citations"]:
            for detail in citation["details"]:
                citation_num = detail["citation_num"]
                citation_marker = f"[{citation_num}]"
                if (
                    citation_marker in actual_citations
                    and detail["valid"]
                    and citation_marker not in seen_citations
                ):
                    valid_citations += 1
                    seen_citations.add(citation_marker)
        if total_citations > 0:
            percentage = (valid_citations / total_citations) * 100
            if percentage >= 90:
                quality_label = "Excellent"
            elif percentage >= 75:
                quality_label = "Good"
            elif percentage >= 50:
                quality_label = "Fair"
            else:
                quality_label = "Poor"
            quality_score = f"{quality_label} ({valid_citations}/{total_citations} valid citations, {percentage:.1f}%)"
        else:
            quality_score = "No citations to evaluate"
        st.session_state.quality_score = quality_score

        # Track telemetry and calculate actual latency
        total_time = time.time() - start_time
        telemetry = track_telemetry(
            question, search_results, scraped_texts_non_null, answer
        )
        telemetry["latency"] = total_time  # Use actual end-to-end time

        progress_bar.progress(100, text="Done!")
        time.sleep(0.5)
        progress_bar.empty()

        # Display quality score badge if toggle is enabled
        if (
            "show_quality_check" in st.session_state
            and st.session_state.show_quality_check
        ):
            quality_score = st.session_state.quality_score
            if "Excellent" in quality_score:
                badge_class = "quality-excellent"
            elif "Good" in quality_score:
                badge_class = "quality-good"
            elif "Fair" in quality_score:
                badge_class = "quality-fair"
            else:
                badge_class = "quality-poor"
            st.markdown(
                f"<div class='quality-badge {badge_class}'>Citation Quality: {quality_score}</div>",
                unsafe_allow_html=True,
            )

        # Process answer for inline citation styling
        answer_html = answer
        for i in range(len(search_results)):
            citation_num = i + 1
            styled_citation = f"<span class='citation'>[{citation_num}]</span>"
            answer_html = answer_html.replace(f"[{citation_num}]", styled_citation)

        # Display answer in a nice container
        st.markdown("### Answer")
        st.markdown(
            f"<div class='answer-container'>{answer_html}</div>", unsafe_allow_html=True
        )

        # Format sources as a list
        st.markdown("### Sources")
        sources_md_typed: Optional[str] = cast(Optional[str], sources_md)  # Force type
        if sources_md_typed is not None:
            sources_list: List[str] = (
                sources_md_typed.replace("Sources:", "").strip().split("\n")
            )  # type: ignore[assignment]
            for source in sources_list:  # type: ignore
                source = source.strip()  # type: ignore[attr-defined]
                if source:
                    source_parts = source.split(" - ")  # type: ignore[attr-defined]
                    if len(source_parts) >= 2:
                        citation_label = source_parts[0].strip()
                        url = source_parts[-1].strip()
                        st.markdown(
                            f"- {citation_label} - [{url}]({url})",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(f"- {source}", unsafe_allow_html=True)
        else:
            st.write("No sources available.")

        # Display telemetry in sidebar
        with telemetry_container:
            st.markdown("<div class='telemetry-card'>", unsafe_allow_html=True)
            st.markdown(
                f"<span class='metric-label'>Total Time:</span> <span class='metric-value'>{telemetry['latency']:.2f}s</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span class='metric-label'>Input Tokens:</span> <span class='metric-value'>{telemetry['input_tokens']}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span class='metric-label'>Output Tokens:</span> <span class='metric-value'>{telemetry['output_tokens']}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span class='metric-label'>Total Tokens:</span> <span class='metric-value'>{telemetry['total_tokens']}</span>",
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # Debug panel with better styling
        with st.expander("Debug: Raw Search Results"):
            st.json(search_results)

        # Show Citation Quality Check debug only if toggle is enabled
        if (
            "show_quality_check" in st.session_state
            and st.session_state.show_quality_check
        ):
            with st.expander("Debug: Citation Quality Check"):
                st.json(quality_results)

    except Exception as e:
        st.markdown(
            f"<div class='error-message'>Error: {str(e)}</div>", unsafe_allow_html=True
        )
        st.error(f"An error occurred: {str(e)}")
        if "cache" in str(e).lower():
            st.warning(
                "A caching error occurred. Try clearing the cache from the sidebar."
            )

# Footer - fixed at bottom
st.markdown(
    """
<div class='footer'>
    <p>Created for SkillCat Work Sample. Powered by Streamlit + Gemini.</p>
</div>
""",
    unsafe_allow_html=True,
)
