from abc import ABC, abstractmethod

from ..entities import Agent
from ..value_objects import AgentId

class IAgentRepository(ABC):
    @abstractmethod
    async def create(self, project_name: str, agent: Agent) -> Agent:
        pass

    @abstractmethod
    async def find_by_id(self, project_name: str, agent_id: AgentId) -> Agent | None:
        pass

    @abstractmethod
    async def find_all(self, project_name: str) -> list[Agent]:
        pass

    @abstractmethod
    async def delete(self, project_name: str, agent_id: AgentId) -> None:
        pass
