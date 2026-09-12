# src/tools/search_tools.py

import logging
import urllib.request
from bs4 import BeautifulSoup
from ddgs import DDGS

logger = logging.getLogger(__name__)

def fetch_page_content(url: str, timeout: int = 5) -> str:
    """Scrapes the actual visible text from a webpage URL to get deep data."""
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            html = response.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove scripts, styles, and footers to keep text clean
            for element in soup(["script", "style", "footer", "nav", "header"]):
                element.decompose()
                
            text = soup.get_text(separator=' ')
            # Clean up extra whitespace
            cleaned_text = " ".join(text.split())
            return cleaned_text[:3000]  # Limit to first 3000 chars to save tokens
    except Exception as e:
        logger.warning(f"Could not scrape webpage content from {url}: {e}")
        return ""

def search_community_discussions(query: str, max_results: int = 3) -> str:
    """
    Finds top local links across Google Maps references, Justdial indexes, 
    and blogs, then reads the actual text content of those pages.
    """
    clean_query = query.replace("site:://", "").replace("https://", "").strip()
    
    # Target actual local data discoverability
    search_query = f"Nagpur market bazaar lane for {clean_query}"
    logger.info(f"Launching deep harvester web query: '{search_query}'")
    
    web_data = []
    try:
        ddgs = DDGS(timeout=8)
        results = list(ddgs.text(search_query, max_results=max_results))
        
        for idx, r in enumerate(results):
            url = r.get("href")
            title = r.get("title", "")
            snippet = r.get("body", "")
            
            logger.info(f"[{idx+1}/{len(results)}] Scraping deep page content from: {url}...")
            # Go beyond the snippet: fetch the actual text written on the page
            page_text = fetch_page_content(url)
            
            combined_context = f"Title: {title}\nURL: {url}\nSnippet: {snippet}\nDeep Page Content: {page_text}"
            web_data.append(combined_context)
            
    except Exception as e:
        logger.error(f"Harvester deep search failed: {e}")

    return "\n\n=== NEXT SOURCE ===\n\n".join(web_data) if web_data else ""
