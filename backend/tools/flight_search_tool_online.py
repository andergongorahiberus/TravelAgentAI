from strands import tool
from duckduckgo_search import DDGS


@tool
def search_flights_online(origin: str, destination: str, departure_date: str, return_date: str) -> str:
    """
        Busca información de vuelos en tiempo real usando DuckDuckGo.

        Args:
            origin: Ciudad o código IATA (ej. 'Madrid' o 'MAD')
            destination: Ciudad o código IATA (ej. 'Atenas' o 'ATH')
            departure_date: Fecha en formato YYYY-MM-DD
            return_date: Fecha de regreso en formato YYYY-MM-DD
        """
    query = f"vuelos de {origin} a {destination} el {departure_date} regreso {return_date} mejores precios"

    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]

        if not results:
            return "No se encontró información de vuelos para esas fechas."

        summary = [f"Resultados de búsqueda de {origin} a {destination}:"]
        for res in results:
            summary.append(f"- {res['title']}: {res['href']}\n  Resumen: {res['body']}\n")

        return "\n".join(summary)

    except Exception as e:
        return f"Error al buscar vuelos: {str(e)}"