from ...domain.entities import Agent
from ...domain.value_objects import AgentId
from ...domain.repositories import IAgentRepository
from ...domain.exceptions import AgentNotFoundException

class GetAgentUseCase:
    def __init__(self, agent_repository: IAgentRepository) -> None:
        self._agent_repository = agent_repository

    async def execute(self, project_name: str, agent_id: str) -> Agent:
        id_vo = AgentId(value=agent_id)
        agent = await self._agent_repository.find_by_id(project_name, id_vo)

        if not agent:
            raise AgentNotFoundException(agent_id)

        return agent
