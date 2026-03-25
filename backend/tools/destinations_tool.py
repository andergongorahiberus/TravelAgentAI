from pydantic import BaseModel
from typing import List
from duckduckgo_search import DDGS
from strands import tool


class DestinoEncontrado(BaseModel):
    nombre_sitio: str
    resumen: str
    url: str


class RespuestaBusqueda(BaseModel):
    query: str
    resultados: List[DestinoEncontrado]


@tool
def search_destinations_online(query: str, max_results: int = 5) -> RespuestaBusqueda:
    """
    Busca en internet destinos y devuelve una estructura JSON con los resultados.
    """
    try:
        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=max_results))

        lista_destinos = []
        for res in search_results:
            destino = DestinoEncontrado(
                nombre_sitio=res.get("title", "N/A"),
                resumen=res.get("body", "N/A"),
                url=res.get("href", "N/A"),
            )
            lista_destinos.append(destino)

        return RespuestaBusqueda(query=query, resultados=lista_destinos)

    except Exception:
        return RespuestaBusqueda(query=query, resultados=[])
