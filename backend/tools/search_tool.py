# tools/search_tool.py
from strands import tool
import os
import json

MOCK_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "mocks.json")

@tool
def search_tool(query: str) -> str:
    """MOCK: Busca actividades, planes y lugares de interés en el destino sugerido.
    
    Args:
        query: Consulta sobre actividades (ej: 'qué hacer en Santorini', 'restaurantes en Paris')
    """
    if os.path.exists(MOCK_FILE):
        try:
            with open(MOCK_FILE, "r", encoding="utf-8") as f:
                mocks = json.load(f).get("search", {})
                query_lower = query.lower()
                
                # Búsqueda de actividades en los mocks
                for key, data in mocks.items():
                    if "actividades" in key.lower() and key.lower().split()[0] in query_lower:
                        return data
                
                # Fallback genérico por ciudad
                for key, data in mocks.items():
                    if key.lower().split()[0] in query_lower:
                        return data
        except Exception:
            pass

    return f"Simulación de búsqueda de actividades para: '{query}'. Se han encontrado varios puntos de interés y recomendaciones locales."
