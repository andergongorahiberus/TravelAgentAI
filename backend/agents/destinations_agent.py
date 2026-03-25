import os
import json
from strands import Agent
from strands.models import BedrockModel

from tools.destinations_tool import search_destinations_online

# from tools.mock_destinations_tool import search_destinations_online
from tools.config.destinations_schema import ListaDestinos


def create_destinations_agent() -> Agent:
    """
    Crea el Agente de Destinos.
    Entrada esperada en shared_state: UserTravelQuery
    Salida esperada (formato JSON): ListaDestinos
    """

    output_schema = json.dumps(ListaDestinos.model_json_schema(), indent=2)

    system_prompt = f"""
    Eres el 'Agente Destinos'. Tu misión es ser la primera pieza del puzzle de viajes.
    
    CONTEXTO DE ENTRADA:
    Recibirás un 'shared_state' que sigue el modelo 'UserTravelQuery'. 
    Debes leer: origin, theme, budget_eur, departure_date y return_date.
    
    TAREA:
    1. Usa 'search_destinations_online' para buscar lugares basados en 'origin' y 'theme'.
    2. Filtra los resultados que no encajen con el 'budget_eur' o las fechas.
    3. Genera de 5 a 8 candidatos con sus coordenadas (lat, lon) usando tu conocimiento.
    
    FORMATO DE SALIDA (ESTRICTO):
    Debes responder EXCLUSIVAMENTE con un objeto JSON que cumpla con el siguiente esquema de Pydantic:
    {output_schema}

    REGLA DE ORO: No incluyas explicaciones, solo el JSON puro. 
    Asegúrate de propagar los datos originales (origin, theme, etc.) en el JSON de salida.
    """

    model = BedrockModel(
        model_id="eu.anthropic.claude-3-5-sonnet-20240620-v1:0",
        region_name=os.getenv("AWS_REGION", "eu-west-1"),
    )

    return Agent(
        name="destinations",
        description="Busca destinos en internet y devuelve coordenadas y justificación",
        system_prompt=system_prompt,
        model=model,
        tools=[search_destinations_online],
        structured_output_model=ListaDestinos,
    )
