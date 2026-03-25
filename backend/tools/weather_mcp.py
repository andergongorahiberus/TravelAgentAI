from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp import MCPClient


def create_open_meteo_mcp() -> MCPClient:
    """Create an MCPClient for the Open-Meteo MCP server.

    Uses stdio transport via npx to run the server as a subprocess.
    The MCPClient can be passed directly to Agent(tools=[...]) —
    Strands manages the lifecycle automatically.

    Returns:
        MCPClient instance ready to be passed to an Agent.
    """
    return MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="npx",
                args=["-y", "-p", "open-meteo-mcp-server", "open-meteo-mcp-server"],
            )
        )
    )
