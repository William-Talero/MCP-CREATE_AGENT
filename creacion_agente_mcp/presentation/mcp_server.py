import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import ValidationError
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route

from ..application.use_cases import (
    CreateAgentUseCase,
    CreateAgentDTO,
    GetAgentUseCase,
    ListAgentsUseCase,
)
from ..domain.value_objects import AIModel, AIModelProvider
from ..domain.exceptions import DomainException
from ..infrastructure.azure import AzureFoundryClient

class MCPServer:
    def __init__(
        self,
        create_agent_use_case: CreateAgentUseCase,
        get_agent_use_case: GetAgentUseCase,
        list_agents_use_case: ListAgentsUseCase,
        azure_client: AzureFoundryClient,
    ) -> None:
        self._create_agent_use_case = create_agent_use_case
        self._get_agent_use_case = get_agent_use_case
        self._list_agents_use_case = list_agents_use_case
        self._azure_client = azure_client
        self._server = Server("creacion-agente-mcp")

        self._server.list_tools()(self._list_tools)
        self._server.call_tool()(self._call_tool)

    async def _list_tools(self) -> list[Tool]:
        return [
            Tool(
                name="create_agent",
                description="Crea un nuevo agente en Azure AI Foundry con la configuración especificada",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Nombre del proyecto de Azure AI Foundry",
                        },
                        "name": {
                            "type": "string",
                            "description": "Nombre del agente (1-100 caracteres)",
                        },
                        "modelName": {
                            "type": "string",
                            "description": "Nombre del modelo. Ejemplos: gpt-4o, gpt-4, claude-3-5-sonnet, llama-3.1-405b, mistral-large, gemini-1.5-pro. Use list_models para ver todos los modelos disponibles.",
                        },
                        "provider": {
                            "type": "string",
                            "description": "Proveedor del modelo (azure_openai, anthropic, meta, mistral, cohere, google). Opcional, se detecta automáticamente del nombre del modelo.",
                            "enum": [
                                "azure_openai",
                                "anthropic",
                                "meta",
                                "mistral",
                                "cohere",
                                "google",
                            ],
                        },
                        "temperature": {
                            "type": "number",
                            "description": "Temperatura del modelo (0-2, default: 0.7)",
                        },
                        "maxTokens": {
                            "type": "number",
                            "description": "Máximo de tokens (1-1000000, default: automático)",
                        },
                        "topP": {
                            "type": "number",
                            "description": "Top P sampling (0-1, default: 1.0)",
                        },
                        "frequencyPenalty": {
                            "type": "number",
                            "description": "Penalización de frecuencia (-2 a 2, default: 0)",
                        },
                        "presencePenalty": {
                            "type": "number",
                            "description": "Penalización de presencia (-2 a 2, default: 0)",
                        },
                        "instructions": {
                            "type": "string",
                            "description": "Instrucciones del sistema para el agente (max 10000 caracteres)",
                        },
                        "tools": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de herramientas disponibles para el agente (max 50)",
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Metadatos adicionales para el agente",
                        },
                    },
                    "required": ["projectName", "name", "modelName"],
                },
            ),
            Tool(
                name="get_agent",
                description="Obtiene la información de un agente específico por su ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Nombre del proyecto de Azure AI Foundry",
                        },
                        "agentId": {
                            "type": "string",
                            "description": "ID del agente a consultar",
                        },
                    },
                    "required": ["projectName", "agentId"],
                },
            ),
            Tool(
                name="list_agents",
                description="Lista todos los agentes creados en Azure Foundry",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Nombre del proyecto de Azure AI Foundry",
                        },
                    },
                    "required": ["projectName"],
                },
            ),
            Tool(
                name="list_models",
                description="Lista todos los modelos de AI disponibles en Azure AI Foundry con sus características",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "provider": {
                            "type": "string",
                            "description": "Filtrar por proveedor específico (opcional)",
                            "enum": [
                                "azure_openai",
                                "anthropic",
                                "meta",
                                "mistral",
                                "cohere",
                                "google",
                            ],
                        },
                    },
                },
            ),
            Tool(
                name="list_projects",
                description="Lista todos los proyectos disponibles en Azure AI Foundry",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]

    async def _call_tool(self, name: str, arguments: Any) -> list[TextContent]:
        try:
            if name == "create_agent":
                return await self._handle_create_agent(arguments)
            elif name == "get_agent":
                return await self._handle_get_agent(arguments)
            elif name == "list_agents":
                return await self._handle_list_agents(arguments)
            elif name == "list_models":
                return await self._handle_list_models(arguments)
            elif name == "list_projects":
                return await self._handle_list_projects(arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

        except ValidationError as e:
            errors = ", ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
            return [TextContent(type="text", text=f"Validation error: {errors}")]
        except DomainException as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_create_agent(self, arguments: dict[str, Any]) -> list[TextContent]:
        dto_data = {
            "project_name": arguments.get("projectName"),
            "name": arguments.get("name"),
            "model_name": arguments.get("modelName"),
            "provider": arguments.get("provider"),
            "temperature": arguments.get("temperature"),
            "max_tokens": arguments.get("maxTokens"),
            "top_p": arguments.get("topP"),
            "frequency_penalty": arguments.get("frequencyPenalty"),
            "presence_penalty": arguments.get("presencePenalty"),
            "instructions": arguments.get("instructions"),
            "tools": arguments.get("tools"),
            "metadata": arguments.get("metadata", {}),
        }

        dto_data = {k: v for k, v in dto_data.items() if v is not None}

        dto = CreateAgentDTO(**dto_data)
        agent = await self._create_agent_use_case.execute(dto)

        return [TextContent(type="text", text=json.dumps(agent.to_dict(), indent=2))]

    async def _handle_get_agent(self, arguments: dict[str, Any]) -> list[TextContent]:
        project_name = arguments.get("projectName")
        agent_id = arguments.get("agentId")

        if not project_name or not agent_id:
            raise ValueError("projectName and agentId are required")

        agent = await self._get_agent_use_case.execute(project_name, agent_id)

        return [TextContent(type="text", text=json.dumps(agent.to_dict(), indent=2))]

    async def _handle_list_agents(self, arguments: dict[str, Any]) -> list[TextContent]:
        project_name = arguments.get("projectName")

        if not project_name:
            raise ValueError("projectName is required")

        agents = await self._list_agents_use_case.execute(project_name)
        agents_dict = [agent.to_dict() for agent in agents]

        return [TextContent(type="text", text=json.dumps(agents_dict, indent=2))]

    async def _handle_list_models(self, arguments: dict[str, Any]) -> list[TextContent]:
        provider_str = arguments.get("provider")

        if provider_str:
            provider = AIModelProvider(provider_str)
            models = AIModel.get_models_by_provider(provider)
        else:
            models = AIModel.get_all_models()

        result = {
            "total": len(models),
            "models": [
                {
                    "model": model_name,
                    "displayName": info.display_name,
                    "provider": info.provider.value,
                    "description": info.description,
                    "maxTokens": info.max_tokens,
                    "supportsTools": info.supports_tools,
                    "supportsVision": info.supports_vision,
                }
                for model_name, info in models.items()
            ],
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def _handle_list_projects(self, arguments: dict[str, Any]) -> list[TextContent]:
        projects = await self._azure_client.list_projects()

        result = {
            "total": len(projects),
            "projects": [
                {
                    "name": project.name,
                    "displayName": project.display_name,
                    "description": project.description,
                    "location": project.location,
                    "resourceGroup": project.resource_group,
                }
                for project in projects
            ],
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async def run_stdio(self) -> None:
        async with stdio_server() as (read_stream, write_stream):
            await self._server.run(read_stream, write_stream, self._server.create_initialization_options())

    async def run_sse(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        from mcp.server.sse import SseServerTransport

        sse = SseServerTransport("/messages")

        async def handle_sse(request):
            async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
                await self._server.run(read_stream, write_stream, self._server.create_initialization_options())

        async def handle_messages(request):
            await sse.handle_post_message(request.scope, request.receive, request._send)

        app = Starlette(
            routes=[
                Route("/sse", endpoint=handle_sse),
                Route("/messages", endpoint=handle_messages, methods=["POST"]),
            ]
        )

        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
