import logging
from typing import List
from strands import tool
from tools.config.HotelOption import HotelOption

logger = logging.getLogger(__name__)


@tool
def search_hotels(destination: str, check_in_date: str, check_out_date: str) -> str:
    """
    Busca hoteles en el destino en las fechas indicadas y devuelve un resumen de los resultados.

    Args:
        destination: Nombre de la ciudad o destino (ej. "Santorini")
        check_in_date: Fecha de entrada en formato YYYY-MM-DD
        check_out_date: Fecha de salida en formato YYYY-MM-DD
    """
    mock_hotels: List[HotelOption] = [
        HotelOption(name=f"Luxury Palace {destination}", rating=5.0,
                    price_per_night=450.0, amenities=["Spa", "Pool", "Valet"]),
        HotelOption(name=f"Downtown {destination} Inn", rating=3.5,
                    price_per_night=110.0, amenities=["WiFi", "Breakfast"]),
    ]
    logger.debug("Buscando hoteles en %s del %s al %s", destination, check_in_date, check_out_date)
    return "\n".join(
        f"{h.name} — {h.price_per_night}€/noche — {h.rating}⭐ — {', '.join(h.amenities)}"
        for h in mock_hotels
    )
