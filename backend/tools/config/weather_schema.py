from pydantic import BaseModel, Field
from typing import List


class DestinoWeather(BaseModel):
    name: str
    country: str
    lat: float
    lon: float
    weather_score: int = Field(ge=0, le=100)
    avg_temp_max_c: float
    avg_temp_min_c: float
    avg_precipitation_mm: float
    avg_wind_speed_kmh: float
    avg_sun_hours: float
    weather_summary: str = Field(description="Resumen en lenguaje natural del clima")
    data_source: str = Field(description="Ej: 'weather_archive (julio 2025)'")


class DestinoDescartado(BaseModel):
    name: str
    reason: str = Field(description="Motivo del descarte con score incluido")


class ListaWeather(BaseModel):
    """Salida del weather_agent. Propaga el contexto de ListaDestinos."""

    # Contexto pass-through (viene de ListaDestinos)
    origin: str
    theme: str
    budget_eur: float
    departure_date: str
    return_date: str

    # Resultados del agente
    filtered_destinations: List[DestinoWeather] = Field(
        description="Destinos con score >= 40, ordenados de mayor a menor score"
    )
    discarded: List[DestinoDescartado] = Field(
        default_factory=list,
        description="Destinos descartados por mal clima (score < 40)",
    )