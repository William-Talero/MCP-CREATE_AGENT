from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from ..value_objects import AgentId, AgentName, AgentDescription, ModelConfiguration

class AgentProps(BaseModel):
    id: Optional[AgentId] = None
    name: AgentName
    description: AgentDescription
    model_configuration: ModelConfiguration
    instructions: Optional[str] = None
    tools: Optional[list[str]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Agent:
    def __init__(self, props: AgentProps) -> None:
        self._id = props.id
        self._name = props.name
        self._description = props.description
        self._model_configuration = props.model_configuration
        self._instructions = props.instructions
        self._tools = props.tools or []
        self._metadata = props.metadata
        self._created_at = props.created_at
        self._updated_at = props.updated_at

    @property
    def id(self) -> Optional[AgentId]:
        return self._id

    @property
    def name(self) -> AgentName:
        return self._name

    @property
    def description(self) -> AgentDescription:
        return self._description

    @property
    def model_configuration(self) -> ModelConfiguration:
        return self._model_configuration

    @property
    def instructions(self) -> Optional[str]:
        return self._instructions

    @property
    def tools(self) -> list[str]:
        return self._tools

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self._id.value if self._id else None,
            "name": self._name.value,
            "description": self._description.value,
            "modelConfiguration": {
                "modelName": self._model_configuration.model_name,
                "provider": self._model_configuration.provider,
                "temperature": self._model_configuration.temperature,
                "maxTokens": self._model_configuration.max_tokens,
                "topP": self._model_configuration.top_p,
                "frequencyPenalty": self._model_configuration.frequency_penalty,
                "presencePenalty": self._model_configuration.presence_penalty,
            },
            "instructions": self._instructions,
            "tools": self._tools,
            "metadata": self._metadata,
            "createdAt": self._created_at.isoformat(),
            "updatedAt": self._updated_at.isoformat(),
        }
