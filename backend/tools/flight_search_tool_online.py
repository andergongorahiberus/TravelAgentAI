from strands import tool
from duckduckgo_search import DDGS


@tool
def search_flights_online(origin: str, destination: str, departure_date: str, return_date: str) -> str:
    """
        Search for real-time flight information using DuckDuckGo.
        
        Args:
            origin: City or IATA code (e.g., 'Madrid' or 'MAD')
            destination: City or IATA code (e.g., 'Athens' or 'ATH')
            departure_date: Date in YYYY-MM-DD format
            return_date: Date in YYYY-MM-DD format
        """
    query = f"flights from {origin} to {destination} on {departure_date} returning {return_date} best prices"
    
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
        
        if not results:
            return "No flight information found for those dates."

        summary = [f"Search results for {origin} to {destination}:"]
        for res in results:
            summary.append(f"- {res['title']}: {res['href']}\n  Snippet: {res['body']}\n")
            
        return "\n".join(summary)

    except Exception as e:
        return f"Error searching for flights: {str(e)}"