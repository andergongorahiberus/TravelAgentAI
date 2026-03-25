from pydantic import BaseModel, Field

class FlightOption(BaseModel):
    airline: str = Field(..., description="Airline name")
    flight_number: str = Field(..., description="Unique flight ID")
    departure: datetime = Field(..., description="Departure time")
    price: float = Field(..., description="Price of the flight")
    stops: int = Field(default=0, description="Number of layovers")