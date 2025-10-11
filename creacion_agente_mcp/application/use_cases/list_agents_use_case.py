from ...domain.entities import Agent
from ...domain.repositories import IAgentRepository

class ListAgentsUseCase:
    def __init__(self, agent_repository: IAgentRepository) -> None:
        self._agent_repository = agent_repository

    async def execute(self, project_name: str) -> list[Agent]:
        return await self._agent_repository.find_all(project_name)
