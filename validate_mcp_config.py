#!/usr/bin/env python3
"""
Script para validar la configuración MCP para Copilot
"""
import json
import os
import asyncio
from pathlib import Path

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_check(passed, message):
    symbol = f"{GREEN}✅{RESET}" if passed else f"{RED}❌{RESET}"
    print(f"{symbol} {message}")

def print_info(message):
    print(f"{BLUE}ℹ️{RESET}  {message}")

def print_warning(message):
    print(f"{YELLOW}⚠️{RESET}  {message}")

async def main():
    print("=" * 80)
    print(f"{BLUE}VALIDACIÓN DE CONFIGURACIÓN MCP PARA COPILOT{RESET}")
    print("=" * 80)
    print()

    # 1. Verificar que existe el archivo mcp.json
    mcp_file = Path(".vscode/mcp.json")
    print_check(mcp_file.exists(), f"Archivo {mcp_file} existe")

    if not mcp_file.exists():
        print_warning("Crea el archivo .vscode/mcp.json para configurar Copilot")
        return

    # 2. Leer y validar estructura JSON
    try:
        with open(mcp_file, 'r') as f:
            config = json.load(f)
        print_check(True, "JSON válido")
    except json.JSONDecodeError as e:
        print_check(False, f"JSON inválido: {e}")
        return

    # 3. Validar estructura básica
    has_servers = "servers" in config
    print_check(has_servers, "Tiene clave 'servers'")

    if not has_servers:
        return

    has_agentes = "agentes-foundry" in config["servers"]
    print_check(has_agentes, "Tiene servidor 'agentes-foundry'")

    if not has_agentes:
        return

    server_config = config["servers"]["agentes-foundry"]

    # 4. Validar configuración del servidor
    has_type = server_config.get("type") == "stdio"
    print_check(has_type, "Tipo de servidor: stdio")

    has_command = "command" in server_config
    print_check(has_command, f"Comando configurado: {server_config.get('command', 'N/A')}")

    has_env = "env" in server_config
    print_check(has_env, "Variables de entorno configuradas")

    if not has_env:
        return

    env = server_config["env"]

    # 5. Validar variables de entorno requeridas
    print()
    print(f"{BLUE}Variables de Entorno:{RESET}")
    print("-" * 80)

    required_vars = [
        "AZURE_AI_ENDPOINT",
        "AZURE_AI_API_VERSION",
        "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
        "USE_MANAGED_IDENTITY"
    ]

    all_vars_present = True
    for var in required_vars:
        present = var in env
        all_vars_present = all_vars_present and present
        value = env.get(var, "N/A")

        # Ocultar secretos
        if "SECRET" in var and present:
            display_value = value[:10] + "..." if len(value) > 10 else "***"
        else:
            display_value = value

        print_check(present, f"{var}: {display_value}")

    # 6. Validar valores específicos
    print()
    print(f"{BLUE}Validaciones de Valores:{RESET}")
    print("-" * 80)

    # Endpoint
    endpoint = env.get("AZURE_AI_ENDPOINT", "")
    endpoint_correct = endpoint == "https://ai-agentes.services.ai.azure.com"
    print_check(endpoint_correct, f"Endpoint correcto: {endpoint}")

    # API Version
    api_version = env.get("AZURE_AI_API_VERSION", "")
    version_correct = api_version == "2025-05-01"
    print_check(version_correct, f"API Version: {api_version}")

    if api_version != "2025-05-01":
        print_warning(f"Se recomienda usar '2025-05-01' en lugar de '{api_version}'")

    # Managed Identity
    use_mi = env.get("USE_MANAGED_IDENTITY", "")
    mi_correct = use_mi.lower() == "false"
    print_check(mi_correct, f"USE_MANAGED_IDENTITY: {use_mi} (Service Principal activo)")

    # 7. Verificar que el comando existe
    print()
    print(f"{BLUE}Verificación de Comando:{RESET}")
    print("-" * 80)

    command = server_config.get("command", "")

    # Verificar si el comando está en PATH o es ejecutable
    from shutil import which
    command_exists = which(command) is not None
    print_check(command_exists, f"Comando '{command}' encontrado en PATH")

    if not command_exists:
        print_warning("Asegúrate de que 'creacion-agente-mcp' esté instalado: pip install -e .")

    # 8. Probar conexión básica
    print()
    print(f"{BLUE}Prueba de Conexión:{RESET}")
    print("-" * 80)

    print_info("Probando conexión con Service Principal...")

    try:
        from creacion_agente_mcp.config import get_settings
        from creacion_agente_mcp.infrastructure.azure import AzureFoundryClient, AzureFoundryConfig

        # Usar las variables del mcp.json
        test_config = AzureFoundryConfig(
            endpoint=env.get("AZURE_AI_ENDPOINT"),
            api_version=env.get("AZURE_AI_API_VERSION"),
            tenant_id=env.get("AZURE_TENANT_ID"),
            client_id=env.get("AZURE_CLIENT_ID"),
            client_secret=env.get("AZURE_CLIENT_SECRET"),
            use_managed_identity=env.get("USE_MANAGED_IDENTITY", "false").lower() == "true"
        )

        client = AzureFoundryClient(test_config)

        # Probar obtener headers de autenticación
        headers = await client._get_auth_headers()
        has_auth = "Authorization" in headers or "api-key" in headers
        print_check(has_auth, "Token de autenticación obtenido")

        # Probar listar agentes
        try:
            agents = await client.list_agents("AGENTES_MCP")
            print_check(True, f"Conexión exitosa - {len(agents)} agentes encontrados")
        except Exception as e:
            print_check(False, f"Error al listar agentes: {str(e)[:100]}")

    except Exception as e:
        print_check(False, f"Error en prueba de conexión: {str(e)[:100]}")

    # 9. Resumen final
    print()
    print("=" * 80)
    print(f"{BLUE}RESUMEN{RESET}")
    print("=" * 80)

    if endpoint_correct and version_correct and all_vars_present and command_exists:
        print(f"{GREEN}✅ Configuración lista para GitHub Copilot{RESET}")
        print()
        print_info("Pasos siguientes:")
        print("  1. Reinicia VS Code")
        print("  2. Abre un archivo del proyecto")
        print("  3. Abre Copilot Chat (@agentes-foundry)")
        print("  4. Prueba el comando: list_agents con projectName: AGENTES_MCP")
    else:
        print(f"{RED}❌ Hay problemas en la configuración{RESET}")
        print()
        print_warning("Revisa los errores anteriores y corrígelos")

        if not endpoint_correct:
            print_info("Actualiza AZURE_AI_ENDPOINT a: https://ai-agentes.services.ai.azure.com")
        if not version_correct:
            print_info("Actualiza AZURE_AI_API_VERSION a: 2025-05-01")
        if not all_vars_present:
            print_info("Asegúrate de que todas las variables estén definidas")

if __name__ == "__main__":
    asyncio.run(main())
