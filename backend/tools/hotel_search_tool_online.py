import logging
import re
from strands import tool
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

@tool
def search_hotels(destination: str, check_in_date: str, check_out_date: str) -> str:
    """
    Search for hotels with a focus on extracting price data from search snippets.

    Args:
        destination: City or destination name (e.g. "Santorini")
        check_in_date: Check-in date in YYYY-MM-DD format
        check_out_date: Check-out date in YYYY-MM-DD format
    """
    # Optimized query to trigger price-rich snippets (e.g., Booking, Expedia, etc.)
    query = f"hotel rates {destination} {check_in_date} to {check_out_date} price per night"
    
    logger.debug("Live price search for %s", destination)

    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=10)]

        if not results:
            return f"No hotel results found for {destination}."

        summary = [f"--- HOTEL PRICE SEARCH: {destination} ({check_in_date} / {check_out_date}) ---"]
        
        for res in results:
            text_to_scan = f"{res['title']} {res['body']}"
            
            price_match = re.search(r'([€$£]\s?\d+(?:[.,]\d{2})?|from\s\d+)', text_to_scan, re.IGNORECASE)
            
            price_info = f"PRICE FOUND: {price_match.group(0)}" if price_match else "Price not explicitly in snippet"
            
            summary.append(
                f"Hotel/Source: {res['title']}\n"
                f"Extracted Rate: **{price_info}**\n"
                f"Booking Link: {res['href']}\n"
                f"Description: {res['body']}\n"
                f"{'-'*30}"
            )
            
        return "\n".join(summary)

    except Exception as e:
        logger.error("Hotel price search failed: %s", str(e))
        return f"Error: {str(e)}"