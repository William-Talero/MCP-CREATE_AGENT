# Creación Agente MCP

MCP Server para la creación de agentes en Azure AI Foundry usando arquitectura limpia, DDD y buenas prácticas. Implementado en **Python** con Pydantic y tipo safety.

## 🚀 Quick Start

```bash
# 1. Clonar e instalar
git clone <repository-url>
cd creacion-agente-mcp

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar
cp .env.example .env
# Editar .env con tus credenciales de Azure

# 5. Ejecutar (STDIO - para Claude Desktop)
creacion-agente-mcp

# O para acceso HTTP/SSE remoto
export MCP_TRANSPORT=sse
export MCP_PORT=8000
creacion-agente-mcp
```

## 📖 Documentación

- **[Guía de Integración](INTEGRATION.md)** - Cómo conectarte al MCP desde diferentes clientes
- **[Transporte (STDIO/SSE)](TRANSPORT.md)** - Opciones de conexión: local (STDIO) o remoto (HTTP/SSE)
- **[Ejemplos](examples/)** - Ejemplos de código completos

## Características

- **Python 3.11+**: Moderno, con type hints completos
- **Arquitectura Limpia**: Separación clara de capas (Domain, Application, Infrastructure, Presentation)
- **Domain-Driven Design**: Value Objects, Entidades, Repositorios e Interfaces bien definidas
- **Type Safety**: Pydantic para validación y type safety en runtime
- **Async/Await**: Operaciones asíncronas nativas con asyncio
- **MCP Protocol**: Integración completa con Model Context Protocol
- **Dual Transport**: Soporte para STDIO (local) y HTTP/SSE (remoto)
- **Azure AI Foundry**: Soporte para múltiples modelos de AI
  - OpenAI (GPT-4, GPT-4 Turbo, GPT-4o, GPT-3.5)
  - Anthropic (Claude 3.5 Sonnet, Claude 3 Opus/Sonnet/Haiku)
  - Meta (Llama 3.1 405B/70B/8B)
  - Mistral (Mistral Large, Small)
  - Google (Gemini 1.5 Pro/Flash)
  - Cohere (Command R+)

## Estructura del Proyecto

```
creacion_agente_mcp/
├── domain/                    # Capa de dominio
│   ├── entities/             # Entidades del negocio
│   │   └── agent.py         # Entidad Agent
│   ├── value_objects/        # Objetos de valor
│   │   ├── agent_id.py
│   │   ├── agent_name.py
│   │   ├── agent_description.py
│   │   ├── ai_model.py
│   │   └── model_configuration.py
│   ├── repositories/         # Interfaces de repositorios
│   │   └── agent_repository.py
│   └── exceptions/           # Excepciones del dominio
│       └── domain_exception.py
├── application/              # Capa de aplicación
│   └── use_cases/           # Casos de uso
│       ├── create_agent_use_case.py
│       ├── get_agent_use_case.py
│       └── list_agents_use_case.py
├── infrastructure/           # Capa de infraestructura
│   └── azure/               # Cliente de Azure Foundry
│       ├── azure_foundry_client.py
│       └── azure_agent_repository.py
├── presentation/             # Capa de presentación
│   └── mcp_server.py        # Servidor MCP
├── config.py                 # Configuración (Pydantic Settings)
└── main.py                   # Punto de entrada
```

## Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
source venv/bin/activate  # Linux/macOS
# O en Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# O instalar en modo desarrollo
pip install -e .[dev]
```

## Configuración

Crea un archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Configura las siguientes variables de entorno:

### Variables requeridas:

- `AZURE_AI_ENDPOINT`: Endpoint base de Azure AI Foundry (sin `/api/projects`)
  - Ejemplo: `https://your-resource.services.ai.azure.com`

### Variables de autenticación (elige una opción):

**Opción 1: API Key** (más simple para desarrollo)
- `AZURE_AI_API_KEY`: API Key de Azure AI Foundry

**Opción 2: Service Principal** (recomendado para producción)
- `AZURE_TENANT_ID`: ID del tenant de Azure
- `AZURE_CLIENT_ID`: Client ID del service principal
- `AZURE_CLIENT_SECRET`: Client secret del service principal

**Opción 3: Managed Identity** (para ambientes Azure)
- `USE_MANAGED_IDENTITY=true`: Usa la identidad administrada del pod/VM

### Variables opcionales:

- `AZURE_AI_API_VERSION`: Versión de la API (default: 2025-05-01)
- `HEALTH_CHECK_PORT`: Puerto para health checks (default: 3000)

## Uso

### Como servidor MCP

```bash
# Opción 1: Usando Python directamente
python -m creacion_agente_mcp.main

# Opción 2: Usando el comando instalado
creacion-agente-mcp
```

### Conectarse al MCP

Hay varias formas de conectarte al servidor MCP. Ver [Guía de Integración completa](INTEGRATION.md).

#### 1. Claude Desktop

Agrega esto a tu `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "creacion-agente": {
      "command": "python",
      "args": ["-m", "creacion_agente_mcp.main"],
      "env": {
        "AZURE_AI_ENDPOINT": "https://your-resource.services.ai.azure.com",
        "AZURE_AI_API_KEY": "your-api-key"
      }
    }
  }
}
```

#### 2. Cliente TypeScript/JavaScript

```typescript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const transport = new StdioClientTransport({
  command: 'python',
  args: ['-m', 'creacion_agente_mcp.main'],
  env: {
    AZURE_AI_ENDPOINT: 'https://your-resource.services.ai.azure.com',
    AZURE_AI_API_KEY: 'your-api-key'
  }
});

const client = new Client({ name: 'my-client', version: '1.0.0' }, {});
await client.connect(transport);
```

#### 3. Cliente Python

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["-m", "creacion_agente_mcp.main"],
    env={
        "AZURE_AI_ENDPOINT": "https://your-resource.services.ai.azure.com",
        "AZURE_AI_API_KEY": "your-api-key"
    }
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # Usar el cliente
```

Ver más opciones en [INTEGRATION.md](INTEGRATION.md).

### Herramientas disponibles

#### 1. list_models

Lista todos los modelos de AI disponibles en Azure AI Foundry con sus características.

**Parámetros opcionales:**
- `provider`: Filtrar por proveedor específico (`azure_openai`, `anthropic`, `meta`, `mistral`, `cohere`, `google`)

**Ejemplo de respuesta:**
```json
{
  "total": 15,
  "models": [
    {
      "model": "gpt-4o",
      "displayName": "GPT-4o",
      "provider": "azure_openai",
      "description": "GPT-4 optimizado multimodal",
      "maxTokens": 128000,
      "supportsTools": true,
      "supportsVision": true
    },
    {
      "model": "claude-3-5-sonnet",
      "displayName": "Claude 3.5 Sonnet",
      "provider": "anthropic",
      "description": "Último modelo de Anthropic, equilibrio perfecto",
      "maxTokens": 200000,
      "supportsTools": true,
      "supportsVision": true
    }
  ]
}
```

#### 2. create_agent

Crea un nuevo agente en Azure AI Foundry con el modelo de AI seleccionado.

**Parámetros requeridos:**
- `projectName`: Nombre del proyecto de Azure AI Foundry
- `name`: Nombre del agente (1-100 caracteres)
- `modelName`: Nombre del modelo (usa `list_models` para ver opciones)

**Parámetros opcionales:**
- `provider`: Proveedor del modelo (se detecta automáticamente si no se especifica)
- `temperature`: Temperatura del modelo (0-2, default: 0.7)
- `maxTokens`: Máximo de tokens (varía según modelo, default: automático)
- `topP`: Top P sampling (0-1, default: 1.0)
- `frequencyPenalty`: Penalización de frecuencia (-2 a 2, default: 0)
- `presencePenalty`: Penalización de presencia (-2 a 2, default: 0)
- `instructions`: Instrucciones del sistema (max 10000 caracteres)
- `tools`: Array de herramientas disponibles (max 50)
- `metadata`: Objeto con metadatos adicionales

**Ejemplos:**

**Usando GPT-4:**
```json
{
  "projectName": "my-foundry-project",
  "name": "Asistente de Ventas",
  "modelName": "gpt-4",
  "temperature": 0.7,
  "instructions": "Eres un asistente de ventas experto...",
  "tools": ["web_search", "calculator"]
}
```

**Usando Claude 3.5 Sonnet:**
```json
{
  "projectName": "my-foundry-project",
  "name": "Analizador de Código",
  "modelName": "claude-3-5-sonnet",
  "provider": "anthropic",
  "temperature": 0.3,
  "maxTokens": 150000,
  "instructions": "Eres un experto en análisis de código..."
}
```

**Usando Llama 3.1 405B:**
```json
{
  "projectName": "my-foundry-project",
  "name": "Generador de Contenido",
  "modelName": "llama-3.1-405b",
  "provider": "meta",
  "temperature": 0.9,
  "instructions": "Eres un escritor creativo..."
}
```

**Usando Gemini 1.5 Pro:**
```json
{
  "projectName": "my-foundry-project",
  "name": "Asistente Multimodal",
  "modelName": "gemini-1.5-pro",
  "provider": "google",
  "maxTokens": 500000,
  "instructions": "Eres un asistente multimodal..."
}
```

#### 3. get_agent

Obtiene información de un agente específico.

**Parámetros:**
- `projectName`: Nombre del proyecto de Azure AI Foundry
- `agentId`: ID del agente

#### 4. list_agents

Lista todos los agentes creados en un proyecto.

**Parámetros:**
- `projectName`: Nombre del proyecto de Azure AI Foundry

## Arquitectura

### Domain Layer (Dominio)

Define las reglas de negocio y entidades principales:

- **Agent**: Entidad principal que representa un agente
- **AgentId, AgentName, AgentDescription**: Value Objects para validación
- **ModelConfiguration**: Value Object para configuración del modelo
- **IAgentRepository**: Interface del repositorio

### Application Layer (Aplicación)

Contiene la lógica de los casos de uso:

- **CreateAgentUseCase**: Crea un nuevo agente
- **GetAgentUseCase**: Obtiene un agente por ID
- **ListAgentsUseCase**: Lista todos los agentes

### Infrastructure Layer (Infraestructura)

Implementaciones concretas de las interfaces:

- **AzureFoundryClient**: Cliente para Azure OpenAI Assistants API
- **AzureAgentRepository**: Implementación del repositorio usando Azure

### Presentation Layer (Presentación)

Capa de presentación MCP:

- **MCPServer**: Servidor MCP con las herramientas expuestas
- **AgentSchemas**: Validación de entrada con Zod

## Principios aplicados

- **SOLID**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **Clean Architecture**: Independencia de frameworks, testabilidad, independencia de UI
- **DDD**: Value Objects, Entities, Repositories, Domain Exceptions
- **Type Safety**: TypeScript estricto con validación en runtime (Zod)

## Desarrollo

```bash
# Instalar en modo desarrollo
pip install -e .[dev]

# Ejecutar
python -m creacion_agente_mcp.main

# Tests (cuando estén implementados)
pytest

# Type checking
mypy creacion_agente_mcp

# Linting
ruff check creacion_agente_mcp

# Formateo
black creacion_agente_mcp
```

## Deployment

### Docker

#### Construir imagen Docker

```bash
# Construcción básica (usando Dockerfile.python)
docker build -f Dockerfile.python -t creacion-agente-mcp:latest .

# Con registry
docker build -f Dockerfile.python -t myregistry.azurecr.io/creacion-agente-mcp:v1.0.0 .
```

#### Ejecutar localmente con Docker

```bash
# Asegúrate de tener un archivo .env configurado
cp .env.example .env
# Edita .env con tus credenciales

# Ejecutar usando el script
./scripts/run-local-docker.sh

# O manualmente
docker run -d \
  --name creacion-agente-mcp \
  --env-file .env \
  -p 3000:3000 \
  creacion-agente-mcp:latest
```

#### Health Checks

El servidor incluye endpoints de health check para Kubernetes/Docker:

- **`/health`**: Health check general
- **`/live`**: Liveness probe
- **`/ready`**: Readiness probe

```bash
# Verificar health
curl http://localhost:3000/health
```

### Kubernetes

#### Preparar configuración

1. **Actualizar credenciales de Azure**:
   ```bash
   # Editar k8s/secret.yaml con tus credenciales
   vim k8s/secret.yaml
   ```

2. **Personalizar configuración** (opcional):
   ```bash
   # Editar deployment, service, etc.
   vim k8s/deployment.yaml
   ```

#### Desplegar en Kubernetes

```bash
# Actualizar k8s/secret.python.yaml con tus credenciales

# Desplegar
kubectl apply -f k8s/secret.python.yaml
kubectl apply -f k8s/deployment.python.yaml

# Verificar el deployment
kubectl get all -l app=creacion-agente-mcp
kubectl logs -l app=creacion-agente-mcp
```

#### Configuración de Kubernetes incluida

- **`deployment.yaml`**: Deployment con 2 réplicas, health checks, recursos límitados
- **`service.yaml`**: Service ClusterIP para exponer el pod
- **`secret.yaml`**: Secret para credenciales de Azure (actualizar antes de usar)
- **`configmap.yaml`**: ConfigMap para variables de entorno
- **`hpa.yaml`**: HorizontalPodAutoscaler para auto-scaling (2-10 pods)

#### Características del Deployment

- ✅ Non-root user (1001)
- ✅ Read-only filesystem
- ✅ Security context configurado
- ✅ Liveness y readiness probes
- ✅ Resource limits configurados
- ✅ Auto-scaling con HPA
- ✅ Graceful shutdown

### Variables de Entorno

**Requeridas:**
- `AZURE_AI_ENDPOINT`: Endpoint base de Azure AI Foundry
  - Ejemplo: `https://your-resource.services.ai.azure.com`

**Autenticación (elegir una opción):**
- `AZURE_AI_API_KEY`: API Key de Azure AI Foundry, O
- `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`: Service Principal, O
- `USE_MANAGED_IDENTITY=true`: Managed Identity (en Azure)

**Opcionales:**
- `AZURE_AI_API_VERSION`: Versión de la API (default: 2025-05-01)
- `HEALTH_CHECK_PORT`: Puerto para health checks (default: 3000)
- `NODE_ENV`: Entorno de ejecución (default: production)

### Azure Container Registry (ACR)

```bash
# Login a ACR
az acr login --name myregistry

# Build y push
docker build -t myregistry.azurecr.io/creacion-agente-mcp:v1.0.0 .
docker push myregistry.azurecr.io/creacion-agente-mcp:v1.0.0

# Actualizar deployment para usar la imagen de ACR
kubectl set image deployment/creacion-agente-mcp \
  mcp-server=myregistry.azurecr.io/creacion-agente-mcp:v1.0.0
```

## Monitoreo

### Logs

```bash
# Ver logs en Kubernetes
kubectl logs -f deployment/creacion-agente-mcp

# Ver logs en Docker
docker logs -f creacion-agente-mcp
```

### Métricas

El HPA incluido monitoreará automáticamente CPU y memoria para escalar los pods.

## Licencia

MIT
