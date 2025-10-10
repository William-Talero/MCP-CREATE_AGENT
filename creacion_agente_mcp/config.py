from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    azure_ai_endpoint: str
    azure_ai_api_version: str = "2025-05-01"

    azure_ai_api_key: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    use_managed_identity: bool = False

    def validate_auth(self) -> None:
        has_api_key = bool(self.azure_ai_api_key)
        has_service_principal = bool(
            self.azure_tenant_id and self.azure_client_id and self.azure_client_secret
        )

        if not has_api_key and not has_service_principal and not self.use_managed_identity:
            raise ValueError(
                "Authentication is required. Please configure one of:\n"
                "1. AZURE_AI_API_KEY for API Key authentication\n"
                "2. AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET for Service Principal\n"
                "3. USE_MANAGED_IDENTITY=true for Managed Identity (in Azure environments)"
            )

def get_settings() -> Settings:
    settings = Settings()  # type: ignore
    settings.validate_auth()
    return settings
