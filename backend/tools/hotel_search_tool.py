import logging
from strands import tool

logger = logging.getLogger(__name__)

@tool
def search_hotels(destination: str, check_in_date: str, check_out_date: str) -> List[HotelOption]:
    """
    Search for hotels in the destination on the given dates and return a summary of the results.
    """
    # Mocked data to simulate an API response from a provider like Expedia or Booking
    mock_hotels: List[HotelOption] = [
        HotelOption(name=f"Luxury Palace {destination}", rating=5.0, price_per_night=450.0, 
                    amenities=["Spa", "Pool", "Valet"]),
        HotelOption(name=f"Downtown {destination} Inn", rating=3.5, price_per_night=110.0, 
                    amenities=["WiFi", "Breakfast"])
    ]
    logger.debug(f"Searching hotels in {destination} from {check_in_date} to {check_out_date}")
    
    return mock_hotels