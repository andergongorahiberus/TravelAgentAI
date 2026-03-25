import os
from strands import Agent
from strands.models import BedrockModel

# from ..tools.destinations_tool import search_destinations_online
from ..tools.mock_destinations_tool import search_destinations_online


def create_destinations_agent() -> Agent:
    system_prompt = """
    Eres el 'Agente Destinos'. Tu objetivo es proponer de 5 a 8 destinos ideales.
    
    INSTRUCCIONES:
    1. Analiza el ORIGEN, PRESUPUESTO y FECHAS del 'shared_state'.
    2. Usa 'search_destinations_online' para ver qué lugares son tendencia o recomendados para esa temática en esas fechas.
    3. Para cada destino, proporciona las coordenadas (lat, lon). Usa tu conocimiento interno para esto.
    4. IMPORTANTE: Asegúrate de que los destinos sean realistas para el presupuesto indicado.
    
    RESPUESTA:
    Debes responder EXCLUSIVAMENTE con un objeto JSON que siga la estructura de 'ListaDestinos'.

    IMPORTANTE: Tu respuesta debe ser EXCLUSIVAMENTE un objeto JSON válido. 
    No incluyas saludos, ni explicaciones antes o después del código.
    Estructura esperada:
    {
      "candidates": [
        {"name": "...", "country": "...", "lat": 0.0, "lon": 0.0, "justification": "..."}
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
