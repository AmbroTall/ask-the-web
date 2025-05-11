# Ask the Web - Streamlit Q&A with Citations

A Streamlit app that answers user questions by searching the web, extracting relevant content, and generating responses with citations using Gemini LLM. Includes optional stretch features: telemetry and citation quality validation.

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
│ │(SerpAPI)  │ │(Beautiful │ │ (Gemini) │ │ (metrics)    │
│ └───────────┘ │ Soup)     │ └────┬─────┘ └──────────────┘
└───────────────┴───────────┘      │
                           ┌───────▼─────────┐
                           │ quality_check.py │
                           │ (citation check) │
                           └─────────────────┘
```

## Setup (≤ 5 Commands)

### Clone the repository  
```bash
git clone https://github.com/yourusername/ask-the-web.git
cd ask-the-web
```

### Set up environment variables  
```bash
cp .env.example .env  # Edit .env with your SerpAPI and Gemini API keys
```

### Run with Docker (recommended)  
```bash
docker build -t ask-web .
docker run -p 8501:8501 ask-web
```

### Alternative (Local Setup):  
1. Create a virtual environment: 
   ```bash
   python -m venv venv && source venv/bin/activate
   ```
   (Windows: `venv\Scripts\activate`)  

2. Install dependencies: 
   ```bash
   pip install -r requirements.txt
   ```  

3. Run: 
   ```bash
   streamlit run app.py
   ```

## How It Works

1. **Search**: Queries SerpAPI to fetch up to 5 organic search results.  

2. **Scrape**: Uses BeautifulSoup to extract main content from each result (removes scripts, nav, etc.).  

3. **Generate**: Passes the question and scraped texts to Gemini (gemini-1.5-flash) for an answer.  

4. **Cite**: Formats citations as [n] and lists sources in a "Sources" section.  

### Stretch Features:  
- **Telemetry sidebar**: Displays total tokens and latency per query.  
- **Citation Quality Check**: Validates citations using a second LLM call, showing a pass/fail badge.

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
The prompt was iterated to enforce strict source usage and citation discipline, minimizing hallucinations. Initial versions lacked clarity on citation frequency, leading to over-citation; the final version balances accuracy and readability.

## Testing

Run tests with:  
```bash
pytest
```

### Coverage:  
- **scrape.py**: Tests content extraction and error handling.  
- **quality_check.py**: Tests citation extraction and validation logic.  
- **search.py**: Tests API response parsing.

## Known Limitations

- **Search**: SerpAPI free tier has rate limits; results may vary by query.  
- **Scrape**: Fails on JavaScript-heavy sites (no headless browser support).  
- **LLM**: 8000-char limit per source may truncate content (notified in debug).  
- **Quality Check**: LLM-based validation may have false positives/negatives.  
- **Performance**: End-to-end latency is 5-15s due to sequential processing.

## Dependencies

- **streamlit**: UI framework  
- **beautifulsoup4**: Web scraping  
- **google-generative-ai**: Gemini API  
- **requests**: HTTP requests  
- **python-dotenv**: Environment variable management  
- **pytest**: Testing framework  
- **tiktoken**: Token counting for telemetry

See `requirements.txt` for full list.

## Credits

- Built for SkillCat work sample.  
- Uses SerpAPI free tier for search ([SerpAPI license](https://serpapi.com/terms)).  
- BeautifulSoup and other libraries per their licenses.