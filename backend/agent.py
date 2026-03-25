# Entry point para AgentCore Runtime
import json
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from agents.orchestrator import create_travel_graph
from tools.config.destinations_schema import UserTravelQuery

# Crear la app AgentCore
app = BedrockAgentCoreApp()

# Crear el grafo de agentes (se instancia una vez por microVM)
travel_graph = create_travel_graph()


@app.entrypoint
def invoke(payload):
    """Entry point que AgentCore Runtime invoca por cada petición.

    El payload viene del frontend (Streamlit) vía InvokeAgentRuntime.
    Contiene el prompt del usuario y el shared_state con parámetros del viaje.
    """
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

    # Ejecutar el grafo completo
    result = travel_graph(user_prompt, invocation_state=clean_state)

    return {
        "result": str(result.message) if hasattr(result, "message") else str(result),
        "status": "success",
    }


# Para desarrollo local: ejecuta como servidor HTTP en localhost:8080
if __name__ == "__main__":
    app.run()
