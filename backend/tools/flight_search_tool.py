from typing import List
from strands import tool
from tools.config.FlightOption import FlightOption


@tool
def search_flights(origin: str, destination: str, departure_date: str, return_date: str) -> str:
    """
    Busca vuelos entre el origen y el destino en las fechas indicadas y devuelve un resumen de los resultados.

    Args:
        origin: Código IATA o ciudad de origen (ej. "MAD")
        destination: Código IATA o ciudad de destino (ej. "ATH")
        departure_date: Fecha de salida en formato YYYY-MM-DD
        return_date: Fecha de regreso en formato YYYY-MM-DD
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
