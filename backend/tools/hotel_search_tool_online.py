import logging
import re
from strands import tool
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

@tool
def search_hotels_online(destination: str, check_in_date: str, check_out_date: str) -> str:
    """
    Busca hoteles con foco en extraer datos de precio de los fragmentos de búsqueda.

    Args:
        destination: Nombre de la ciudad o destino (ej. "Santorini")
        check_in_date: Fecha de entrada en formato YYYY-MM-DD
        check_out_date: Fecha de salida en formato YYYY-MM-DD
    """
    # Query optimizada para obtener fragmentos con precios (Booking, Expedia, etc.)
    query = f"precios hotel {destination} {check_in_date} hasta {check_out_date} precio por noche"

    logger.debug("Búsqueda de precios en directo para %s", destination)

    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=10)]

        if not results:
            return f"No se encontraron hoteles para {destination}."

        summary = [f"--- BÚSQUEDA DE HOTELES: {destination} ({check_in_date} / {check_out_date}) ---"]

        for res in results:
            text_to_scan = f"{res['title']} {res['body']}"

            price_match = re.search(r'([€$£]\s?\d+(?:[.,]\d{2})?|desde\s\d+|from\s\d+)', text_to_scan, re.IGNORECASE)

            price_info = f"PRECIO ENCONTRADO: {price_match.group(0)}" if price_match else "Precio no disponible en el fragmento"

            summary.append(
                f"Hotel/Fuente: {res['title']}\n"
                f"Tarifa extraída: **{price_info}**\n"
                f"Enlace de reserva: {res['href']}\n"
                f"Descripción: {res['body']}\n"
                f"{'-'*30}"
            )

        return "\n".join(summary)

    except Exception as e:
        logger.error("Búsqueda de hoteles fallida: %s", str(e))
        return f"Error: {str(e)}"