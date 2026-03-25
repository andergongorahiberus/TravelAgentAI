FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    AWS_REGION=eu-west-1 \
    AWS_DEFAULT_REGION=eu-west-1 \
    BEDROCK_MODEL_ID=eu.amazon.nova-lite-v1:0

# Node.js necesario para npx (Open-Meteo MCP server)
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt requirements.txt
RUN uv pip install -r requirements.txt

RUN uv pip install aws-opentelemetry-distro==0.12.2

# Usuario no-root (requerido por AgentCore)
RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore

EXPOSE 8080

# Copia solo backend/ → los imports absolutos funcionan desde /app
COPY backend/ .

CMD ["opentelemetry-instrument", "python", "agent.py"]
