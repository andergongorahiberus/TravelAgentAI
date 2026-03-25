from strands import tool
from .config.destinations_schema import RespuestaBusqueda, DestinoEncontrado


@tool
def search_destinations_online(
    query: str, origin: str, theme: str
) -> RespuestaBusqueda:
    """MOCK: Busca destinos teniendo en cuenta el origen y la temática."""

    mock_data = [
        DestinoEncontrado(
            nombre_sitio=f"Aventura desde {origin}: Marruecos",
            resumen=f"Perfecto para temática {theme} con vuelos directos.",
            url="https://mock-travel.com/atlas",
        ),
        DestinoEncontrado(
            nombre_sitio=f"Aventura desde {origin}: Azores",
            resumen=f"Naturaleza salvaje ideal para {theme}.",
            url="https://mock-travel.com/azores",
        ),
    ]

    return RespuestaBusqueda(
        query=query, origin=origin, theme=theme, resultados=mock_data
    )
