from pydantic import BaseModel, Field
from typing import List


class DestinoEncontrado(BaseModel):
    nombre_sitio: str
    resumen: str
    url: str


class RespuestaBusqueda(BaseModel):
    query: str
    resultados: List[DestinoEncontrado]


class DestinoFinal(BaseModel):
    name: str = Field(description="Nombre de la ciudad o destino")
    country: str
    lat: float
    lon: float
    justification: str = Field(description="Por qué este destino encaja")


class ListaDestinos(BaseModel):
    candidates: List[DestinoFinal]
