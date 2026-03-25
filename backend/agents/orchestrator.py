from strands.multiagent import GraphBuilder
from agents.destinations_agent import create_destinations_agent
from agents.weather_agent import create_weather_agent
from agents.financial_agent import create_financial_agent
from agents.planner_agent import create_planner_agent


def create_travel_graph():
    """Grafo secuencial: Destinos → Meteo → Financiero → Planificador."""
    destinations = create_destinations_agent()
    weather = create_weather_agent()
    financial = create_financial_agent()
    planner = create_planner_agent()

    builder = GraphBuilder()
    builder.add_node(destinations, "destinations")
    builder.add_node(weather, "weather")
    builder.add_node(financial, "financial")
    builder.add_node(planner, "planner")

    builder.add_edge("destinations", "weather")
    builder.add_edge("weather", "financial")
    builder.add_edge("financial", "planner")

    builder.set_entry_point("destinations")
    return builder.build()
