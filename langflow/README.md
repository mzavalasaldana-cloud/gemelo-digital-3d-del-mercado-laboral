# Flujo del Copiloto IA de LaborTwin en Langflow

Este directorio contiene la definición oficial del flujo de Langflow para el Copiloto IA del Gemelo Digital 3D del Mercado Laboral (modelo ITDT).

---

## 1. Arquitectura del Flujo

El flujo implementa una arquitectura secuencial y desacoplada de 4 etapas:

1. **Chat Input (`ChatInput`)**: Recibe la consulta del usuario enriquecida dinámicamente por el backend FastAPI con las evidencias micro y macroeconómicas (`build_simulation_context_prompt`).
2. **Prompt (`PromptComponent`)**: Inyecta el rol del Copiloto Experto en Economía Laboral, las definiciones canónicas de escenarios (A, B1, B2, C, D) y las reglas de no alucinación.
3. **Modelo Gemini (`GoogleGenerativeAIComponent`)**: Ejecuta la inferencia utilizando la variable global desacoplada `GEMINI_API_KEY` (sin claves en el lienzo).
4. **Chat Output (`ChatOutput`)**: Emite la respuesta analítica formateada en Markdown hacia la interfaz web de LaborTwin.

---

## 2. Instrucciones de Importación y Puesta en Marcha

### Paso A: Importar el Flujo
1. Inicie Langflow Desktop o abra la consola web en `http://127.0.0.1:7860`.
2. En la pantalla principal de proyectos, haga clic en **Upload / Import**.
3. Seleccione el archivo [`copiloto_itdt.json`](./copiloto_itdt.json).
4. El flujo aparecerá registrado bajo el nombre **LaborTwin Copilot V1**.

### Paso B: Configurar la Variable Global de Gemini
1. En Langflow, abra **Settings** (ícono de engranaje) → **Global Variables**.
2. Haga clic en **Add New**.
3. Configure los siguientes campos:
   - **Variable Name**: `GEMINI_API_KEY`
   - **Type**: `Credential`
   - **Value**: Su clave de Google AI Studio configurada para Gemini.
4. Guarde los cambios. El componente `Google Generative AI` cargará automáticamente la clave en tiempo de ejecución (`load_from_db: true`).

### Paso C: Generar y Configurar la API Key de Langflow
1. En **Settings** → pestaña **Langflow API Keys**, haga clic en **Add New**.
2. Asigne un nombre descriptivo (ej. `LaborTwin-Copilot`) y copie la clave generada.
3. Abra el archivo `.env` en la raíz del proyecto y configure:
   ```bash
   LANGFLOW_BASE_URL=http://127.0.0.1:7860
   LANGFLOW_COPILOT_FLOW_ID=2d660758-1eee-46f8-969f-c17998844627
   LANGFLOW_API_KEY=<su_clave_api_de_langflow>
   ```
   *(Reemplace `LANGFLOW_COPILOT_FLOW_ID` por el ID asignado a su flujo importado si difiere).*

---

## 3. Mecanismo de Cascada de 3 Niveles en el Backend

El backend de LaborTwin (`backend/copilot_service.py`) gestiona la resiliencia en tres niveles ordenados:
- **Nivel 1 (Langflow)**: Orquestación gráfica del flujo vía REST API.
- **Nivel 2 (Gemini Directo)**: Invocación directa a la API REST de Google Gemini si Langflow no está activo o devuelve error.
- **Nivel 3 (Contingencia Determinista)**: Respuestas basadas en reglas analíticas y tablas precomputadas (`outputs/`) sin depender de LLMs externos.
