from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .ai_model import AIModelProvider, AIModel

class ModelConfiguration(BaseModel):
    model_name: str = Field(..., min_length=1)
    provider: Optional[AIModelProvider] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=1000000)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Model name cannot be empty")
        return v.strip()

    @field_validator("provider", mode="before")
    @classmethod
    def auto_detect_provider(cls, v: Optional[AIModelProvider], info: dict) -> AIModelProvider:
        if v is not None:
            return v

        model_name = info.data.get("model_name")
        if not model_name:
            raise ValueError("Model name is required")

        detected_provider = AIModel.detect_provider(model_name)
        if detected_provider:
            return detected_provider

        # Default to Azure OpenAI if cannot detect
        return AIModelProvider.AZURE_OPENAI

    def __str__(self) -> str:
        return f"{self.model_name} ({self.provider})"
