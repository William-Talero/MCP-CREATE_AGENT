import asyncio
import sys
import os

from .config import get_settings
from .infrastructure.azure import AzureFoundryClient, AzureFoundryConfig, AzureAgentRepository
from .application.use_cases import CreateAgentUseCase, GetAgentUseCase, ListAgentsUseCase
from .presentation.mcp_server import MCPServer

async def main() -> None:
    try:
        settings = get_settings()

        config = AzureFoundryConfig(
            endpoint=settings.azure_ai_endpoint,
            api_version=settings.azure_ai_api_version,
            api_key=settings.azure_ai_api_key,
            tenant_id=settings.azure_tenant_id,
            client_id=settings.azure_client_id,
            client_secret=settings.azure_client_secret,
            use_managed_identity=settings.use_managed_identity,
        )

        azure_client = AzureFoundryClient(config)
        agent_repository = AzureAgentRepository(azure_client)

        create_agent_use_case = CreateAgentUseCase(agent_repository)
        get_agent_use_case = GetAgentUseCase(agent_repository)
        list_agents_use_case = ListAgentsUseCase(agent_repository)

        mcp_server = MCPServer(
            create_agent_use_case=create_agent_use_case,
            get_agent_use_case=get_agent_use_case,
            list_agents_use_case=list_agents_use_case,
            azure_client=azure_client,
        )

        transport = os.getenv("MCP_TRANSPORT", "stdio")

        if transport == "sse":
            host = os.getenv("MCP_HOST", "0.0.0.0")
            port = int(os.getenv("MCP_PORT", "8000"))
            print(f"Starting MCP server on http://{host}:{port} (SSE)", file=sys.stderr)
            await mcp_server.run_sse(host, port)
        else:
            print("Starting MCP server on stdio", file=sys.stderr)
            await mcp_server.run_stdio()

    except Exception as e:
        print(f"Failed to start server: {e}", file=sys.stderr)
        sys.exit(1)

def run() -> None:
    asyncio.run(main())

if __name__ == "__main__":
    run()
