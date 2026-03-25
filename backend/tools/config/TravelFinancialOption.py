from pydantic import BaseModel, Field
from typing import List
from .FlightOption import FlightOption
from .HotelOption import HotelOption


class TravelFinancialOption(BaseModel):
    flight_options: List[FlightOption] = Field(
        ..., description="A list of flight options for the trip"
    )
    hotel_options: List[HotelOption] = Field(
        ..., description="A list of hotel options for the trip"
    )
    # total_cost: list[float]
