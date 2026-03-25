from pydantic import BaseModel, Field

class FinancialAgentResponse(BaseModel):
    responses: List[TravelFinancialOption] = Field(..., description="A list of financial options for the trip and different destinations")