
class DomainException(Exception):
    pass

class AgentNotFoundException(DomainException):
    def __init__(self, agent_id: str) -> None:
        super().__init__(f"Agent with ID '{agent_id}' not found")
        self.agent_id = agent_id

class AgentCreationException(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(f"Failed to create agent: {message}")

class ValidationException(DomainException):
    def __init__(self, message: str) -> None:
        super().__init__(f"Validation error: {message}")
