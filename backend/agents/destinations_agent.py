import os
from strands import Agent
from strands.models import BedrockModel

# from ..tools.destinations_tool import search_destinations_online
from ..tools.mock_destinations_tool import search_destinations_online


def create_destinations_agent() -> Agent:
    system_prompt = """
    Eres el 'Agente Destinos'. Tu salida será el punto de partida para otros agentes.
    
    CONTEXTO:
    Lee del 'shared_state' los datos: origin, theme, budget_eur, departure_date y return_date.
    
    TAREA:
    1. Usa 'search_destinations_online' pasando el origen y tema.
    2. Selecciona los mejores destinos.
    3. Genera un JSON que NO SOLO tenga los destinos, sino que RECOJA también los datos originales.
    
    FORMATO DE RESPUESTA (JSON ESTRICTO):
    {
      "origin": "Ciudad de origen",
      "theme": "Temática elegida",
      "budget_eur": 0.0,
      "departure_date": "YYYY-MM-DD",
      "return_date": "YYYY-MM-DD",
      "candidates": [
        {
          "name": "...",
          "country": "...",
          "lat": 0.0,
          "lon": 0.0,
          "justification": "..."
        }
      ]
    }
    """

    model = BedrockModel(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        region_name=os.getenv("AWS_REGION", "eu-west-1"),
    )

    return Agent(
        name="destinations",
        description="Busca destinos en internet y devuelve coordenadas y justificación",
        system_prompt=system_prompt,
        model=model,
        tools=[search_destinations_online],
    )
