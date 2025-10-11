from datetime import datetime
from typing import Any, Optional

import httpx
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from pydantic import BaseModel, Field, field_validator

class AzureFoundryConfig(BaseModel):
    endpoint: str = Field(..., min_length=1)
    api_version: str = Field(default="2025-05-01")

    # Auth Option 1: API Key
    api_key: Optional[str] = None

    # Auth Option 2: Service Principal
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    # Auth Option 3: Managed Identity
    use_managed_identity: bool = False

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Endpoint cannot be empty")
        v = v.strip()
        if not v.startswith("https://"):
            raise ValueError("Endpoint must start with https://")
        return v.rstrip("/")

    def validate_auth(self) -> None:
        has_api_key = bool(self.api_key)
        has_service_principal = bool(self.tenant_id and self.client_id and self.client_secret)

        if not has_api_key and not has_service_principal and not self.use_managed_identity:
            raise ValueError(
                "At least one authentication method must be configured: "
                "API Key, Service Principal, or Managed Identity"
            )

class AzureAgentRequest(BaseModel):
    model: str
    name: str
    instructions: Optional[str] = None
    tools: Optional[list[dict[str, Any]]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class AzureAgentResponse(BaseModel):
    id: str
    name: str
    model: str
    instructions: Optional[str] = None
    tools: Optional[list[dict[str, Any]]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: int
    object: str = "assistant"

class AzureProjectResponse(BaseModel):
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    resource_group: Optional[str] = None

class AzureFoundryClient:
    def __init__(self, config: AzureFoundryConfig) -> None:
        config.validate_auth()
        self._config = config
        self._credential: Optional[DefaultAzureCredential | ClientSecretCredential] = None

        # Initialize credential based on auth method
        if config.use_managed_identity:
            self._credential = DefaultAzureCredential()
        elif config.tenant_id and config.client_id and config.client_secret:
            self._credential = ClientSecretCredential(
                tenant_id=config.tenant_id,
                client_id=config.client_id,
                client_secret=config.client_secret,
            )

    async def _get_auth_headers(self) -> dict[str, str]:
        if self._config.api_key:
            return {"api-key": self._config.api_key}
        elif self._credential:
            token = self._credential.get_token("https://ai.azure.com/.default")
            return {"Authorization": f"Bearer {token.token}"}
        else:
            raise ValueError("No authentication method configured")

    def _build_project_url(self, project_name: str, path: str) -> str:
        return (
            f"{self._config.endpoint}/api/projects/{project_name}{path}"
            f"?api-version={self._config.api_version}"
        )

    async def create_agent(
        self, project_name: str, request: AzureAgentRequest
    ) -> AzureAgentResponse:
        url = self._build_project_url(project_name, "/assistants")
        headers = await self._get_auth_headers()
        headers["Content-Type"] = "application/json"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, json=request.model_dump(exclude_none=True), headers=headers, timeout=30.0
            )
            response.raise_for_status()
            return AzureAgentResponse(**response.json())

    async def get_agent(self, project_name: str, agent_id: str) -> AzureAgentResponse | None:
        url = self._build_project_url(project_name, f"/assistants/{agent_id}")
        headers = await self._get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return AzureAgentResponse(**response.json())

    async def list_agents(self, project_name: str) -> list[AzureAgentResponse]:
        url = self._build_project_url(project_name, "/assistants")
        headers = await self._get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            agents = data.get("data", [])
            return [AzureAgentResponse(**agent) for agent in agents]

    async def delete_agent(self, project_name: str, agent_id: str) -> None:
        url = self._build_project_url(project_name, f"/assistants/{agent_id}")
        headers = await self._get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers, timeout=30.0)
            response.raise_for_status()

    async def list_projects(self) -> list[AzureProjectResponse]:
        url = f"{self._config.endpoint}/api/projects?api-version={self._config.api_version}"
        headers = await self._get_auth_headers()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            projects = data.get("value", [])
            return [AzureProjectResponse(**project) for project in projects]
