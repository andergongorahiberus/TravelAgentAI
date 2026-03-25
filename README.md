# TravelAgent AI — Proyecto Final Hiberus AI University 2026

## 1. Visión del proyecto

**Problema:** Planificar un viaje implica cruzar manualmente múltiples fuentes (clima, vuelos, alojamiento, actividades) y consume horas. No existe una herramienta que, dada una fecha y una temática, recomiende un destino óptimo considerando clima + precio + actividades de forma integrada.

**Solución:** Un sistema multiagente que recibe fechas de ida/vuelta, temática (playa, montaña, ciudad, rural) y ciudad de origen, y devuelve una recomendación completa con destino, previsión meteorológica, desglose de precios y un itinerario día a día.

**Stack obligatorio:** Streamlit + Strands Agents SDK + AWS Bedrock (AgentCore)

**Demo:** 10 minutos en vivo. Input del usuario → orquestación visible → output en Streamlit.

---

## 2. Arquitectura general

```
┌─────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  Streamlit  │────▶│  AgentCore           │────▶│  AWS Bedrock    │
│  (Frontend) │◀────│  (Orquestador Graph) │◀────│  Claude / Nova  │
└─────────────┘     └──────────┬───────────┘     └─────────────────┘
                               │
            ┌──────────┬───────┴───────┬──────────┐
            ▼          ▼               ▼          ▼
     ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
     │  Agente    │ │ Agente   │ │ Agente   │ │ Agente       │
     │  Destinos  │ │ Meteo    │ │ Financ.  │ │ Planificador │
     │            │ │          │ │          │ │              │
     │ Tools:     │ │ Tools:   │ │ Tools:   │ │ Tools:       │
     │ - search   │ │ - weather│ │ - search │ │ - search     │
     │ - scraper  │ │ - scorer │ │ - calc   │ │ - places     │
     │ - db       │ │          │ │          │ │ - itinerary  │
     └────────────┘ └──────────┘ └──────────┘ └──────────────┘
```

**Patrón multiagente elegido:** `Graph` (GraphBuilder de Strands).
- Es un pipeline secuencial determinista: Destinos → Meteorólogo → Financiero → Planificador.
- La salida de cada nodo se pasa como input al siguiente.
- Flujo predecible, ideal para demo en vivo.

**Alternativa a considerar:** Si queréis que el orquestador decida dinámicamente qué agente invocar según el prompt del usuario (más flexible pero menos predecible para demo), usad `Swarm` en vez de `Graph`.

---

## 3. Estructura de archivos

```
travel-agent-ai/
├── app.py                          # Entry point Streamlit
├── requirements.txt
├── .env.example                    # Template de variables de entorno
├── README.md
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py             # GraphBuilder: define el grafo de agentes
│   ├── destinations_agent.py       # Agente Destinos
│   ├── weather_agent.py            # Agente Meteorólogo
│   ├── financial_agent.py          # Agente Financiero
│   └── planner_agent.py            # Agente Planificador
│
├── tools/
│   ├── __init__.py
│   ├── search_tool.py              # Wrapper Tavily/Serper
│   ├── weather_tool.py             # Llamadas a OpenWeatherMap
│   ├── flight_search_tool.py       # Búsqueda de vuelos
│   ├── hotel_search_tool.py        # Búsqueda de alojamiento
│   ├── places_tool.py              # Google Places API
│   ├── budget_calculator_tool.py   # Calculadora de presupuesto
│   └── climate_scorer_tool.py      # Scoring de clima por temática
│
├── config/
│   ├── __init__.py
│   ├── settings.py                 # Pydantic Settings (env vars)
│   └── destinations_db.json        # BD local de destinos por temática
│
├── prompts/
│   ├── destinations_system.txt     # System prompt agente Destinos
│   ├── weather_system.txt          # System prompt agente Meteorólogo
│   ├── financial_system.txt        # System prompt agente Financiero
│   └── planner_system.txt          # System prompt agente Planificador
│
└── tests/
    ├── test_tools.py
    └── test_agents.py
```

---

## 4. Dependencias

```txt
# requirements.txt
strands-agents>=1.0.0
strands-agents-tools
streamlit>=1.30.0
boto3>=1.34.0
python-dotenv>=1.0.0
pydantic-settings>=2.0.0
requests>=2.31.0
```

**Instalación:**

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows WSL: source .venv/bin/activate
pip install -r requirements.txt
```

---

## 5. Variables de entorno

```bash
# .env
AWS_REGION=us-west-2
AWS_PROFILE=default                    # o el perfil SSO de Hiberus

# APIs externas
TAVILY_API_KEY=tvly-xxxxx              # https://tavily.com (free tier: 1000 req/mes)
OPENWEATHERMAP_API_KEY=xxxxx           # https://openweathermap.org/api (free tier)
SERPER_API_KEY=xxxxx                   # https://serper.dev (alternativa/complemento a Tavily)

# Opcionales
GOOGLE_PLACES_API_KEY=xxxxx            # Para actividades y lugares
BEDROCK_MODEL_ID=anthropic.claude-sonnet-4-20250514-v1:0  # o amazon.nova-pro-v1:0
```

---

## 6. Definición de agentes

### 6.1 Agente Destinos

**Rol:** Generar una lista de 5-8 destinos candidatos según la temática y la época del año.

**System prompt (`prompts/destinations_system.txt`):**

```
Eres un experto en viajes y destinos turísticos. Tu misión es generar una lista de destinos
candidatos basándote en:
- La temática elegida por el usuario (playa, montaña, ciudad, rural, aventura)
- Las fechas del viaje (para considerar temporada alta/baja y estacionalidad)
- La ciudad de origen (para priorizar destinos accesibles)

REGLAS:
- Genera exactamente entre 5 y 8 destinos candidatos.
- Incluye destinos variados: algunos cercanos/económicos y otros más lejanos/premium.
- Para cada destino devuelve: nombre, país, coordenadas (lat, lon), y una breve justificación
  de por qué encaja con la temática.
- Prioriza destinos con buena conectividad aérea desde la ciudad de origen.
- Usa la herramienta de búsqueda para verificar que los destinos son relevantes para la
  temporada indicada.

FORMATO DE SALIDA (JSON):
{
  "candidates": [
    {
      "name": "Santorini",
      "country": "Grecia",
      "lat": 36.3932,
      "lon": 25.4615,
      "justification": "Destino icónico de playa con temporada ideal en junio-septiembre",
      "category_score": 9
    }
  ]
}
```

**Tools asignadas:**
- `search_web`: Búsqueda Tavily/Serper para verificar destinos y temporadas.
- `query_destinations_db`: Consulta la BD local JSON de destinos categorizados.

**Implementación:**

```python
# agents/destinations_agent.py
from strands import Agent, tool
from strands.models import BedrockModel
from tools.search_tool import search_web
from tools.destinations_db_tool import query_destinations_db

def create_destinations_agent() -> Agent:
    system_prompt = open("prompts/destinations_system.txt").read()

    model = BedrockModel(
        model_id="anthropic.claude-sonnet-4-20250514-v1:0",
        region_name="us-west-2"
    )

    return Agent(
        name="destinations",
        description="Genera destinos candidatos según temática, fechas y origen",
        system_prompt=system_prompt,
        model=model,
        tools=[search_web, query_destinations_db]
    )
```

---

### 6.2 Agente Meteorólogo

**Rol:** Filtrar los destinos candidatos por clima favorable en las fechas del viaje.

**System prompt (`prompts/weather_system.txt`):**

```
Eres un meteorólogo experto. Recibirás una lista de destinos candidatos y unas fechas de viaje.
Tu misión es:

1. Consultar la previsión meteorológica para cada destino en las fechas indicadas.
2. Calcular un "score climático" de 0-100 para cada destino, considerando:
   - Temperatura (según temática: playa quiere calor, montaña acepta frío)
   - Probabilidad de lluvia (penalizar lluvia para playa, menos relevante para ciudad)
   - Horas de sol
   - Viento (relevante para playa)
3. Filtrar destinos con score < 40 (clima desfavorable).
4. Devolver los destinos ordenados por score climático descendente.

REGLAS TEMÁTICAS DE CLIMA:
- Playa: Temperatura ideal 25-35°C, lluvia < 20%, sol > 8h
- Montaña: Temperatura 10-25°C, sin tormentas eléctricas
- Ciudad: Temperatura 15-30°C, lluvia < 40%
- Rural: Temperatura 15-28°C, sin condiciones extremas

FORMATO DE SALIDA (JSON):
{
  "filtered_destinations": [
    {
      "name": "Santorini",
      "country": "Grecia",
      "weather_score": 92,
      "avg_temp_c": 28,
      "rain_probability": 5,
      "sun_hours": 12,
      "weather_summary": "Cielos despejados, temperatura ideal para playa"
    }
  ]
}
```

**Tools asignadas:**
- `get_weather_forecast`: Llama a OpenWeatherMap API (forecast 5 días o datos históricos).
- `calculate_climate_score`: Función Python que calcula el score según temática.

**Implementación:**

```python
# agents/weather_agent.py
from strands import Agent
from strands.models import BedrockModel
from tools.weather_tool import get_weather_forecast
from tools.climate_scorer_tool import calculate_climate_score

def create_weather_agent() -> Agent:
    system_prompt = open("prompts/weather_system.txt").read()

    model = BedrockModel(
        model_id="anthropic.claude-sonnet-4-20250514-v1:0",
        region_name="us-west-2"
    )

    return Agent(
        name="weather",
        description="Filtra destinos por clima favorable según fechas y temática",
        system_prompt=system_prompt,
        model=model,
        tools=[get_weather_forecast, calculate_climate_score]
    )
```

---

### 6.3 Agente Financiero

**Rol:** Buscar precios reales de vuelos y alojamiento para los destinos filtrados.

**System prompt (`prompts/financial_system.txt`):**

```
Eres un analista financiero de viajes. Recibirás una lista de destinos filtrados por clima
favorable. Tu misión es:

1. Buscar precios estimados de vuelos ida/vuelta desde la ciudad de origen a cada destino.
2. Buscar precios estimados de alojamiento por noche para las fechas indicadas.
3. Calcular el presupuesto total estimado por destino:
   - Vuelo ida/vuelta
   - Alojamiento (precio/noche × número de noches)
   - Estimación de gastos diarios (comida + transporte local)
4. Si el usuario indicó un presupuesto máximo, filtrar destinos que lo superen.
5. Ordenar por mejor relación calidad-precio (weather_score / precio_total).

FORMATO DE SALIDA (JSON):
{
  "priced_destinations": [
    {
      "name": "Santorini",
      "country": "Grecia",
      "weather_score": 92,
      "flight_price_eur": 180,
      "hotel_price_per_night_eur": 95,
      "num_nights": 5,
      "daily_expenses_eur": 60,
      "total_budget_eur": 955,
      "value_score": 9.6,
      "price_source": "Búsqueda Serper - Skyscanner"
    }
  ]
}
```

**Tools asignadas:**
- `search_flights`: Búsqueda de vuelos vía Serper/Tavily (scraping de resultados de Google Flights / Skyscanner).
- `search_hotels`: Búsqueda de alojamiento vía Serper/Tavily.
- `calculate_budget`: Calculadora Python de presupuesto total.

---

### 6.4 Agente Planificador

**Rol:** Crear un itinerario día a día para el destino ganador.

**System prompt (`prompts/planner_system.txt`):**

```
Eres un planificador de viajes experto. Recibirás el destino ganador (o top 2) con toda su info
(clima, precios). Tu misión es crear un itinerario completo día a día.

Para cada día incluye:
- Mañana: actividad principal (monumento, playa, ruta de senderismo...)
- Mediodía: recomendación de restaurante o zona gastronómica
- Tarde: actividad secundaria o tiempo libre
- Noche: plan opcional (vida nocturna, paseo, cena especial)

REGLAS:
- Adapta las actividades a la temática (playa ≠ ciudad ≠ montaña).
- El primer día considera que llegas (medio día).
- El último día considera que te vas (mañana libre, check-out).
- Incluye al menos un "plan alternativo por si llueve" si el clima no es 100% seguro.
- Busca actividades reales, no inventadas. Usa las herramientas de búsqueda.

FORMATO DE SALIDA (JSON):
{
  "destination": "Santorini",
  "itinerary": [
    {
      "day": 1,
      "title": "Llegada y primera toma de contacto",
      "morning": "Llegada al aeropuerto, transfer al hotel en Oia",
      "lunch": "Ammoudi Fish Tavern - pescado fresco con vistas a la caldera",
      "afternoon": "Paseo por las callejuelas de Oia, atardecer desde el castillo",
      "evening": "Cena en Sunset Ammoudi",
      "rain_plan": null
    }
  ],
  "general_tips": [
    "El transporte en la isla es limitado, alquilar quad/moto es recomendable",
    "Reservar restaurantes al atardecer con al menos 2 días de antelación"
  ]
}
```

**Tools asignadas:**
- `search_web`: Buscar actividades, restaurantes, planes en el destino.
- `search_places`: Google Places API para obtener lugares reales con ratings.
- `generate_itinerary`: Función Python que estructura el itinerario final.

---

## 7. Orquestador (GraphBuilder)

```python
# agents/orchestrator.py
from strands.multiagent import GraphBuilder
from agents.destinations_agent import create_destinations_agent
from agents.weather_agent import create_weather_agent
from agents.financial_agent import create_financial_agent
from agents.planner_agent import create_planner_agent

def create_travel_graph():
    """Crea el grafo secuencial: Destinos → Meteo → Financiero → Planificador."""

    destinations = create_destinations_agent()
    weather = create_weather_agent()
    financial = create_financial_agent()
    planner = create_planner_agent()

    builder = GraphBuilder()

    # Añadir agentes como nodos
    builder.add_node(destinations, "destinations")
    builder.add_node(weather, "weather")
    builder.add_node(financial, "financial")
    builder.add_node(planner, "planner")

    # Definir edges (pipeline secuencial)
    builder.add_edge("destinations", "weather")
    builder.add_edge("weather", "financial")
    builder.add_edge("financial", "planner")

    # Entry point
    builder.set_entry_point("destinations")

    return builder.build()


def run_travel_agent(user_input: str, shared_state: dict = None):
    """Ejecuta el grafo completo y devuelve el resultado."""
    graph = create_travel_graph()
    result = graph(user_input, invocation_state=shared_state)
    return result
```

---

## 8. Frontend (Streamlit)

```python
# app.py
import streamlit as st
from datetime import date, timedelta
from agents.orchestrator import run_travel_agent

st.set_page_config(page_title="TravelAgent AI", page_icon="🌍", layout="wide")

st.title("🌍 TravelAgent AI")
st.markdown("Tu asistente de viajes con IA multiagente")

# --- Sidebar: Inputs del usuario ---
with st.sidebar:
    st.header("📝 Configura tu viaje")

    origin = st.text_input("📍 Ciudad de origen", value="Madrid")

    col1, col2 = st.columns(2)
    with col1:
        departure = st.date_input("📅 Ida", value=date.today() + timedelta(days=30))
    with col2:
        return_date = st.date_input("📅 Vuelta", value=date.today() + timedelta(days=37))

    theme = st.selectbox("🎯 Temática", ["Playa", "Montaña", "Ciudad", "Rural", "Aventura"])

    budget = st.slider("💰 Presupuesto máximo (€)", 200, 5000, 1500, step=100)

    num_travelers = st.number_input("👥 Viajeros", min_value=1, max_value=10, value=2)

    search_btn = st.button("🚀 ¡Buscar destino!", type="primary", use_container_width=True)

# --- Main area: Resultados ---
if search_btn:
    num_nights = (return_date - departure).days

    user_prompt = (
        f"Busco un viaje de {theme.lower()} desde {origin}. "
        f"Fechas: {departure.strftime('%d/%m/%Y')} al {return_date.strftime('%d/%m/%Y')} "
        f"({num_nights} noches). "
        f"Presupuesto máximo: {budget}€ para {num_travelers} persona(s). "
        f"Recomiéndame el mejor destino con buen tiempo, buen precio y un itinerario día a día."
    )

    shared_state = {
        "origin": origin,
        "departure": departure.isoformat(),
        "return_date": return_date.isoformat(),
        "num_nights": num_nights,
        "theme": theme.lower(),
        "budget_eur": budget,
        "num_travelers": num_travelers,
    }

    # Mostrar progreso
    with st.status("🔍 Buscando tu viaje perfecto...", expanded=True) as status:
        st.write("1️⃣ Generando destinos candidatos...")
        # TODO: Implementar streaming de eventos del grafo para actualizar el progreso
        result = run_travel_agent(user_prompt, shared_state)
        status.update(label="✅ ¡Viaje encontrado!", state="complete")

    # Mostrar resultado
    st.markdown("---")
    st.markdown(str(result))

    # TODO: Parsear el JSON de resultado y mostrar:
    # - st.metric() para precio, temperatura, score
    # - st.map() para ubicación del destino
    # - st.expander() para cada día del itinerario
    # - st.dataframe() para tabla comparativa de destinos
```

---

## 9. Tools — Implementación detallada

### 9.1 Search Tool (Tavily)

```python
# tools/search_tool.py
from strands import tool
import requests
import os

@tool
def search_web(query: str, max_results: int = 5) -> str:
    """Busca información en la web usando Tavily Search API.

    Args:
        query: La consulta de búsqueda
        max_results: Número máximo de resultados (default: 5)

    Returns:
        Resultados de búsqueda formateados como texto
    """
    api_key = os.getenv("TAVILY_API_KEY")
    response = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "include_answer": True,
        }
    )
    data = response.json()

    results = []
    if data.get("answer"):
        results.append(f"Resumen: {data['answer']}")

    for r in data.get("results", []):
        results.append(f"- {r['title']}: {r['content'][:200]}")

    return "\n".join(results)
```

### 9.2 Weather Tool

```python
# tools/weather_tool.py
from strands import tool
import requests
import os

@tool
def get_weather_forecast(lat: float, lon: float, destination_name: str) -> str:
    """Obtiene la previsión meteorológica para unas coordenadas.

    Args:
        lat: Latitud del destino
        lon: Longitud del destino
        destination_name: Nombre del destino para contexto

    Returns:
        Previsión meteorológica formateada
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")

    # Forecast 5 días
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params={
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric",
            "lang": "es"
        }
    )
    data = response.json()

    forecasts = []
    for item in data.get("list", [])[:10]:  # Primeras 10 entradas (~ 30h)
        forecasts.append(
            f"  {item['dt_txt']}: {item['main']['temp']}°C, "
            f"{item['weather'][0]['description']}, "
            f"lluvia: {item.get('rain', {}).get('3h', 0)}mm, "
            f"viento: {item['wind']['speed']}m/s"
        )

    return f"Previsión para {destination_name}:\n" + "\n".join(forecasts)
```

### 9.3 Climate Scorer Tool

```python
# tools/climate_scorer_tool.py
from strands import tool

@tool
def calculate_climate_score(
    avg_temp: float,
    rain_probability: float,
    sun_hours: float,
    wind_speed: float,
    theme: str
) -> str:
    """Calcula un score climático (0-100) para un destino según la temática.

    Args:
        avg_temp: Temperatura media en Celsius
        rain_probability: Probabilidad de lluvia (0-100)
        sun_hours: Horas de sol estimadas por día
        wind_speed: Velocidad del viento en m/s
        theme: Temática del viaje (playa, montaña, ciudad, rural)

    Returns:
        Score climático con desglose
    """
    score = 50  # Base

    if theme == "playa":
        # Temperatura: ideal 25-35
        if 25 <= avg_temp <= 35:
            score += 25
        elif 20 <= avg_temp < 25:
            score += 15
        else:
            score -= 10

        # Lluvia: penalizar mucho
        score -= rain_probability * 0.4

        # Sol
        score += min(sun_hours * 2, 15)

        # Viento: penalizar si > 20 km/h
        if wind_speed > 5.5:
            score -= 10

    elif theme == "montaña":
        if 10 <= avg_temp <= 25:
            score += 25
        elif 5 <= avg_temp < 10:
            score += 15

        score -= rain_probability * 0.25
        score += min(sun_hours * 1.5, 10)

    elif theme == "ciudad":
        if 15 <= avg_temp <= 30:
            score += 25
        score -= rain_probability * 0.3
        score += min(sun_hours * 1, 10)

    elif theme == "rural":
        if 15 <= avg_temp <= 28:
            score += 25
        score -= rain_probability * 0.3
        score += min(sun_hours * 1.5, 10)

    final_score = max(0, min(100, round(score)))

    return (
        f"Score climático: {final_score}/100 "
        f"(temp={avg_temp}°C, lluvia={rain_probability}%, "
        f"sol={sun_hours}h, viento={wind_speed}m/s, tema={theme})"
    )
```

### 9.4 Budget Calculator Tool

```python
# tools/budget_calculator_tool.py
from strands import tool

@tool
def calculate_budget(
    flight_price: float,
    hotel_per_night: float,
    num_nights: int,
    daily_expenses: float,
    num_travelers: int
) -> str:
    """Calcula el presupuesto total estimado del viaje.

    Args:
        flight_price: Precio del vuelo ida/vuelta por persona en EUR
        hotel_per_night: Precio del hotel por noche (habitación) en EUR
        num_nights: Número de noches
        daily_expenses: Gastos diarios estimados por persona en EUR
        num_travelers: Número de viajeros

    Returns:
        Desglose del presupuesto total
    """
    total_flights = flight_price * num_travelers
    total_hotel = hotel_per_night * num_nights
    total_daily = daily_expenses * num_nights * num_travelers
    total = total_flights + total_hotel + total_daily

    return (
        f"Presupuesto estimado:\n"
        f"  Vuelos: {total_flights:.0f}€ ({flight_price:.0f}€ x {num_travelers} personas)\n"
        f"  Hotel: {total_hotel:.0f}€ ({hotel_per_night:.0f}€ x {num_nights} noches)\n"
        f"  Gastos diarios: {total_daily:.0f}€ ({daily_expenses:.0f}€/día x {num_travelers} pers x {num_nights} días)\n"
        f"  TOTAL: {total:.0f}€"
    )
```

---

## 10. Base de datos local de destinos

```json
// config/destinations_db.json
{
  "playa": [
    {"name": "Santorini", "country": "Grecia", "lat": 36.39, "lon": 25.46, "best_months": [5,6,7,8,9]},
    {"name": "Cancún", "country": "México", "lat": 21.16, "lon": -86.85, "best_months": [11,12,1,2,3,4]},
    {"name": "Bali", "country": "Indonesia", "lat": -8.34, "lon": 115.09, "best_months": [4,5,6,7,8,9,10]},
    {"name": "Algarve", "country": "Portugal", "lat": 37.02, "lon": -7.93, "best_months": [5,6,7,8,9]},
    {"name": "Dubrovnik", "country": "Croacia", "lat": 42.65, "lon": 18.09, "best_months": [5,6,7,8,9]},
    {"name": "Cerdeña", "country": "Italia", "lat": 39.22, "lon": 9.12, "best_months": [5,6,7,8,9]},
    {"name": "Maldivas", "country": "Maldivas", "lat": 3.20, "lon": 73.22, "best_months": [11,12,1,2,3,4]},
    {"name": "Zanzibar", "country": "Tanzania", "lat": -6.16, "lon": 39.19, "best_months": [6,7,8,9,10]},
    {"name": "Costa Brava", "country": "España", "lat": 41.72, "lon": 2.93, "best_months": [6,7,8,9]},
    {"name": "Creta", "country": "Grecia", "lat": 35.24, "lon": 24.90, "best_months": [5,6,7,8,9,10]}
  ],
  "montaña": [
    {"name": "Chamonix", "country": "Francia", "lat": 45.92, "lon": 6.87, "best_months": [6,7,8,9,12,1,2,3]},
    {"name": "Dolomitas", "country": "Italia", "lat": 46.41, "lon": 11.84, "best_months": [6,7,8,9]},
    {"name": "Interlaken", "country": "Suiza", "lat": 46.68, "lon": 7.86, "best_months": [6,7,8,9]},
    {"name": "Pirineos", "country": "España/Francia", "lat": 42.65, "lon": 0.05, "best_months": [6,7,8,9,12,1,2,3]},
    {"name": "Picos de Europa", "country": "España", "lat": 43.17, "lon": -4.83, "best_months": [6,7,8,9]},
    {"name": "Innsbruck", "country": "Austria", "lat": 47.26, "lon": 11.39, "best_months": [6,7,8,9,12,1,2]},
    {"name": "Zermatt", "country": "Suiza", "lat": 46.02, "lon": 7.75, "best_months": [6,7,8,12,1,2,3]},
    {"name": "Banff", "country": "Canadá", "lat": 51.18, "lon": -115.57, "best_months": [6,7,8,9]}
  ],
  "ciudad": [
    {"name": "Lisboa", "country": "Portugal", "lat": 38.72, "lon": -9.14, "best_months": [3,4,5,6,9,10]},
    {"name": "Praga", "country": "Chequia", "lat": 50.08, "lon": 14.44, "best_months": [4,5,6,9,10]},
    {"name": "Roma", "country": "Italia", "lat": 41.90, "lon": 12.50, "best_months": [3,4,5,9,10,11]},
    {"name": "Estambul", "country": "Turquía", "lat": 41.01, "lon": 28.98, "best_months": [4,5,6,9,10]},
    {"name": "Ámsterdam", "country": "Países Bajos", "lat": 52.37, "lon": 4.90, "best_months": [4,5,6,7,8,9]},
    {"name": "Budapest", "country": "Hungría", "lat": 47.50, "lon": 19.04, "best_months": [4,5,6,9,10]},
    {"name": "Marrakech", "country": "Marruecos", "lat": 31.63, "lon": -8.01, "best_months": [3,4,5,10,11]},
    {"name": "Cracovia", "country": "Polonia", "lat": 50.06, "lon": 19.94, "best_months": [5,6,7,8,9]},
    {"name": "Tokio", "country": "Japón", "lat": 35.68, "lon": 139.69, "best_months": [3,4,5,10,11]},
    {"name": "Edimburgo", "country": "Escocia", "lat": 55.95, "lon": -3.19, "best_months": [5,6,7,8,9]}
  ],
  "rural": [
    {"name": "Toscana", "country": "Italia", "lat": 43.35, "lon": 11.02, "best_months": [4,5,6,9,10]},
    {"name": "Cotswolds", "country": "Inglaterra", "lat": 51.83, "lon": -1.68, "best_months": [5,6,7,8,9]},
    {"name": "Provenza", "country": "Francia", "lat": 43.95, "lon": 5.56, "best_months": [5,6,7,8,9]},
    {"name": "Selva Negra", "country": "Alemania", "lat": 48.00, "lon": 8.20, "best_months": [5,6,7,8,9]},
    {"name": "Alentejo", "country": "Portugal", "lat": 38.57, "lon": -7.91, "best_months": [3,4,5,9,10]},
    {"name": "Alpujarras", "country": "España", "lat": 36.95, "lon": -3.36, "best_months": [4,5,6,9,10]}
  ]
}
```

---

## 11. Flujo de ejecución detallado

```
USUARIO INTRODUCE:
  - Origen: Madrid
  - Fechas: 15/07/2026 → 22/07/2026 (7 noches)
  - Temática: Playa
  - Presupuesto: 1500€
  - Viajeros: 2

PASO 1 — Agente Destinos:
  Input: prompt + shared_state
  Acciones:
    1. Consulta destinations_db.json filtrando por "playa" y mes julio
    2. Búsqueda web: "mejores destinos playa julio 2026 desde Madrid"
    3. Genera lista de 6-8 candidatos con coordenadas
  Output: JSON con candidatos → pasa a Meteorólogo

PASO 2 — Agente Meteorólogo:
  Input: lista de candidatos + fechas
  Acciones:
    1. Para cada destino, llama a OpenWeatherMap con lat/lon
    2. Calcula climate_score para cada uno (temática=playa)
    3. Filtra los que tienen score < 40
    4. Ordena por score descendente
  Output: JSON con destinos filtrados y scored → pasa a Financiero

PASO 3 — Agente Financiero:
  Input: destinos filtrados + origen + fechas + presupuesto
  Acciones:
    1. Busca "vuelos Madrid a Santorini julio 2026" vía Serper/Tavily
    2. Busca "hotel Santorini julio 2026 precio" para cada destino
    3. Calcula presupuesto total con calculate_budget
    4. Filtra destinos que superan 1500€ para 2 personas
    5. Ordena por value_score (weather_score / precio)
  Output: JSON con destinos con precio → pasa a Planificador

PASO 4 — Agente Planificador:
  Input: top 1-2 destinos con toda la info
  Acciones:
    1. Busca "qué hacer en Santorini julio" vía Tavily
    2. Busca restaurantes y actividades vía Google Places (o Tavily)
    3. Genera itinerario día a día (7 días)
    4. Añade tips generales y planes alternativos por lluvia
  Output: JSON con itinerario completo → se muestra en Streamlit
```

---

## 12. Consideraciones para la demo

### Qué puede fallar y cómo manejar

1. **API rate limits:** Tavily free tier tiene 1000 req/mes. Usar caché en memoria para demos repetidas.
2. **Latencia:** Cada agente hace llamadas LLM + API. Pipeline completo puede tardar 30-60s. Implementar streaming de eventos para mostrar progreso.
3. **Weather API forecast limitado a 5 días:** Si las fechas del viaje son > 5 días en el futuro, usar datos históricos o climatológicos en vez de forecast.
4. **Precios de vuelos imprecisos:** Serper/Tavily no dan precios exactos de vuelos. Aclarar en la demo que son "estimaciones basadas en búsqueda web".
5. **Alucinaciones en itinerario:** El agente puede inventar restaurantes. Usar Google Places API para verificar que los lugares existen.

### Tips para una demo memorable

- Preparar 2-3 prompts de demo bien testeados (playa verano, montaña invierno, ciudad fin de semana).
- Tener un "fallback demo" grabado en vídeo por si algo falla en vivo.
- Mostrar el razonamiento visible: logear qué agente está actuando y qué tool usa.
- Si algo falla, explicar POR QUÉ y CÓMO lo arreglaríais (la rúbrica valora esto).

---

## 13. Extensiones opcionales (si da tiempo)

- **Memoria conversacional:** Que el usuario pueda refinar ("busca algo más barato", "prefiero playa menos turística") sin empezar de cero.
- **Mapa interactivo en Streamlit:** Usar `st.map()` o `folium` para mostrar los destinos candidatos sobre un mapa.
- **Export a PDF:** Generar un PDF con el itinerario completo para descargar.
- **Comparativa visual:** Tabla Streamlit con los top 3 destinos side-by-side (precio, clima, score).
- **Notificaciones de precio:** Guardar búsquedas en DynamoDB y notificar si bajan precios.

---

## 14. Referencias clave

- Strands Agents SDK docs: https://strandsagents.com/
- Strands Agents GitHub: https://github.com/strands-agents/sdk-python
- Strands tools: https://github.com/strands-agents/tools
- GraphBuilder pattern: https://strandsagents.com/docs/user-guide/concepts/multi-agent/graph/
- Swarm pattern: https://strandsagents.com/docs/user-guide/concepts/multi-agent/swarm/
- Tavily API: https://docs.tavily.com/
- OpenWeatherMap API: https://openweathermap.org/api
- Streamlit docs: https://docs.streamlit.io/
- AWS Bedrock model IDs: https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html
