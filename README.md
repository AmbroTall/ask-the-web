# Ask the Web - Streamlit Q&A with Citations

Ask the Web is a Streamlit application that answers user questions by searching the web, extracting relevant content, and generating responses with citations using the Gemini LLM. It includes stretch features: telemetry for token and latency metrics and citation quality validation.

## Project Structure
```
ask_the_web/
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI pipeline
├── ask_the_web/
│   ├── __init__.py        # Marks ask_the_web as a package
│   └── src/
│       ├── __init__.py
│       ├── search.py      # Serper API search integration
│       ├── scrape.py      # Web content extraction
│       ├── llm.py         # Gemini LLM answer generation
│       ├── quality_check.py # Citation validation
│       └── telemetry.py   # Token and latency metrics
├── tests/
│   ├── __init__.py
│   ├── test_search.py
│   ├── test_scrape.py
│   ├── test_quality_check.py
│   ├── test_llm.py
│   └── test_telemetry.py
├── .env                  # Example environment variables
├── app.py                # Streamlit UI and main app logic
├── AmbroseCv.pdf         # My resume attached
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker setup
└── README.md
```

## Architecture

```
┌───────────────┐
│  Streamlit UI │
└───────┬───────┘
        │
┌───────▼────────┐
│     app.py     │
└───────┬────────┘
        │
┌───────┴─────────────┬──────────────┬──────────────┐
│ ┌───────────┐ ┌────▼─────┐ ┌────▼─────┐ ┌────────▼─────┐
│ │ search.py │ │ scrape.py │ │  llm.py  │ │ telemetry.py │
│ │(Serper)   │ │(Beautiful │ │ (Gemini) │ │ (metrics)    │
│ └───────────┘ │ Soup)     │ └────┬─────┘ └──────────────┘
└───────────────┴───────────┘      │
                           ┌───────▼─────────┐
                           │ quality_check.py │
                           │ (citation check) │
                           └─────────────────┘
```

## Setup (≤ 5 Commands)

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/ask-the-web.git
   cd ask-the-web
   ```

2. **Set up environment variables**  
   ```bash
   cp .env .env
   ```
   Edit .env to add your Serper API (SEARCH_API_KEY), and Gemini API (GEMINI_API_KEY).
   
   Note: I have provided the .env intentionally for evaluation and testing purposes since the keys are free tier. 

3. **Run with Docker (recommended)**  
   ```bash
   docker build -t ask-web .
   docker run -p 8501:8501 --env-file .env ask-web
   ```

### Alternative (Local Setup):
Requires Python 3.12.
```bash
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run ask_the_web/src/app.py
```

## How It Works

- **Search**: Queries Serper API (https://google.serper.dev/search) to fetch up to 5 organic search results.  

- **Scrape**: Uses BeautifulSoup to extract main content from each result, removing scripts, navigation, etc.  

- **Generate**: Passes the question and scraped texts to Gemini (gemini-1.5-flash) to generate an answer.  

- **Cite**: Formats citations as [n] and lists sources in a "Sources" section.

### Stretch Features:
- **Telemetry Sidebar**: Shows total tokens and latency per query.  

- **Citation Quality Check**: Validates citations with a second LLM call, displaying a pass/fail badge.

## LLM Prompt & Rationale

### Prompt (simplified):  
```
You are a precise research assistant. Answer the question using ONLY the provided sources.
QUESTION: {question}
SOURCES:
[1] Title: {title1}
    URL: {url1}
    Content: {content1}
...
INSTRUCTIONS:
1. Answer in clear, concise paragraphs with numbered citations [1], [2], etc.
2. Cite a source only once per paragraph for related claims.
3. Only make claims directly supported by the sources.
...
```

### Rationale:
The prompt ensures strict adherence to provided sources, minimizing LLM hallucinations. It uses clear instructions to enforce concise answers and proper citation formatting, with iterations to balance readability and accuracy.

## Testing

Run tests with:  
```bash
pytest
```

Run linting with:  
```bash
flake8 ask_the_web tests
```

Run type checking with:  
```bash
mypy ask_the_web tests
```

Generate coverage report:  
```bash
pytest --cov=ask_the_web/src --cov-report=html
```

# Ask the Web - Test Results

```
============================================================ test session starts ============================================================
collected 18 items

tests/test_llm.py::test_generate_answer_success PASSED                                                                              [  5%]
tests/test_llm.py::test_generate_answer_no_content PASSED                                                                            [ 11%]
tests/test_quality_check.py::test_extract_citations PASSED                                                                           [ 16%]
tests/test_quality_check.py::test_extract_citations_empty PASSED                                                                     [ 22%]
tests/test_quality_check.py::test_extract_citations_invalid PASSED                                                                   [ 27%]
tests/test_quality_check.py::test_validate_citations_success PASSED                                                                  [ 33%]
tests/test_quality_check.py::test_validate_citations_invalid PASSED                                                                  [ 38%]
tests/test_scrape.py::test_scrape_page_success PASSED                                                                                [ 44%]
tests/test_scrape.py::test_scrape_page_non_html PASSED                                                                               [ 50%]
tests/test_scrape.py::test_scrape_page_404_error PASSED                                                                              [ 55%]
tests/test_scrape.py::test_scrape_page_invalid_url PASSED                                                                            [ 61%]
tests/test_scrape.py::test_scrape_page_retry_timeout PASSED                                                                          [ 66%]
tests/test_search.py::test_search_web_success PASSED                                                                                 [ 72%]
tests/test_search.py::test_search_web_empty PASSED                                                                                   [ 77%]
tests/test_search.py::test_search_web_error PASSED                                                                                   [ 83%]
tests/test_telemetry.py::test_count_tokens PASSED                                                                                    [ 88%]
tests/test_telemetry.py::test_count_tokens_empty PASSED                                                                              [ 94%]
tests/test_telemetry.py::test_track_telemetry PASSED                                                                                 [100%]

============================================================= 18 passed in 4.02s =============================================================
```
### Coverage:
- **scrape.py**: Tests content extraction and error handling (invalid URLs, HTTP errors).  
- **quality_check.py**: Tests citation extraction and validation logic.  
- **search.py**: Tests API response parsing and error handling.  
- **llm.py**: Tests answer generation and citation formatting.  
- **telemetry.py**: Tests token counting and telemetry tracking.

## CI/CD
A GitHub Actions workflow (.github/workflows/ci.yml) runs on every push or pull request to the main branch. It:
- Lints code with Flake8 to ensure PEP 8 compliance.
- Checks type hints with Mypy for type safety.
- Runs unit tests with pytest and generates a coverage report.
- Builds and tests the Docker image to ensure it starts on port 8501.

To verify the CI pipeline:
1. Push changes to the main branch or open a pull request.
2. Check the workflow status in the GitHub "Actions" tab.
3. Review linting, type checking, test, and Docker build logs for failures.

Note: Tests, linting, and type checking use mock API keys (SEARCH_API_KEY, GEMINI_API_KEY) to avoid real API calls.

## Known Limitations

- **Search**: Serper API free tier has rate limits, which may affect results.  
- **Scrape**: Fails on JavaScript-heavy sites (no headless browser).  
- **LLM**: 8000-character limit per source may truncate content (notified in debug).  
- **Quality Check**: LLM-based validation may produce false positives/negatives.  
- **Performance**: End-to-end latency is 5-15 seconds due to sequential processing.

## Troubleshooting
- **Streamlit Cache**: Clear cache with `streamlit cache clear` or the sidebar "Clear Cache" button.  
- **API Rate Limits**: Verify valid API keys and check Serper/Gemini limits.  
- **Docker**: Pass .env with `--env-file .env`.  
- **Linting/Type Errors**: Run `flake8 ask_the_web tests` or `mypy ask_the_web tests` locally to fix issues.

## Dependencies

- **streamlit**: UI framework  
- **beautifulsoup4**: Web scraping  
- **google-generative-ai**: Gemini API  
- **requests**: HTTP requests  
- **python-dotenv**: Environment variable management  
- **pytest**: Testing framework  
- **tiktoken**: Token counting for telemetry  
- **flake8**: Linting  
- **mypy**: Type checking

See `requirements.txt` for full list.

## Credits

- Built for SkillCat work sample.  
- Uses Serper Google Search API [Serper API](https://google.serper.dev).  
