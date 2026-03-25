import os
from strands import Agent
from strands.models import BedrockModel
from tools.search_tool import search_tool
from tools.config.planification_schema import TravelReport

# Configuración básica
AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
model_id = os.getenv("BEDROCK_MODEL_ID", "eu.anthropic.claude-sonnet-4-20250514-v1:0")

model = BedrockModel(model_id=model_id)
planner_prompt = """
Eres el 'Agente Planificador' y el nodo final del proceso. 
Tu responsabilidad es doble:
1. CREAR UN ITINERARIO: Basándote en el destino elegido y la información recibida (clima, precios, hoteles, vuelos), busca planes específicos para cada día usando 'search_tool' que es una busqueda en internet. Si no encuentras resultados, puedes inventartelos. También aporta el precio aproximado de cada actividad y se tiene que ajustar al presupuesto del usuario teniendo en cuenta lo gastado en hoteles y vuelos.
2. GENERAR EL REPORTE FINAL: Consolidar TODO el flujo en un único reporte estructurado para el usuario.

RECIBIRÁS (vía shared_state u output del nodo anterior):
- Destino ganador con coordenadas.
- Info meteorológica (probabilidad de lluvia, sol, etc.).
- Detalles financieros (vuelos específicos encontrados, hotel seleccionado, presupuesto total).

TAREAS:
- Genera un itinerario día a día con mañana, mediodía, tarde y noche.
- Incluye planes alternativos para la lluvia si es necesario.
- Resume los detalles de vuelos y hoteles que ya han sido seleccionados por los agentes anteriores.
- Proporciona un reporte final sólido y amigable.

RESPUESTA:
Debes responder un objeto JSON que siga exactamente la estructura de 'TravelReport'.
No busques nuevos vuelos ni hoteles, usa los que ya te vienen dados.
"""


def create_planner_agent() -> Agent:
    """Crea el agente planificador que consolida la información y añade actividades."""

    model = BedrockModel(model_id=model_id, region_name=AWS_REGION)

    return Agent(
        name="planner",
        description="Consolida la información de todo el viaje y genera el itinerario de actividades.",
        system_prompt=planner_prompt,
        model=model,
        tools=[search_tool],
        structured_output_model=TravelReport,
    )
