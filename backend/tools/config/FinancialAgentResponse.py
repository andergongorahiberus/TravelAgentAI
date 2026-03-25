from pydantic import BaseModel, Field
from typing import List
from .TravelFinancialOption import TravelFinancialOption


class FinancialAgentResponse(BaseModel):
    responses: List[TravelFinancialOption] = Field(
        ...,
        description="A list of financial options for the trip and different destinations",
    )
