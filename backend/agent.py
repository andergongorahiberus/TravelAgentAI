# Entry point para AgentCore Runtime
import json
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from agents.orchestrator import create_travel_graph
from tools.config.destinations_schema import UserTravelQuery

# Crear la app AgentCore
app = BedrockAgentCoreApp()

# Crear el grafo de agentes (se instancia una vez por microVM)
travel_graph = create_travel_graph()

# Nombres del structured_output_model por nodo (mismo orden de prioridad que el frontend)
_STRUCTURED_TOOL_NAMES = {
    "planner": "TravelReport",
    "financial": "FinancialAgentResponse",
    "weather": "ListaWeather",
    "destinations": "ListaDestinos",
}


def _extract_final_text(graph_result) -> str:
    """Extrae el JSON del toolUse del structured_output_model del último nodo completado."""
    for node_name, tool_name in _STRUCTURED_TOOL_NAMES.items():
        node = getattr(graph_result, "results", {}).get(node_name)
        if node is None:
            continue
        message = getattr(getattr(node, "result", None), "message", None)
        if not isinstance(message, dict):
            continue
        content = message.get("content", [])

        # 1. Busca el toolUse del schema estructurado
        for block in content:
            if (isinstance(block, dict)
                    and "toolUse" in block
                    and block["toolUse"].get("name") == tool_name):
                return json.dumps(block["toolUse"].get("input", {}))

        # 2. Fallback: último bloque de texto no vacío
        for block in reversed(content):
            if isinstance(block, dict) and "text" in block:
                text = block["text"].strip()
                if text:
                    return text

    return str(graph_result)


@app.entrypoint
def invoke(payload):
    """Entry point que AgentCore Runtime invoca por cada petición."""
    user_prompt = payload.get("prompt", "")
    shared_state = payload.get("state", {})

    try:
        validated_data = UserTravelQuery(**shared_state)
        clean_state = validated_data.model_dump()
    except Exception as e:
        return {
            "result": f"Error de validación: {str(e)}",
            "status": "error_schema_validation",
        }

    result = travel_graph(user_prompt, invocation_state=clean_state)

    return {
        "result": _extract_final_text(result),
        "status": "success",
    }


# Para desarrollo local: ejecuta como servidor HTTP en localhost:8080
if __name__ == "__main__":
    app.run()
