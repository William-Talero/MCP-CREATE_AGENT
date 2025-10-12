#!/usr/bin/env python3
"""
Cliente MCP para crear el agente AGENTE_WARP
"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Configurar el servidor MCP
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "creacion_agente_mcp.main"],
        env={}  # Las variables de entorno se cargan desde .env
    )

    print("🔌 Conectando al servidor MCP...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Inicializar la sesión
            await session.initialize()
            print("✅ Conectado al servidor MCP\n")

            # Listar herramientas disponibles
            print("📋 Herramientas disponibles:")
            tools_result = await session.list_tools()
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")
            print()

            # Primero, listar proyectos disponibles
            print("🔍 Listando proyectos disponibles...")
            try:
                list_projects_result = await session.call_tool("list_projects", arguments={})
                projects_data = json.loads(list_projects_result.content[0].text)
                print(f"✅ Proyectos encontrados: {projects_data['total']}")
                for project in projects_data['projects']:
                    print(f"  - {project['name']} ({project['displayName']})")
                print()
            except Exception as e:
                print(f"⚠️  Error listando proyectos: {e}\n")

            # Crear el agente AGENTE_WARP en el proyecto AGENTES_MCP
            print("🚀 Creando agente AGENTE_WARP en proyecto AGENTES_MCP...")

            agent_data = {
                "projectName": "AGENTES_MCP",
                "name": "AGENTE_WARP",
                "modelName": "gpt-4o",
                "provider": "azure_openai",
                "temperature": 0.7,
                "maxTokens": 4096,
                "topP": 1.0,
                "frequencyPenalty": 0.0,
                "presencePenalty": 0.0,
                "instructions": "Eres AGENTE_WARP, un asistente de IA avanzado diseñado para ayudar con tareas de desarrollo y análisis. Tu objetivo es proporcionar respuestas precisas, útiles y bien estructuradas.",
                "tools": ["code_interpreter"],
                "metadata": {
                    "created_by": "mcp_client",
                    "version": "1.0",
                    "purpose": "production"
                }
            }

            print("\n📤 Datos enviados:")
            print("=" * 70)
            print(json.dumps(agent_data, indent=2))
            print("=" * 70)
            print()

            try:
                result = await session.call_tool("create_agent", arguments=agent_data)

                print("✅ ¡Agente creado exitosamente!\n")
                print("📊 Respuesta del servidor:")
                print("=" * 70)
                print(result.content[0].text)
                print("=" * 70)
                print()

                # Parsear y mostrar información clave
                agent_info = json.loads(result.content[0].text)
                print("\n🎯 Información del agente creado:")
                print(f"  • ID: {agent_info.get('id', 'N/A')}")
                print(f"  • Nombre: {agent_info.get('name', 'N/A')}")
                print(f"  • Modelo: {agent_info.get('model_configuration', {}).get('model_name', 'N/A')}")
                print(f"  • Proveedor: {agent_info.get('model_configuration', {}).get('provider', 'N/A')}")
                print(f"  • Creado: {agent_info.get('created_at', 'N/A')}")

            except Exception as e:
                print(f"❌ Error al crear el agente: {str(e)}")
                print(f"\nDetalles del error: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(main())
