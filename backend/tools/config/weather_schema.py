from pydantic import BaseModel
from typing import List
from .destinations_schema import DestinoFinal


class ListaWeather(BaseModel):
    origin: str
    theme: str
    budget_eur: float
    departure_date: str
    return_date: str
    candidates: List[DestinoFinal]
