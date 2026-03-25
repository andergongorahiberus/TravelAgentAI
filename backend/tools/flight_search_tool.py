from typing import List
from strands import tool
from tools.config.FlightOption import FlightOption


@tool
def search_flights(origin: str, destination: str, departure_date: str, return_date: str) -> str:
    """
    Search for flights between origin and destination on the given dates and return a summary of the results.

    Args:
        origin: IATA code or city of origin (e.g. "MAD")
        destination: IATA code or city of destination (e.g. "ATH")
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format
    """
    options: List[FlightOption] = [
        FlightOption(airline="CloudAir", flight_number="CA42", price=350.0,
                     departure=f"{departure_date}T09:00:00", stops=0),
        FlightOption(airline="BudgetFly", flight_number="BF99", price=120.0,
                     departure=f"{departure_date}T22:30:00", stops=2),
    ]
    return "\n".join(
        f"{o.airline} {o.flight_number} — {o.price}€ — {o.stops} escala(s) — salida {o.departure}"
        for o in options
    )
