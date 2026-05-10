"""Tools module for DeepResearchMind - Web search and URL scraping utilities."""

from langchain.tools import tool
import logging
import re
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from typing import List

import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants - avoid magic numbers
DEFAULT_MAX_RESULTS: int = 5
SNIPPET_LENGTH: int = 300
SCRAPE_TIMEOUT: int = 8
MAX_SCRAPED_CHARS: int = 3000

# Constants for URL validation
URL_PATTERN = re.compile(
    r"^https?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
    r"localhost|"  # localhost
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP address
    r"(?::\d+)?$",
    re.IGNORECASE,
)


def _get_tavily_client() -> TavilyClient:
    """Create and return Tavily client with API key validation."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is not set")
    return TavilyClient(api_key=api_key)


def _validate_query(query: str) -> str:
    """Validate and sanitize search query input."""
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
    # Limit query length to prevent abuse
    sanitized = query.strip()[:500]
    return sanitized


def _validate_url(url: str) -> str:
    """Validate URL format."""
    if not url or not url.strip():
        raise ValueError("URL cannot be empty")
    # Basic URL validation
    if not URL_PATTERN.match(url.strip()):
        raise ValueError(f"Invalid URL format: {url}")
    return url.strip()


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic.

    Args:
        query: The search query string.

    Returns:
        Formatted string with search results including titles, URLs, and snippets.
    """
    # Validate input
    validated_query = _validate_query(query)

    try:
        tavily = _get_tavily_client()
        results = tavily.search(query=validated_query, max_results=DEFAULT_MAX_RESULTS)
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return f"Search error: {str(e)}"

    out: List[str] = []
    for r in results.get("results", []):
        title = r.get("title", "No title")
        url = r.get("url", "")
        content = r.get("content", "")[:SNIPPET_LENGTH]
        out.append(f"Title: {title}\nURL: {url}\nSnippet: {content}\n")

    if not out:
        return "No search results found."

    return "\n----\n".join(out)


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading.

    Args:
        url: The URL to scrape.

    Returns:
        Cleaned text content from the URL, or an error message.
    """
    # Validate input
    validated_url = _validate_url(url)

    try:
        resp = requests.get(
            validated_url,
            timeout=SCRAPE_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            allow_redirects=True,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch URL {validated_url}: {e}")
        return f"Could not fetch URL: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error scraping URL {validated_url}: {e}")
        return f"Could not scrape URL: {str(e)}"

    try:
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove unwanted tags
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        # Truncate to max characters
        return text[:MAX_SCRAPED_CHARS]
    except Exception as e:
        logger.error(f"Failed to parse HTML from {validated_url}: {e}")
        return f"Could not parse content: {str(e)}"
