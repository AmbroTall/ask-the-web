# Ask the Web - Streamlit Q&A with Citations

A Streamlit application that answers questions by searching the web, extracting information from relevant pages, and generating responses with proper citations using Gemini LLM.

![Ask the Web Screenshot](https://via.placeholder.com/800x400.png?text=Ask+The+Web+Screenshot)

## Architecture

```
                     ┌───────────────┐
                     │  Streamlit UI │
                     └───────┬───────┘
                             │
                  ┌──────────▼──────────┐
                  │       app.py        │
                  └──────────┬──────────┘
                             │
           ┌────────────┬────┴────┬────────────┐
           │            │         │            │
  ┌────────▼─────┐ ┌────▼────┐ ┌──▼───┐ ┌──────▼──────┐
  │   search.py  │ │scrape.py│ │llm.py│ │telemetry.py │
  │ (web search) │ │(content │ │(LLM  │ │(performance │
  │              │ │extraction)│ │answer)│ │metrics)    │
  └──────────────┘ └─────────┘ └──────┘ └─────────────┘
                                  │
                      ┌───────────▼───────────┐
                      │    quality_check.py   │
                      │   (citation validation)│
                      └───────────────────────┘
```

## Setup (5 commands)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ask-the-web.git
   cd ask-the-web
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env  # Then edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

Alternatively, **run with Docker**:
```bash
docker build -t ask-web .
docker run -p 8501:8501 ask-web
```

## How it Works

1. **Search**: The application uses SerpAPI to search the web for the most relevant results.
2. **Scrape**: It extracts the main content from up to 5 search results using BeautifulSoup.
3. **Generate**: The scraped content and the user's question are sent to Gemini LLM to generate an answer.
4. **Cite**: The LLM includes numbered citations in the answer, linking to the source material.
5. **Validate**: (Optional stretch) A second LLM call validates whether each citation actually supports the claims made.

## LLM Prompting Strategy

The system uses a structured prompt that includes:

```
You are a precise research assistant. Answer the question using ONLY the information from the provided sources.

QUESTION: {question}

SOURCES:
[1] Title: {title1}
URL: {url1}
Content: {content1}
...

INSTRUCTIONS:
1. Answer in clear, concise paragraphs.
2. Use numbered citations like [1], [2], etc. after EVERY sentence or claim.
3. Only make claims that are directly supported by the sources.
...
```

**Rationale**: This prompt explicitly instructs the model to maintain strict citation discipline while focusing only on information present in the provided sources, which significantly reduces hallucination risks.

## Testing

Run the tests with:
```bash
pytest
```

The test suite covers:
- Web scraping functionality
- Citation extraction and validation
- Error handling scenarios

## Known Limitations

- Search results quality depends on the SerpAPI service
- Web scraping may fail on sites with complex JavaScript rendering or anti-scraping measures
- Token limitations may truncate long source texts
- Citation validation is not 100% reliable and may generate false positives/negatives
- Response time can be slow (5-15 seconds) due to the sequential process of search → scrape → LLM generation

## Dependencies

- **Streamlit**: UI framework
- **BeautifulSoup4**: Web scraping
- **Google Generative AI**: Gemini API access
- **Requests**: HTTP requests
- **python-dotenv**: Environment variables management
- **pytest**: Testing framework

## Credits

This project was created as a work sample for SkillCat.

Third-party libraries are used according to their respective licenses.