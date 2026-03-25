from strands import tool
from .config.destinations_schema import RespuestaBusqueda, DestinoEncontrado


@tool
def search_destinations_online(query: str, max_results: int = 5) -> RespuestaBusqueda:
    """MOCK: Simula una búsqueda en internet de destinos de aventura."""

    mock_data = [
        DestinoEncontrado(
            nombre_sitio="Senderismo en las Azores, Portugal",
            resumen="Octubre es ideal para visitar las Azores. Rutas volcánicas, lagos verdes y avistamiento de ballenas. Vuelos baratos desde Madrid con SATA o TAP.",
            url="https://viajes-aventura.com/azores-octubre",
        ),
        DestinoEncontrado(
            nombre_sitio="Escalada y Trekking en el Atlas, Marruecos",
            resumen="A solo 2 horas de Madrid. El clima en octubre es perfecto para subir al Toubkal sin el calor extremo del verano. Muy económico.",
            url="https://aventura-marrakech.ma/atlas",
        ),
        DestinoEncontrado(
            nombre_sitio="Ruta de los Volcanes en Islandia",
            resumen="Para presupuestos medios-altos (1500€ es justo pero posible). Octubre permite ver Auroras Boreales y hacer trekking por glaciares.",
            url="https://iceland-travel.is/adventure",
        ),
        DestinoEncontrado(
            nombre_sitio="Selva Negra, Alemania",
            resumen="Bosques infinitos para BTT y senderismo. Muy accesible desde Madrid volando a Basilea. Paisajes otoñales espectaculares en octubre.",
            url="https://blackforest-tourism.de",
        ),
    ]

    return RespuestaBusqueda(query=query, resultados=mock_data)
