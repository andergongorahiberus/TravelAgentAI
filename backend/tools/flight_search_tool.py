from strands import tool

@tool
def search_flights(origin: str, destination: str, departure_date: str, return_date: str) -> List[FlightOption]:
    """
    search for flights between origin and destination on the given dates and return a summary of the results.
    """
    return [
        FlightOption(airline="CloudAir", flight_number="CA42", price=350.0, 
                     departure=f"{date}T09:00:00", stops=0),
        FlightOption(airline="BudgetFly", flight_number="BF99", price=120.0, 
                     departure=f"{date}T22:30:00", stops=2)
    ]