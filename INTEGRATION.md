# Guía de Integración - Creación Agente MCP

Esta guía explica cómo conectarte y usar el MCP Server de Creación de Agentes desde diferentes entornos.

## Tabla de Contenidos

1. [Claude Desktop](#claude-desktop)
2. [Cliente TypeScript/JavaScript](#cliente-typescriptjavascript)
3. [Cliente Python](#cliente-python)
4. [Docker Compose](#docker-compose)
5. [API HTTP (vía Proxy)](#api-http-vía-proxy)
6. [Kubernetes Service](#kubernetes-service)

---

## Claude Desktop

### Configuración para Claude Desktop App

1. **Ubicación del archivo de configuración:**

   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Agregar el servidor MCP:**

   ```json
   {
     "mcpServers": {
       "creacion-agente": {
         "command": "node",
         "args": [
           "/ruta/absoluta/a/creacion-agente-mcp/dist/index.js"
         ],
         "env": {
           "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com",
           "AZURE_OPENAI_API_KEY": "your-api-key-here"
         }
       }
     }
   }
   ```

3. **Reiniciar Claude Desktop**

4. **Verificar conexión:**
   - Abre Claude Desktop
   - El servidor debería aparecer en la lista de MCP servers
   - Puedes usar las herramientas directamente en la conversación

### Ejemplo de uso en Claude Desktop

```
Usuario: "Lista los modelos disponibles de Anthropic"

Claude: [Llama a list_models con provider: "anthropic"]

Usuario: "Crea un agente con Claude 3.5 Sonnet para análisis de código"

Claude: [Llama a create_agent con los parámetros necesarios]
```

---

## Cliente TypeScript/JavaScript

### Instalación

```bash
npm install @modelcontextprotocol/sdk
```

### Ejemplo de Uso

Ver archivo completo: [`examples/client-example.ts`](examples/client-example.ts)

```typescript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const transport = new StdioClientTransport({
  command: 'node',
  args: ['dist/index.js'],
  env: {
    AZURE_OPENAI_ENDPOINT: process.env.AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY: process.env.AZURE_OPENAI_API_KEY,
  },
});

const client = new Client({
  name: 'my-client',
  version: '1.0.0',
}, { capabilities: {} });

await client.connect(transport);

// Usar las herramientas
const result = await client.callTool({
  name: 'create_agent',
  arguments: {
    name: 'Mi Agente',
    description: 'Descripción del agente',
    deploymentName: 'gpt-4-deployment',
    modelName: 'gpt-4o',
  },
});
```

### Ejecutar el ejemplo

```bash
cd examples
npm install
npx tsx client-example.ts
```

---

## Cliente Python

### Instalación

```bash
pip install mcp
```

### Ejemplo de Uso

Ver archivo completo: [`examples/python-client-example.py`](examples/python-client-example.py)

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="node",
    args=["dist/index.js"],
    env={
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
    }
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        result = await session.call_tool(
            "create_agent",
            arguments={
                "name": "Mi Agente",
                "description": "Descripción",
                "deploymentName": "gpt-4-deployment",
                "modelName": "gpt-4o",
            }
        )
```

### Ejecutar el ejemplo

```bash
cd examples
chmod +x python-client-example.py
python3 python-client-example.py
```

---

## Docker Compose

### Configuración

Ver archivo completo: [`examples/docker-compose.yml`](examples/docker-compose.yml)

```yaml
version: '3.8'

services:
  mcp-server:
    image: creacion-agente-mcp:latest
    environment:
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
    ports:
      - "3000:3000"
```

### Uso

```bash
# 1. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 2. Levantar el servicio
cd examples
docker-compose up -d

# 3. Verificar health
curl http://localhost:3000/health

# 4. Conectar desde tu aplicación usando stdio transport al contenedor
```

---

## API HTTP (vía Proxy)

Si necesitas acceder al MCP vía HTTP, puedes usar un proxy como `mcp-http-proxy`:

### Opción 1: Usando npx

```bash
npx @modelcontextprotocol/http-proxy \
  --command "node" \
  --args "dist/index.js" \
  --port 8080
```

### Opción 2: Crear un wrapper

```typescript
// http-wrapper.ts
import express from 'express';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const app = express();
app.use(express.json());

let client: Client;

app.post('/mcp/call-tool', async (req, res) => {
  try {
    const result = await client.callTool(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(8080, () => {
  console.log('MCP HTTP Proxy listening on port 8080');
});
```

---

## Kubernetes Service

### Conectar desde otro pod en el mismo cluster

```yaml
# my-app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: my-app:latest
        env:
        - name: MCP_SERVICE_URL
          value: "http://creacion-agente-mcp:3000"
```

### Conectar vía Port Forward (desarrollo)

```bash
# Port forward el servicio
kubectl port-forward service/creacion-agente-mcp 3000:3000

# Ahora puedes conectar localmente
curl http://localhost:3000/health
```

### Conectar con Ingress (producción)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcp-ingress
spec:
  rules:
  - host: mcp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: creacion-agente-mcp
            port:
              number: 3000
```

---

## Herramientas Disponibles

### 1. `list_models`

Lista todos los modelos de AI disponibles.

```json
{
  "name": "list_models",
  "arguments": {
    "provider": "anthropic"  // opcional
  }
}
```

### 2. `create_agent`

Crea un nuevo agente en Azure AI Foundry.

```json
{
  "name": "create_agent",
  "arguments": {
    "name": "Mi Agente",
    "description": "Descripción del agente",
    "deploymentName": "deployment-name",
    "modelName": "gpt-4o",
    "temperature": 0.7,
    "maxTokens": 50000,
    "instructions": "Instrucciones del sistema..."
  }
}
```

### 3. `get_agent`

Obtiene información de un agente específico.

```json
{
  "name": "get_agent",
  "arguments": {
    "agentId": "asst_xxxxxxxxxxxxx"
  }
}
```

### 4. `list_agents`

Lista todos los agentes creados.

```json
{
  "name": "list_agents",
  "arguments": {}
}
```

---

## Troubleshooting

### El servidor no inicia

```bash
# Verificar variables de entorno
echo $AZURE_OPENAI_ENDPOINT
echo $AZURE_OPENAI_API_KEY

# Verificar logs
docker logs creacion-agente-mcp
kubectl logs -l app=creacion-agente-mcp
```

### Error de conexión desde el cliente

```bash
# Verificar que el servidor esté corriendo
curl http://localhost:3000/health

# Verificar permisos del archivo
ls -la dist/index.js

# Verificar versión de Node
node --version  # Debe ser >= 20
```

### Error de autenticación de Azure

```bash
# Verificar credenciales
az account show

# Probar conexión directa
curl -H "api-key: $AZURE_OPENAI_API_KEY" \
  "$AZURE_OPENAI_ENDPOINT/openai/deployments?api-version=2024-02-15-preview"
```

---

## Recursos Adicionales

- [MCP SDK Documentation](https://modelcontextprotocol.io)
- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Ejemplos completos](./examples/)

