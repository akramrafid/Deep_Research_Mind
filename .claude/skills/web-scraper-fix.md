# web-scraper-fix

Fix web scraping issues, handle dynamic content, bypass anti-bot protection, and improve scraper reliability.

## When to Use

- scrape_url returns empty or partial content
- Websites blocking requests (403, 429 errors)
- JavaScript-rendered content not captured
- Parsing errors in BeautifulSoup
- Rate limiting or timeout issues
- Invalid URL extraction from search results

## How to Debug

1. Check `tools.py` for scrape_url implementation
2. Verify BeautifulSoup parsing method
3. Test URL directly with curl/requests
4. Check User-Agent header configuration
5. Look at ReaderAgent for URL extraction logic

## Tools to Use

- Grep: Search for `scrape_url`, `BeautifulSoup`, `requests`
- Read: Inspect tools.py for scraping implementation
- Bash: Test scraping with Python requests directly