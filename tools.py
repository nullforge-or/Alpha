from playwright.sync_api import sync_playwright
from duckduckgo_search import DDGS

def browse_website(url: str) -> str:
    """Navigates to a URL and extracts the visible text."""
    print(f"[System] Executing tool: browse_website -> {url}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000)
            
            content = page.evaluate("""
                () => document.body.innerText
            """)
            browser.close()
            return content[:4000] 
    except Exception as e:
        return f"Error accessing {url}: {str(e)}"

def web_search(query: str) -> str:
    """Searches the internet for a query and returns the top 5 results with URLs."""
    print(f"[System] Executing tool: web_search -> {query}")
    try:
        results = DDGS().text(query, max_results=5)
        if not results:
            return "No results found."
        
        formatted_results = []
        for r in results:
            formatted_results.append(f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n")
            
        return "\n".join(formatted_results)
    except Exception as e:
        return f"Search failed: {str(e)}"

AVAILABLE_TOOLS = {
    "browse_website": browse_website,
    "web_search": web_search
}