from strands import tool
from duckduckgo_search import DDGS
import logging

logger = logging.getLogger(__name__)

@tool
def search_tool(query: str, max_results: int = 5) -> str:
    """Busca información en internet usando DuckDuckGo.
    
    Ideal para encontrar actividades y sus precios, lugares de interés y recomendaciones actualizadas.
    
    Args:
        query: La consulta de búsqueda (ej: 'mejores cosas que hacer en Santorini')
        max_results: Número de resultados a devolver (máximo 10)
    """
    try:
        results = []
        with DDGS() as ddgs:
            # Realizar la búsqueda de texto
            ddgs_gen = ddgs.text(query, max_results=max_results)
            for r in ddgs_gen:
                results.append(f"- {r['title']}: {r['body']}")
        
        if not results:
            return f"No se encontraron resultados para: {query}"
            
        return "\n".join(results)
        
    except Exception as e:
        logger.error(f"Error al buscar en DuckDuckGo: {e}")
        return f"Error en la búsqueda: {str(e)}"
