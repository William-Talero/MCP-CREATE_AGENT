from typing import Any, Optional

from pydantic import BaseModel, Field

from ...domain.entities import Agent, AgentProps
from ...domain.value_objects import AgentName, AgentDescription, ModelConfiguration
from ...domain.repositories import IAgentRepository
from ...domain.exceptions import AgentCreationException

class CreateAgentDTO(BaseModel):
    project_name: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    model_name: str = Field(..., min_length=1)
    provider: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=1000000)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    frequency_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    instructions: Optional[str] = Field(default=None, max_length=10000)
    tools: Optional[list[str]] = Field(default=None, max_length=50)
    metadata: dict[str, Any] = Field(default_factory=dict)

class CreateAgentUseCase:
    def __init__(self, agent_repository: IAgentRepository) -> None:
        self._agent_repository = agent_repository

    async def execute(self, dto: CreateAgentDTO) -> Agent:
        try:
            # Build model configuration
            model_config_dict = {"model_name": dto.model_name}
            if dto.provider:
                model_config_dict["provider"] = dto.provider
            if dto.temperature is not None:
                model_config_dict["temperature"] = dto.temperature
            if dto.max_tokens is not None:
                model_config_dict["max_tokens"] = dto.max_tokens
            if dto.top_p is not None:
                model_config_dict["top_p"] = dto.top_p
            if dto.frequency_penalty is not None:
                model_config_dict["frequency_penalty"] = dto.frequency_penalty
            if dto.presence_penalty is not None:
                model_config_dict["presence_penalty"] = dto.presence_penalty

            # Create agent props
            agent_props = AgentProps(
                name=AgentName(value=dto.name),
                description=AgentDescription(
                    value=dto.instructions or f"Agent using {dto.model_name}"
                ),
                model_configuration=ModelConfiguration(**model_config_dict),
                instructions=dto.instructions,
                tools=dto.tools,
                metadata={**dto.metadata, "project_name": dto.project_name},
            )

            # Create and save agent
            agent = Agent(agent_props)
            created_agent = await self._agent_repository.create(dto.project_name, agent)

            return created_agent

        except Exception as e:
            raise AgentCreationException(str(e)) from e
