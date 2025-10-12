# Datos Enviados para Crear AGENTE_WARP

## Información General
- **Nombre del Agente**: AGENTE_WARP
- **Proyecto**: agentes-test
- **Estado**: Datos preparados correctamente (el error 404 es porque el proyecto no existe en Azure, no por un problema con los datos)

## Datos Completos Enviados

```json
{
  "projectName": "agentes-test",
  "name": "AGENTE_WARP",
  "modelName": "gpt-4o",
  "provider": "azure_openai",
  "temperature": 0.7,
  "maxTokens": 4096,
  "topP": 1.0,
  "frequencyPenalty": 0.0,
  "presencePenalty": 0.0,
  "instructions": "Eres AGENTE_WARP, un asistente de IA avanzado diseñado para ayudar con tareas de desarrollo y análisis. Tu objetivo es proporcionar respuestas precisas, útiles y bien estructuradas.",
  "tools": [
    "code_interpreter"
  ],
  "metadata": {
    "created_by": "test_script",
    "version": "1.0",
    "purpose": "testing"
  }
}
```

## Desglose de los Parámetros

### Parámetros Requeridos
- **projectName**: `"agentes-test"` - Nombre del proyecto en Azure AI Foundry
- **name**: `"AGENTE_WARP"` - Nombre único del agente
- **modelName**: `"gpt-4o"` - Modelo de IA a utilizar

### Parámetros de Configuración del Modelo
- **provider**: `"azure_openai"` - Proveedor del modelo (Azure OpenAI)
- **temperature**: `0.7` - Controla la aleatoriedad (0.0 = determinista, 2.0 = muy aleatorio)
- **maxTokens**: `4096` - Máximo de tokens en la respuesta
- **topP**: `1.0` - Sampling de núcleo (nucleus sampling)
- **frequencyPenalty**: `0.0` - Penalización por repetición de tokens frecuentes (-2.0 a 2.0)
- **presencePenalty**: `0.0` - Penalización por repetición de tokens ya usados (-2.0 a 2.0)

### Instrucciones del Sistema
```
Eres AGENTE_WARP, un asistente de IA avanzado diseñado para ayudar con tareas
de desarrollo y análisis. Tu objetivo es proporcionar respuestas precisas,
útiles y bien estructuradas.
```

### Herramientas Habilitadas
- **code_interpreter**: Permite al agente ejecutar código Python y analizar datos

### Metadatos Adicionales
```json
{
  "created_by": "test_script",
  "version": "1.0",
  "purpose": "testing"
}
```

## URL de la Solicitud
```
POST https://ai-agentes.services.ai.azure.com/api/projects/agentes-test/assistants?api-version=2025-05-01
```

## Estructura Interna (CreateAgentDTO)

El sistema convierte estos datos a la siguiente estructura interna:

```python
CreateAgentDTO(
    project_name="agentes-test",
    name="AGENTE_WARP",
    model_name="gpt-4o",
    provider="azure_openai",
    temperature=0.7,
    max_tokens=4096,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    instructions="Eres AGENTE_WARP, un asistente de IA avanzado...",
    tools=["code_interpreter"],
    metadata={
        "created_by": "test_script",
        "version": "1.0",
        "purpose": "testing"
    }
)
```

## Proceso de Creación

1. **Validación de Datos**: Los datos se validan con Pydantic usando `CreateAgentDTO`
2. **Construcción de Value Objects**: Se crean objetos de dominio (`AgentName`, `AgentDescription`, `ModelConfiguration`)
3. **Creación de Entidad**: Se crea una entidad `Agent` con todas las propiedades
4. **Llamada a Azure**: Se envía una solicitud POST a Azure AI Foundry con la estructura de datos

## Notas

- El error 404 ocurrió porque el proyecto "agentes-test" no existe en tu instancia de Azure AI Foundry
- Todos los datos se prepararon correctamente siguiendo las validaciones del sistema
- Para crear el agente exitosamente, necesitas usar un proyecto existente en Azure o crear uno nuevo

## Para Crear el Agente Exitosamente

1. Verifica que el proyecto existe en Azure AI Foundry
2. O crea un nuevo proyecto con el nombre deseado
3. Actualiza el valor de `project_name` en el script con el nombre real del proyecto
4. Ejecuta nuevamente el script

## Script de Prueba

El script completo está disponible en: `test_create_agent.py`
