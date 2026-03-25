"""Weather Agent — Filters destination candidates by climate suitability.

This agent receives a list of destinations with coordinates and travel dates,
queries real weather data via Open-Meteo MCP, scores each destination using
the climate_scorer tool, and returns only those with favorable weather.

Architecture:
  - Open-Meteo MCP provides: weather_forecast, weather_archive, geocoding, etc.
  - calculate_climate_score is a custom @tool for scoring logic
  - Both are passed to the Agent as tools — Strands handles MCP lifecycle
"""

import os

from strands import Agent
from strands.models import BedrockModel

from tools.weather_mcp import create_open_meteo_mcp
from tools.climate_scorer_tool import calculate_climate_score

from ..tools.config.weather_schema import ListaWeather


# Resolve prompts directory relative to project root
PROMPT = """
Eres un meteorólogo experto especializado en turismo. Tu misión es evaluar el clima de una lista de destinos candidatos para unas fechas de viaje concretas y filtrar los que no tengan buen tiempo.

## CONTEXTO

Recibirás:
1. Una lista de destinos candidatos (cada uno con nombre, país, latitud, longitud)
2. Fechas de viaje (ida y vuelta)
3. Temática del viaje (playa, montaña, ciudad, rural)

## HERRAMIENTAS DISPONIBLES

Tienes acceso a la API de Open-Meteo a través de herramientas MCP:

- **weather_forecast**: Previsión a 7-16 días. Úsala cuando las fechas del viaje están dentro de los próximos 16 días.
  Parámetros clave: latitude, longitude, daily (usa: ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max", "sunshine_duration"]), timezone: "auto"

- **weather_archive**: Datos históricos desde 1940. Úsala cuando las fechas del viaje están a MÁS de 16 días en el futuro.
  Estrategia: consulta las mismas fechas (día/mes) pero del AÑO ANTERIOR para obtener datos climáticos representativos.
  Parámetros clave: latitude, longitude, start_date, end_date (formato YYYY-MM-DD), daily (mismas variables que forecast)

- **geocoding**: Busca coordenadas por nombre de ciudad. Úsala SOLO si un destino no tiene coordenadas.

También tienes:
- **calculate_climate_score**: Calcula un score de 0 a 100 basado en temperatura, lluvia, sol y viento para una temática concreta.

## PROCESO PASO A PASO

1. Para CADA destino candidato:
   a. Determina si las fechas de viaje están dentro de 16 días (usa weather_forecast) o más allá (usa weather_archive con fechas del año anterior).
   b. Solicita datos diarios: temperature_2m_max, temperature_2m_min, precipitation_sum, wind_speed_10m_max, sunshine_duration.
   c. Calcula promedios de los datos obtenidos.
   d. Usa calculate_climate_score con los promedios y la temática.

2. Filtra los destinos con score inferior a 40.

3. Ordena los destinos restantes de mayor a menor score.

## REGLAS IMPORTANTES

- SIEMPRE usa las herramientas para obtener datos reales. NUNCA inventes datos meteorológicos.
- Si weather_forecast no cubre las fechas (viaje a más de 16 días), usa weather_archive con las MISMAS fechas del año anterior.
  Ejemplo: viaje del 15/07/2026 al 22/07/2026 → consulta archive del 15/07/2025 al 22/07/2025.
- Convierte sunshine_duration de segundos a horas (dividir entre 3600).
- Si una herramienta falla para un destino, no lo descartes: asígnale un score neutro de 50 con una nota de "datos no disponibles".

## FORMATO DE SALIDA

Responde EXCLUSIVAMENTE con un JSON válido, sin texto adicional antes ni después:

{
  "filtered_destinations": [
    {
      "name": "Santorini",
      "country": "Grecia",
      "lat": 36.39,
      "lon": 25.46,
      "weather_score": 92,
      "avg_temp_max_c": 30.2,
      "avg_temp_min_c": 23.1,
      "avg_precipitation_mm": 0.3,
      "avg_wind_speed_kmh": 18.5,
      "avg_sun_hours": 11.2,
      "weather_summary": "Cielos despejados con temperaturas ideales para playa. Viento moderado pero sin lluvia.",
      "data_source": "weather_archive (julio 2025)"
    }
  ],
  "discarded": [
    {
      "name": "Edimburgo",
      "reason": "Score 28 — lluvia frecuente y temperaturas bajas para playa"
    }
  ]
"""


def create_weather_agent() -> Agent:
    """Create the Weather Agent with Open-Meteo MCP tools + climate scorer.

    The agent uses:
      - Open-Meteo MCP tools (weather_forecast, weather_archive, geocoding, etc.)
        → passed as MCPClient, Strands manages the subprocess lifecycle
      - calculate_climate_score (@tool)
        → custom scoring logic by travel theme

    Returns:
        Configured Agent instance ready to be used in the Graph.
    """

    # LLM model — change model_id / region as needed
    model = BedrockModel(
        model_id=os.getenv(
            "BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-20250514-v1:0"
        ),
        region_name=os.getenv("AWS_REGION", "us-west-2"),
    )

    # MCP client for Open-Meteo (Strands manages lifecycle automatically)
    open_meteo_mcp = create_open_meteo_mcp()

    # Create agent with both MCP tools and custom tools
    # When MCPClient is in the tools list, Strands:
    #   1. Starts the MCP server subprocess on first invocation
    #   2. Discovers all available tools (weather_forecast, weather_archive, etc.)
    #   3. Makes them available to the LLM alongside calculate_climate_score
    #   4. Shuts down the subprocess when the agent is done
    return Agent(
        name="weather",
        description=(
            "Meteorólogo experto que evalúa el clima de destinos candidatos "
            "usando datos reales de Open-Meteo y filtra por idoneidad climática."
        ),
        system_prompt=PROMPT,
        model=model,
        tools=[
            open_meteo_mcp,  # All Open-Meteo tools (forecast, archive, geocoding...)
            calculate_climate_score,  # Custom scoring by travel theme
        ],
        structured_output_model=ListaWeather,
    )


# ---------------------------------------------------------------------------
# Standalone test — run this file directly to test the agent in isolation
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Weather Agent (standalone)")
    print("=" * 60)

    agent = create_weather_agent()

    # Simulated input: what the Destinations agent would pass
    test_prompt = """
    Evalúa el clima para estos destinos candidatos.

    Fechas del viaje: 15/07/2026 al 22/07/2026
    Temática: playa

    Destinos candidatos:
    1. Santorini, Grecia (lat: 36.39, lon: 25.46)
    2. Algarve, Portugal (lat: 37.02, lon: -7.93)
    3. Edimburgo, Escocia (lat: 55.95, lon: -3.19)

    Filtra los destinos con mal tiempo para playa y devuélveme el JSON
    con los destinos aprobados, ordenados por weather_score.
    """

    print(f"\nPrompt:\n{test_prompt.strip()}\n")
    print("-" * 60)

    result = agent(test_prompt)

    print("\nResultado:")
    print(str(result))
