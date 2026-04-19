# DeepResearchMind

**An AI-powered multi-agent research system that automates the entire research workflow — from web search to polished report generation.**

---

## Overview

DeepResearchMind is an intelligent research automation platform built on a multi-agent architecture. It orchestrates four specialized AI agents in a sequential pipeline to transform any research topic into a comprehensive, well-structured report — complete with quality assurance through an automated critic review.

The system leverages LangChain for agent orchestration, Tavily for real-time web search, BeautifulSoup for content extraction, and a custom LLM integration via OpenRouter for natural language generation. The frontend is built with Streamlit and features a premium dark-mode terminal-inspired UI.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DeepResearchMind                        │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │  Search   │──>│  Reader   │──>│  Writer   │──>│  Critic  │ │
│  │  Agent    │   │  Agent    │   │  Chain    │   │  Chain   │ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘ │
│       │               │              │              │       │
│   Tavily API     BeautifulSoup    LLM (LCEL)    LLM (LCEL)  │
│   Web Search     URL Scraping     Report Gen    Review Gen   │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Streamlit Web Interface                    │  │
│  │   Real-time pipeline status + Report display           │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Pipeline Stages

### Stage 01 — Search Agent

The Search Agent takes the user-provided research topic and queries the Tavily web search API. It retrieves up to 5 recent, relevant results including page titles, URLs, and content snippets. This forms the initial knowledge base for the research.

**Tool Used:** `web_search` (powered by Tavily API)
**Output:** Structured list of search results with titles, URLs, and snippets.

### Stage 02 — Reader Agent

The Reader Agent analyzes the search results and uses the LLM to identify the most relevant URL for deep content extraction. It then scrapes that page using BeautifulSoup, removing scripts, styles, navigation, and footer elements to extract clean readable text (up to 3,000 characters).

**Tool Used:** `scrape_url` (powered by BeautifulSoup + requests)
**Output:** Clean, extracted text content from the most relevant web page.

### Stage 03 — Writer Chain

The Writer Chain combines all gathered research (search results + scraped content) and generates a comprehensive research report using LangChain Expression Language (LCEL). The report follows a structured format:

- Introduction
- Key Findings (minimum 3 detailed points)
- Conclusion
- Sources (all URLs from research)

**Model:** Custom LLM via OpenRouter API
**Output:** Full markdown-formatted research report.

### Stage 04 — Critic Chain

The Critic Chain receives the generated report and performs a structured quality review. It evaluates the report across multiple dimensions and provides:

- Overall score (X/10)
- Strengths
- Areas to improve
- One-line verdict

**Model:** Custom LLM via OpenRouter API
**Output:** Structured critique with actionable feedback.

---

## Technology Stack

| Component          | Technology                                      |
|--------------------|-------------------------------------------------|
| **Frontend**       | Streamlit (Python)                              |
| **LLM Framework**  | LangChain + LangChain Core                      |
| **LLM Provider**   | OpenRouter API (configurable model)              |
| **Web Search**     | Tavily Search API                               |
| **Web Scraping**   | BeautifulSoup4 + Requests                        |
| **HTTP Client**    | HTTPX (async-capable)                            |
| **Environment**    | python-dotenv                                    |
| **Data Validation**| Pydantic v2                                      |
| **Styling**        | Custom CSS (Source Code Pro, dark terminal theme) |

---

## Project Structure

```
Multi Agent System/
├── app.py              # Main Streamlit application (primary entry point)
├── pipeline.py         # Duplicate of app.py (backup / alternate entry)
├── agents.py           # Agent definitions, LLM wrapper, and LCEL chains
├── tools.py            # Tool definitions (web_search, scrape_url)
├── requirements.txt    # Python dependencies
├── .env                # API keys (not committed to version control)
└── README.md           # This file
```

### File Details

**`app.py`** — The main Streamlit application. Contains the full UI layer including:
- Custom CSS design system (Source Code Pro font, #000000/#7E3BED/#C6FF34/#FFFFFF palette)
- Hero section with branding
- Input card for research topic entry
- Real-time pipeline status tracker with animated state indicators
- Results display with expanders, report panel, and critic feedback
- Download functionality for generated reports

**`agents.py`** — Core agent logic:
- `MiniMaxLLM` — Custom LangChain LLM wrapper that communicates with OpenRouter API
- `SearchAgent` — Invokes the `web_search` tool and returns structured results
- `ReaderAgent` — Uses LLM to identify best URL, then scrapes it via `scrape_url`
- `writer_chain` — LCEL chain (prompt → LLM → output parser) for report generation
- `critic_chain` — LCEL chain for report critique and scoring

**`tools.py`** — LangChain tools:
- `web_search(query)` — Searches via Tavily API, returns top 5 results
- `scrape_url(url)` — Scrapes a URL with BeautifulSoup, returns clean text (max 3000 chars)

---

## Setup and Installation

### Prerequisites

- Python 3.10 or higher
- An OpenRouter API key ([get one here](https://openrouter.ai/))
- A Tavily API key ([get one here](https://tavily.com/))

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Multi-Agent-System.git
cd Multi-Agent-System
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment:

**Windows:**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
TAVILY_API_KEY=your_tavily_api_key_here
MINIMAX_API_KEY=your_openrouter_api_key_here
```

### Step 5: Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

---

## Usage

1. **Enter a Research Topic** — Type any topic into the input field (e.g., "Quantum computing breakthroughs in 2025").

2. **Run the Pipeline** — Click the "Run Research Pipeline" button. The system will execute all four agents sequentially.

3. **Monitor Progress** — Watch the real-time pipeline status panel on the right side. Each stage transitions through `IDLE → ACTIVE → DONE`.

4. **Review Results** — After completion:
   - Expand "Search Results (raw)" to see raw search data
   - Expand "Scraped Content (raw)" to see extracted page content
   - Read the full research report in the main panel
   - Review the critic's score and feedback

5. **Download Report** — Click "Download Report (.md)" to save the generated report as a markdown file.

---

## Design System

The UI follows a carefully crafted dark terminal-inspired design language:

| Token            | Value      | Usage                                    |
|------------------|------------|------------------------------------------|
| **Background**   | `#000000`  | Primary background, pure black           |
| **Primary**      | `#7E3BED`  | Accents, active states, borders, labels  |
| **Secondary**    | `#C6FF34`  | CTA buttons, success states, highlights  |
| **Text**         | `#FFFFFF`  | Primary text, headings                   |
| **Font**         | Source Code Pro | All typography, monospaced terminal feel |

Additional design features:
- Subtle dot-grid background pattern
- Glassmorphism cards with gradient borders
- Animated pulse effect on active pipeline stages
- Custom scrollbar styling
- Responsive layout with Streamlit column system

---

## Configuration

### Changing the LLM Model

Edit the `model_name` field in `agents.py`:

```python
class MiniMaxLLM(LLM):
    model_name: str = "minimax-m2.5"  # Change to any OpenRouter-supported model
```

Available models on OpenRouter include:
- `openai/gpt-4o-mini`
- `anthropic/claude-3.5-sonnet`
- `google/gemini-2.0-flash`
- `meta-llama/llama-3.1-70b-instruct`
- And many more at [openrouter.ai/models](https://openrouter.ai/models)

### Adjusting Search Results

Edit `tools.py` to change the number of search results:

```python
results = tavily.search(query=query, max_results=5)  # Adjust max_results
```

### Adjusting Scrape Length

Edit `tools.py` to change the maximum scraped content length:

```python
return soup.get_text(separator=" ", strip=True)[:3000]  # Adjust character limit
```

---

## Dependencies

```
requests>=2.31.0          # HTTP requests for web scraping
httpx>=0.27.0             # Async HTTP client for LLM API calls
langchain>=0.2.0          # Core LangChain framework
langchain-core>=0.2.0     # LangChain abstractions (prompts, parsers)
langchain-community>=0.2.0 # Community integrations
tavily-python>=0.3.0      # Tavily web search API client
beautifulsoup4>=4.12.0    # HTML parsing and content extraction
lxml>=5.0.0               # Fast XML/HTML parser backend
aiohttp>=3.9.0            # Async HTTP support
pydantic>=2.7.0           # Data validation and settings
python-dotenv>=1.0.0      # .env file loader
tenacity>=8.2.0           # Retry logic for robustness
rich>=13.7.0              # Terminal formatting
orjson>=3.10.0            # Fast JSON parsing
faiss-cpu>=1.8.0          # Vector store (optional, for future features)
streamlit                 # Web application framework
```

---

## Troubleshooting

| Issue                                  | Solution                                                   |
|----------------------------------------|------------------------------------------------------------|
| `ModuleNotFoundError`                  | Run `pip install -r requirements.txt`                      |
| API key errors                         | Verify `.env` file exists and keys are correct             |
| `bind_tools` error                     | Ensure `agents.py` uses custom agent classes, not `create_react_agent` |
| Timeout errors                         | Increase timeout in `agents.py` (default: 60s)             |
| Empty search results                   | Check Tavily API key and quota                             |
| Streamlit won't start                  | Ensure virtual environment is activated                    |

---

## Developed By

**Akram** — Multi-Agent AI System with LangChain Pipeline

---

## License

This project is for educational and research purposes. See individual API providers for their terms of service.
