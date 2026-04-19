from langchain_core.language_models.llms import LLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.messages import AIMessage
from tools import web_search, scrape_url
from dotenv import load_dotenv
import httpx
import os
import re
from typing import Optional, List, Any

load_dotenv()

# ── LLM Wrapper (OpenRouter-compatible) ──
class MiniMaxLLM(LLM):
    """Custom LLM wrapper for OpenRouter API"""

    api_key: str = os.getenv("MINIMAX_API_KEY", "")
    model_name: str = "minimax-m2.5"
    temperature: float = 0

    @property
    def _llm_type(self) -> str:
        return "minimax"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call OpenRouter API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": 2048
        }

        try:
            with httpx.Client() as client:
                response = client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()

                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0].get("message", {}).get("content", "")
                elif "reply" in result:
                    return result["reply"]
                else:
                    return str(result)
        except Exception as e:
            return f"Error calling API: {str(e)}"


# ── Model setup ──
llm = MiniMaxLLM(temperature=0)


# ── Search Agent ──
class SearchAgent:
    """Agent that searches the web using the Tavily tool directly."""

    def __init__(self, llm):
        self.llm = llm

    def invoke(self, inputs):
        user_msg = inputs["messages"][-1][1]
        # Extract a concise search query from the user message
        search_results = web_search.invoke({"query": user_msg})
        return {"messages": [AIMessage(content=search_results)]}


# ── Reader Agent ──
class ReaderAgent:
    """Agent that picks the best URL from search results and scrapes it."""

    def __init__(self, llm):
        self.llm = llm

    def invoke(self, inputs):
        user_msg = inputs["messages"][-1][1]

        # Ask LLM to pick the best URL
        url_prompt = (
            "From the text below, extract the single most relevant URL to scrape "
            "for detailed information. Return ONLY the raw URL, nothing else.\n\n"
            f"{user_msg}"
        )
        llm_response = self.llm.invoke(url_prompt).strip()

        # Extract URL from LLM response
        urls = re.findall(r'https?://[^\s<>"\')\]]+', llm_response)

        if urls:
            scraped = scrape_url.invoke({"url": urls[0]})
        else:
            # Fallback: try to find URLs in the original message
            fallback_urls = re.findall(r'https?://[^\s<>"\')\]]+', user_msg)
            if fallback_urls:
                scraped = scrape_url.invoke({"url": fallback_urls[0]})
            else:
                scraped = "Could not extract a valid URL from search results."

        return {"messages": [AIMessage(content=scraped)]}


def build_search_agent():
    return SearchAgent(llm)

def build_reader_agent():
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
