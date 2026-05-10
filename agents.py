"""Agents module for DeepResearchMind - LLM wrapper, agents, and chains."""

import logging
import re
from typing import Any, Dict, List, Optional, Union

import httpx
import os
from dotenv import load_dotenv

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from tools import web_search, scrape_url

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants - avoid magic numbers
DEFAULT_MAX_TOKENS: int = 2048
DEFAULT_TEMPERATURE: float = 0.0
DEFAULT_TIMEOUT: float = 60.0
SEARCH_RESULTS_TRUNCATION: int = 800

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# URL extraction pattern
URL_PATTERN = re.compile(r"https?://[^\s<>\"')\]]+")

# HTTP client singleton for connection pooling
_http_client: Optional[httpx.Client] = None


def _get_http_client() -> httpx.Client:
    """Get or create HTTP client with connection pooling."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.Client(
            timeout=DEFAULT_TIMEOUT,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
    return _http_client


def _validate_api_key() -> str:
    """Validate that API key is present."""
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        raise ValueError("MINIMAX_API_KEY environment variable is not set")
    return api_key


# ── LLM Wrapper (OpenRouter-compatible) ──
class MiniMaxLLM(LLM):
    """Custom LLM wrapper for OpenRouter API supporting MiniMax and other models."""

    model_name: str = "minimax-m2.5"
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS

    @property
    def _llm_type(self) -> str:
        return "minimax"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return identifying parameters."""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call OpenRouter API with proper error handling.

        Args:
            prompt: The prompt to send to the LLM.
            stop: Optional stop sequences.
            run_manager: Optional callback manager.
            **kwargs: Additional kwargs.

        Returns:
            The LLM response text.

        Raises:
            RuntimeError: If the API call fails.
        """
        api_key = _validate_api_key()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        if stop:
            payload["stop"] = stop

        try:
            client = _get_http_client()
            response = client.post(OPENROUTER_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0].get("message", {}).get("content", "")
                if content:
                    return content
            if "reply" in result:
                return result["reply"]

            logger.warning(f"Unexpected API response format: {result}")
            return str(result)
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error calling API: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e


# ── Model setup ──
llm = MiniMaxLLM(temperature=DEFAULT_TEMPERATURE)


# ── Search Agent ──
class SearchAgent:
    """Agent that searches the web using the Tavily tool directly."""

    def __init__(self, llm: LLM) -> None:
        """Initialize the search agent.

        Args:
            llm: The language model to use.
        """
        self.llm = llm

    def invoke(self, inputs: Dict[str, List[Union[tuple, BaseMessage]]]) -> Dict[str, List[AIMessage]]:
        """Invoke the search agent to perform web search.

        Args:
            inputs: Dictionary with 'messages' key containing user messages.

        Returns:
            Dictionary with search results in 'messages' key.
        """
        # Extract user message from inputs
        user_msg = inputs["messages"][-1][1]

        # Perform search using the web_search tool
        search_results = web_search.invoke({"query": user_msg})

        return {"messages": [AIMessage(content=search_results)]}


# ── Reader Agent ──
class ReaderAgent:
    """Agent that picks the best URL from search results and scrapes it."""

    def __init__(self, llm: LLM) -> None:
        """Initialize the reader agent.

        Args:
            llm: The language model to use.
        """
        self.llm = llm

    def invoke(self, inputs: Dict[str, List[Union[tuple, BaseMessage]]]) -> Dict[str, List[AIMessage]]:
        """Invoke the reader agent to extract and scrape relevant URL.

        Args:
            inputs: Dictionary with 'messages' key containing search results.

        Returns:
            Dictionary with scraped content in 'messages' key.
        """
        user_msg = inputs["messages"][-1][1]

        # Ask LLM to pick the best URL
        url_prompt = (
            "From the text below, extract the single most relevant URL to scrape "
            "for detailed information. Return ONLY the raw URL, nothing else.\n\n"
            f"{user_msg}"
        )

        try:
            llm_response = self.llm.invoke(url_prompt).strip()
        except RuntimeError as e:
            logger.error(f"LLM failed to extract URL: {e}")
            return {"messages": [AIMessage(content=f"Error extracting URL: {str(e)}")]}

        # Extract URL from LLM response
        urls = URL_PATTERN.findall(llm_response)

        if urls:
            scraped = scrape_url.invoke({"url": urls[0]})
        else:
            # Fallback: try to find URLs in the original message
            fallback_urls = URL_PATTERN.findall(user_msg)
            if fallback_urls:
                scraped = scrape_url.invoke({"url": fallback_urls[0]})
            else:
                scraped = "Could not extract a valid URL from search results."

        return {"messages": [AIMessage(content=scraped)]}


def build_search_agent() -> SearchAgent:
    """Build and return a SearchAgent instance.

    Returns:
        A configured SearchAgent.
    """
    return SearchAgent(llm)


def build_reader_agent() -> ReaderAgent:
    """Build and return a ReaderAgent instance.

    Returns:
        A configured ReaderAgent.
    """
    return ReaderAgent(llm)


# ── Writer Chain ──
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()


# ── Critic Chain ──
critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()
