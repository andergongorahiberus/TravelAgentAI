import logging
from typing import List
from strands import tool
from tools.config.HotelOption import HotelOption

logger = logging.getLogger(__name__)


@tool
def search_hotels(destination: str, check_in_date: str, check_out_date: str) -> str:
    """
    Search for hotels in the destination on the given dates and return a summary of the results.

    Args:
        destination: City or destination name (e.g. "Santorini")
        check_in_date: Check-in date in YYYY-MM-DD format
        check_out_date: Check-out date in YYYY-MM-DD format
    """
    mock_hotels: List[HotelOption] = [
        HotelOption(name=f"Luxury Palace {destination}", rating=5.0,
                    price_per_night=450.0, amenities=["Spa", "Pool", "Valet"]),
        HotelOption(name=f"Downtown {destination} Inn", rating=3.5,
                    price_per_night=110.0, amenities=["WiFi", "Breakfast"]),
    ]
    logger.debug("Searching hotels in %s from %s to %s", destination, check_in_date, check_out_date)
    return "\n".join(
        f"{h.name} — {h.price_per_night}€/noche — {h.rating}⭐ — {', '.join(h.amenities)}"
        for h in mock_hotels
    )
