#!/usr/bin/env python3
"""
Script de prueba para crear el agente AGENTE_WARP
"""
import asyncio
import json
from creacion_agente_mcp.config import get_settings
from creacion_agente_mcp.infrastructure.azure import AzureFoundryClient, AzureFoundryConfig, AzureAgentRepository
from creacion_agente_mcp.application.use_cases import CreateAgentUseCase, CreateAgentDTO

async def main():
    # Obtener configuración
    settings = get_settings()

    # Crear configuración para Azure Foundry
    # Forzar la versión correcta de la API
    api_version = "2025-05-01" if settings.azure_ai_api_version == "v1" else settings.azure_ai_api_version

    config = AzureFoundryConfig(
        endpoint=settings.azure_ai_endpoint,
        api_version=api_version,
        api_key=settings.azure_ai_api_key,
        tenant_id=settings.azure_tenant_id,
        client_id=settings.azure_client_id,
        client_secret=settings.azure_client_secret,
        use_managed_identity=settings.use_managed_identity,
    )
    
    print("🔧 Configuración cargada:")
    print(f"  Endpoint: {config.endpoint}")
    print(f"  API Version: {config.api_version}")
    print(f"  Tenant ID: {config.tenant_id}")
    print(f"  Client ID: {config.client_id}")
    print(f"  Use Managed Identity: {config.use_managed_identity}")

    # Inicializar cliente Azure
    azure_client = AzureFoundryClient(config)

    # Usar un nombre de proyecto predefinido (puedes cambiarlo)
    project_name = "AGENTES_MCP"
    print(f"\n📌 Usando proyecto: {project_name}")

    # Opcional: comentar si quieres listar proyectos
    # print("🔍 Buscando proyectos disponibles...")
    # try:
    #     projects = await azure_client.list_projects()
    #     if projects:
    #         print(f"\n✅ Proyectos disponibles ({len(projects)}):")
    #         for i, project in enumerate(projects, 1):
    #             print(f"  {i}. {project.name} ({project.display_name})")
    # except Exception as e:
    #     print(f"⚠️  No se pudieron listar proyectos: {e}")

    # Crear repositorio y caso de uso
    agent_repository = AzureAgentRepository(azure_client)
    create_agent_use_case = CreateAgentUseCase(agent_repository)

    # Datos para crear el agente AGENTE_WARP
    agent_data = CreateAgentDTO(
        project_name=project_name,
        name="AGENTE_WARP_6",
        model_name="gpt-4o",
        provider="azure_openai",
        temperature=0.7,
        max_tokens=4096,
        top_p=1.0,
        frequency_penalty=0,
        presence_penalty=0,
        instructions="Eres AGENTE_WARP, un asistente de IA avanzado diseñado para ayudar con tareas de desarrollo y análisis. Tu objetivo es proporcionar respuestas precisas, útiles y bien estructuradas.",
        tools=["code_interpreter"],
        metadata={
            "created_by": "test_script",
            "version": "1.0",
            "purpose": "testing",
        }
    )

    print("\n📤 Datos enviados para crear el agente:")
    print("=" * 60)
    print(json.dumps({
        "projectName": agent_data.project_name,
        "name": agent_data.name,
        "modelName": agent_data.model_name,
        "provider": agent_data.provider,
        "temperature": agent_data.temperature,
        "maxTokens": agent_data.max_tokens,
        "topP": agent_data.top_p,
        "frequencyPenalty": agent_data.frequency_penalty,
        "presencePenalty": agent_data.presence_penalty,
        "instructions": agent_data.instructions,
        "tools": agent_data.tools,
        "metadata": agent_data.metadata,
    }, indent=2))
    print("=" * 60)

    # Crear el agente
    print("\n🚀 Creando agente AGENTE_WARP...")
    try:
        agent = await create_agent_use_case.execute(agent_data)

        print("\n✅ ¡Agente creado exitosamente!")
        print("\n📊 Información del agente creado:")
        print("=" * 60)
        print(json.dumps(agent.to_dict(), indent=2))
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error al crear el agente: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
