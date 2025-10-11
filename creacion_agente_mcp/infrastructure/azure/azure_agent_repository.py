from datetime import datetime
from typing import Any

from ...domain.entities import Agent, AgentProps
from ...domain.value_objects import (
    AgentId,
    AgentName,
    AgentDescription,
    ModelConfiguration,
)
from ...domain.repositories import IAgentRepository
from .azure_foundry_client import AzureFoundryClient, AzureAgentRequest

class AzureAgentRepository(IAgentRepository):
    def __init__(self, azure_client: AzureFoundryClient) -> None:
        self._azure_client = azure_client

    async def create(self, project_name: str, agent: Agent) -> Agent:
        # Build tools array
        tools = None
        if agent.tools:
            tools = [{"type": "function", "function": {"name": tool}} for tool in agent.tools]

        # Build request
        request = AzureAgentRequest(
            model=agent.model_configuration.model_name,
            name=agent.name.value,
            instructions=agent.instructions,
            tools=tools,
            metadata={
                **agent.metadata,
                "description": agent.description.value,
                "temperature": agent.model_configuration.temperature,
                "maxTokens": agent.model_configuration.max_tokens,
                "topP": agent.model_configuration.top_p,
                "frequencyPenalty": agent.model_configuration.frequency_penalty,
                "presencePenalty": agent.model_configuration.presence_penalty,
            },
        )

        # Create agent
        response = await self._azure_client.create_agent(project_name, request)

        # Map response to Agent
        return self._map_response_to_agent(response)

    async def find_by_id(self, project_name: str, agent_id: AgentId) -> Agent | None:
        response = await self._azure_client.get_agent(project_name, agent_id.value)

        if not response:
            return None

        return self._map_response_to_agent(response)

    async def find_all(self, project_name: str) -> list[Agent]:
        responses = await self._azure_client.list_agents(project_name)
        return [self._map_response_to_agent(response) for response in responses]

    async def delete(self, project_name: str, agent_id: AgentId) -> None:
        await self._azure_client.delete_agent(project_name, agent_id.value)

    def _map_response_to_agent(self, response: Any) -> Agent:
        metadata = response.metadata or {}

        # Extract tools
        tools = []
        if response.tools:
            tools = [
                tool.get("function", {}).get("name", "unknown")
                for tool in response.tools
                if isinstance(tool, dict)
            ]

        # Build model configuration
        model_config = ModelConfiguration(
            model_name=response.model,
            temperature=metadata.get("temperature", 0.7),
            max_tokens=metadata.get("maxTokens"),
            top_p=metadata.get("topP", 1.0),
            frequency_penalty=metadata.get("frequencyPenalty", 0.0),
            presence_penalty=metadata.get("presencePenalty", 0.0),
        )

        # Build agent props
        agent_props = AgentProps(
            id=AgentId(value=response.id),
            name=AgentName(value=response.name),
            description=AgentDescription(
                value=metadata.get("description", response.instructions or "Azure AI Foundry Agent")
            ),
            model_configuration=model_config,
            instructions=response.instructions,
            tools=tools,
            metadata=response.metadata,
            created_at=datetime.fromtimestamp(response.created_at)
            if response.created_at
            else datetime.now(),
            updated_at=datetime.fromtimestamp(response.created_at)
            if response.created_at
            else datetime.now(),
        )

        return Agent(agent_props)
