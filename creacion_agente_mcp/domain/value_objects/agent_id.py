from pydantic import BaseModel, Field, field_validator

class AgentId(BaseModel):
    value: str = Field(..., min_length=1)

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Agent ID cannot be empty")
        return v.strip()

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AgentId):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
