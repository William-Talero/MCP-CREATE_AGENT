from pydantic import BaseModel, Field, field_validator

class AgentName(BaseModel):
    value: str = Field(..., min_length=1, max_length=100)

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Agent name cannot be empty")
        if len(v.strip()) > 100:
            raise ValueError("Agent name cannot exceed 100 characters")
        return v.strip()

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AgentName):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
