# api-troubleshoot

Debug API errors for Tavily (search) and OpenRouter/MiniMax (LLM), handle rate limits, timeouts, and authentication issues.

## When to Use

- Tavily API errors (quota exceeded, invalid key, empty results)
- OpenRouter/MiniMax API errors (authentication, rate limits, timeouts)
- HTTP 401/403/429 status codes
- Empty or malformed API responses
- Connection timeout issues
- Model not supported errors

## How to Debug

1. Check `.env` for API key configuration
2. Verify API keys are valid and have quota remaining
3. Check `agents.py` for API call implementation
4. Look at `tools.py` for Tavily web_search usage
5. Test API keys directly with curl
6. Check for correct endpoint URLs

## Tools to Use

- Grep: Search for `api_key`, `API_KEY`, `httpx`, `requests`
- Read: Inspect agents.py and .env for configuration
- Bash: Test API with direct curl requests