from pydantic import BaseModel, Field
from typing import List, Optional

class ActividadDia(BaseModel):
    day: int
    title: str
    morning: str
    lunch: str
    afternoon: str
    evening: str
    rain_plan: Optional[str] = None


class DetalleFinanciero(BaseModel):
    item: str = Field(description="Ej: 'Vuelo Madrid-Santorini', 'Hotel Oia Sunset'")
    price_eur: float
    details: str = Field(description="Descripción breve o fuente")


class TravelReport(BaseModel):
    destination: str
    itinerary: List[ActividadDia]
    budget_breakdown: List[DetalleFinanciero]
    total_estimated_price: float
    general_tips: List[str]
    summary_report: str = Field(description="Resumen completo de todo el flujo y decisiones tomadas.")
