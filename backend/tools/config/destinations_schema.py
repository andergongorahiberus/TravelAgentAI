from pydantic import BaseModel, Field
from typing import List
from datetime import date


class UserTravelQuery(BaseModel):
    origin: str = Field(..., examples=["Madrid"])
    theme: str = Field(..., examples=["Aventura"])
    budget_eur: float = Field(..., gt=0, examples=[1500.0])
    departure_date: date = Field(..., examples=["2026-10-10"])
    return_date: date = Field(..., examples=["2026-10-20"])


class DestinoEncontrado(BaseModel):
    nombre_sitio: str
    resumen: str
    url: str


class RespuestaBusqueda(BaseModel):
    query: str
    origin: str
    theme: str
    resultados: List[DestinoEncontrado]


class DestinoFinal(BaseModel):
    name: str = Field(description="Nombre de la ciudad o destino")
    country: str
    lat: float
    lon: float
    justification: str = Field(description="Por qué este destino encaja")


class ListaDestinos(BaseModel):
    origin: str
    theme: str
    budget_eur: float
    departure_date: str
    return_date: str
    candidates: List[DestinoFinal]
