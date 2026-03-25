from pydantic import BaseModel

class HotelOption(BaseModel):
    name: str = Field(..., description="The name of the hotel")
    price_per_night: float = Field(..., descrtiption="The price per night")
    rating: float = Field(..., description="The average rating of the hotel")
    amenities: List[str] = Field(..., description="A list of amenities offered by the hotel")