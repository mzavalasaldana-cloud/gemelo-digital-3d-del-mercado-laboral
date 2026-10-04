# Auditoría, Limpieza y Optimización del Sistema (Fase 1)

Este documento registra el inventario exhaustivo, las evidencias técnicas y las decisiones tomadas durante el proceso de limpieza y optimización del repositorio, preservando intactas las funcionalidades operativas (React 3D `src/`, FastAPI `backend/`, Streamlit `streamlit_app/`, motor de Machine Learning, Copiloto con Langflow y Postgres) y la integridad de las ecuaciones y datos del modelo canónico (`itdt/`, `data/`, `outputs/`).

---

## 1. Punto de Referencia (Línea Base Inicial)

- **Rama de trabajo:** `limpieza` (creada a partir de `itdt-articulo`).
- **Respaldo de validación econométrica:** Los 12 archivos CSV de `outputs/` (`sanctions_sweep_data.csv`, `table2` a `table12`) fueron respaldados en el directorio temporal fuera del repositorio:
  `scratch/baseline_outputs_csv/`.
- **Resultados de pruebas y validaciones iniciales:**
  - `pytest`: **24 pasadas en 5.63 s** (100 % de éxito).
  - `npm run lint`: Salida de `tsc --noEmit` reporta 4 errores preexistentes conocidos en `src/services/api.ts` (`Property 'env' does not exist on type 'ImportMeta'`).
  - `npm run build`: Exitoso en 11.83 s (`dist/index.html` 1.43 kB, `dist/assets/index-*.css` 96.33 kB, `dist/assets/index-*.js` 1,517.80 kB).

### Conteo Inicial de Líneas de Código (LOC)

| Carpeta | Archivos | Líneas de Código | Rol Arquitectural |
|---|---|---|---|
| `backend/` | 11 | 2,391 | API FastAPI, ORM PostgreSQL, Copiloto Langflow y ML Engine |
| `streamlit_app/` | 14 | 4,018 | Dashboard analítico, vistas OIT y HUD de políticas |
| `src/` | 32 | 14,231 | Aplicación web interactiva React 19 + Three.js 3D |
| `itdt/` | 9 | 3,500 | Modelo canónico ABM, calibración SMM y validación LOCO |
| `web_demo/` | 2 | 678 | Adaptador cinemático y puente de simulación 3D |
| **Total** | **68** | **24,818** | **Base de código activa** |

---

## 2. Tabla de Inventario y Decisiones

| Archivo o función | Motivo | Evidencia (resultado del grep) | Acción |
|---|---|---|---|
| `scratch/` | Prototipos y scripts de exploración temporal (`bench_nested_bisect.py`, `fetch_wb.py`, `check_ilo.py`, etc.). | Búsqueda grep en `.py`, `.ts`, `.tsx`, `.json`, `.yml`, `.yaml`, `Makefile`: **0 importaciones o referencias**. Ignorado en `.gitignore`. | **Borrar** de disco. |
| `test_models.py` (raíz) | Script de prueba manual de selección de modelos en Langflow. `backend/copilot_service.py` utiliza activamente Langflow en `http://127.0.0.1:7860`. | `copilot_service.py:31` referencia `http://127.0.0.1:7860`. Útil para pruebas operativas de Langflow pero no pertenece a la raíz del repositorio. | **Mover** a `scripts/test_models.py`. |
| `bun.lock` | Lockfile redundante de Bun. El proyecto utiliza exclusivamente `npm` como gestor de paquetes. | Búsqueda grep: 0 referencias a comandos de `bun` en scripts o Makefile; `package-lock.json` gestiona dependencias activas. | **Borrar**. |
| `metadata.json` | Archivo residual de prototipo inicial con metadatos descriptivos genéricos. | Búsqueda grep en toda la base de código: **0 referencias**. | **Borrar**. |
| `__pycache__/`, `.pytest_cache/`, `dist/` | Cachés de compilación de Python, pytest y artefactos generados por `npm run build`. | Ya listados en `.gitignore`. Artefactos regenerables en tiempo de ejecución. | **Borrar**. |
| `models_store/model-xgboost-3a05e766.joblib` | Modelo XGBoost más reciente (28/09/2026 12:02:14) y algoritmo activo desplegado en `/api/v1/ml/active-model` (`algo-xgboost`). | `backend/main.py:349-367` (`MODELS_REGISTRY[0]` desplegado como champion). | **Conservar** (Modelo Activo Champion). |
| `models_store/model-lightgbm-0f0dbbfc.joblib` | Modelo LightGBM más reciente y único artefacto serializado de este algoritmo (28/09/2026 12:01:51). | Representante del algoritmo `lightgbm` para el selector de modelos. | **Conservar** (Campeón por algoritmo). |
| `models_store/model-random_forest-082db6a3.joblib` | Modelo Random Forest más reciente y único artefacto serializado de este algoritmo (05/09/2026 14:54:24). | Representante del algoritmo `random_forest` para el benchmark. | **Conservar** (Campeón por algoritmo). |
| `models_store/model-xgboost-72d4f00f.joblib` | Checkpoint intermedio de tuning XGBoost (28/09/2026 12:01:32). Superado por `3a05e766`. | Archivo histórico en disco. | **Conservar por ahora** (Listado para Fase posterior). |
| `models_store/model-xgboost-2e796572.joblib` | Checkpoint intermedio de tuning XGBoost (28/09/2026 12:01:04). Superado por `3a05e766`. | Archivo histórico en disco. | **Conservar por ahora** (Listado para Fase posterior). |
| `models_store/model-xgboost-8c12e763.joblib` | Checkpoint intermedio de tuning XGBoost (28/09/2026 11:31:56). Superado por `3a05e766`. | Archivo histórico en disco. | **Conservar por ahora** (Listado para Fase posterior). |
| `models_store/model-xgboost-c67c67ad.joblib` | Checkpoint intermedio de tuning XGBoost (28/09/2026 10:20:38). Superado por `3a05e766`. | Archivo histórico en disco. | **Conservar por ahora** (Listado para Fase posterior). |
| `models_store/model-xgboost-7a3e451a.joblib` | Checkpoint preliminar de tuning XGBoost (28/09/2026 04:26:11). | Archivo histórico en disco. | **Conservar por ahora** (Listado para Fase posterior). |
| `models_store/model-xgboost-bd05784e.joblib` | Checkpoint preliminar de tuning XGBoost (28/09/2026 04:25:32). | Archivo histórico en disco. | **Conservar por ahora** (Listado para Fase posterior). |
| `models_store/model-xgboost-96a686a6.joblib` | Checkpoint inicial antiguo de tuning XGBoost (05/09/2026 13:51:38). | Archivo histórico en disco. | **Conservar por ahora** (Listado para Fase posterior). |

---

## 3. Estado de Componentes Clave Conservados Intactos

1. **`itdt/`**: Ecuaciones, parámetros calibrados, motor numérico vectorial y funciones de validación LOCO se mantienen al 100 % inalteradas.
2. **`outputs/*.csv`**: Todas las tablas econométricas generadas para el artículo científico permanecen intactas.
3. **`data/raw/` y `data/ilostat_s_F.csv`**: Microdatos y descargas originales preservados intactos.
4. **`backend/`**: Rutas de autenticación, PostgreSQL, Copiloto con Langflow, WebSocket y entrenamiento/evaluación de ML permanecen funcionales.
5. **`streamlit_app/`**: Interfaz de visualización de políticas, curvas de Lorenz y auditoría OIT conectada a ITDTModel.
6. **`src/`**: Aplicación React 19 con gemelo digital 3D (Three.js), HUD de control y visualización de partículas.

---

## 4. Fase 2: Limpieza de Código Muerto y Unificación de Módulos (Parte 2)

### 4.1 Herramientas de Análisis Estático
- **Dependencias de desarrollo instaladas:** `ruff>=0.9.0` y `vulture>=2.14` (registradas en `requirements-dev.txt`).
- **Directorios analizados:** `backend/`, `streamlit_app/`, `web_demo/`, `itdt/` y `scripts/`.

### 4.2 Registro de Eliminaciones de Código Muerto

| Archivo | Elemento eliminado | Tipo de regla | Evidencia / Justificación técnica |
|---|---|---|---|
| `backend/ml_engine.py` | `import shap`, `HAS_SHAP` | Ruff F401 / Vulture | Import no utilizado; el motor de explicabilidad calcula contribuciones y curvas sin la librería shap pesada. |
| `backend/ml_engine.py` | `inf_target = 0.886` | Ruff F841 | Variable asignada en el generador sintético de India pero no leída posteriormente. |
| `backend/database.py` | `def get_sessionmaker():` | Vulture | Función accesora redundante; grep confirmó 0 llamadas en todo el repositorio (`AsyncSessionLocal` es el punto de acceso activo). |
| `streamlit_app/views/ai_engine_view.py` | `deploy_res` | Ruff F841 | Asignación del resultado de `deploy_model_to_backend` que nunca se consumía; se llama directamente a la función. |
| `streamlit_app/views/copilot_chat_view.py` | `calculate_structural_metrics` (import y variable `metrics`) | Ruff F401 / F841 | Import y llamada a cálculo estructural innecesaria en la vista de chat del copiloto. |
| `web_demo/simulation.py` | `p = model.params` | Ruff F841 | Asignación local no leída en la función de simulación. |
| `streamlit_app/config.py` | `LIGHT_COLORS`, `DARK_COLORS`, `COLORS`, `get_theme_colors` | Vulture | Paletas y función accesora sin uso alguno en el proyecto (la UI Streamlit se estiliza mediante clases CSS y tokens en `styles/`). |
| `itdt/calibrate.py` | `m_sim_inner = 0.0`, `m_sim_inner = m_sim` | Ruff F841 | Asignaciones locales no leídas en el bucle de bisección de calibración. |
| `itdt/cli.py` | `from typing import Dict, Any`, `export_calibration_artifacts_from_summary` | Ruff F401 | Imports no utilizados en el CLI de orquestación. |
| `itdt/experiments.py` | `import tracemalloc`, `sc_metrics = {}`, asignaciones `bars_f`, `bars_m`, `bars_t` | Ruff F401 / F841 | Import y variables no consumidas en la ejecución y graficación de experimentos. |
| `itdt/loco.py` | `F_obs = c_info["F_obs"]`, `M_obs = c_info["M_obs"]` | Ruff F841 | Asignaciones locales no utilizadas en el trabajador de evaluación de líneas base LOCO. |
| `itdt/metrics.py` | `N_W = len(worker_is_formal)`, `gender_gap = inf_female - inf_male` | Ruff F841 | Variables intermedias no utilizadas (el diccionario final retorna `r_gap`). |
| `itdt/parameters.py` | `dataclasses.field`, `typing.Union` | Ruff F401 | Imports no utilizados en la definición de parámetros. |
| Diversas vistas de `streamlit_app/` y `scripts/` | Módulos `os`, `re`, `json`, `math`, `List`, `Dict`, `Tuple` sin uso | Ruff F401 | Limpieza automática de imports redundantes sin efecto secundario. |

### 4.3 Unificación de Módulos Duplicados

1. **Motor de Machine Learning (`ml_engine.py`):**
   - **Antes:** Existían dos implementaciones divergentes: `backend/ml_engine.py` (con pipelines de FastAPI, modelos entrenados en `models_store/`, generación de presets nacionales) y `streamlit_app/ml_engine.py` (con funciones de microdatos sintéticos, EDA y validación cruzada).
   - **Acción:** Se unificaron en `backend/ml_engine.py`. Las 4 funciones de Streamlit (`generate_synthetic_microdata`, `compute_eda_summary`, `run_cross_validation_models`, `compute_cohort_projections`) se incorporaron formalmente a `backend/ml_engine.py`.
   - **Eliminación:** Se eliminó por completo `streamlit_app/ml_engine.py`. Las vistas de Streamlit (`ai_engine_view.py`, `datasets_reports_view.py`) importan directamente desde `backend.ml_engine`.

2. **Motores de Simulación (`simulation_engine.py`):**
   - **Verificación:** Se auditó `backend/simulation_engine.py` y `streamlit_app/simulation_engine.py`. Ambos módulos actúan como clientes directos de `web_demo/simulation.py`, que a su vez orquesta el modelo canónico `ITDTModel`. No hay lógica matemática duplicada ni discrepancias paramétricas.

### 4.4 Reemplazo de Mocks y Datos de Demostración

1. **`COUNTRY_PROFILES`:**
   - Se reemplazó la definición de constantes fijas en `streamlit_app/data/mock_data.py`. Ahora se alimenta dinámicamente de `itdt.parameters.COUNTRY_DATABASE` y `data/ilostat_s_F.csv`. Se eliminaron constantes arbitrarias de salarios e índices Gini no fundamentados.
2. **Historial de Simulaciones:**
   - La función `get_simulation_runs()` ahora consulta la base de datos PostgreSQL mediante el endpoint `/api/v1/simulations/history`, con fallback automático si el servicio no está disponible en tiempo de ejecución.
3. **Renombrado a `DEMO_` y Etiquetas de Demostración:**
   - Los conjuntos de datos sin fuente empírica oficial fueron renombrados:
     - `MOCK_USERS` → `DEMO_USERS`
     - `MOCK_FIRMS` → `DEMO_FIRMS`
     - `PRELOADED_DATASETS` → `DEMO_DATASETS`
   - Se incorporó la insignia y leyenda visible `"Datos de demostración"` en la interfaz de usuario en `user_management_view.py`, `datasets_reports_view.py` y `digital_twin_3d_view.py`.

### 4.5 Verificaciones de Integridad

- **Pruebas unitarias:** `python -m pytest` ejecutado: **24/24 pruebas pasadas exitosamente**.
- **Integridad econométrica:** Comparación byte a byte de los 12 archivos CSV de `outputs/` frente a la copia de seguridad de línea base: **100 % idénticos**.
- **Arranque de Backend:** `python -m uvicorn backend.main:app` arranca limpiamente e inicializa el esquema de PostgreSQL, respondiendo exitosamente (código 200) a solicitudes HTTP.
- **Arranque de Streamlit:** `streamlit run app.py` arranca limpiamente en modo headless, respondiendo exitosamente (código 200) a solicitudes HTTP.

---

## 5. Fase 3: Limpieza de Frontend React, Código Muerto y Carga Perezosa (Parte 3)

### 5.1 Herramientas y Auditoría de Dependencias
- **Herramientas ejecutadas:** `depcheck`, `tsc --noEmit` y `grep` exhaustivo sobre `src/`, `package.json` y archivos de configuración.
- **Dependencias analizadas y eliminadas:**
  - `@google/genai` (0 usos en el proyecto; desinstalado).
  - `dotenv` (0 usos; Vite utiliza nativamente `import.meta.env`; desinstalado).
  - `express` y `@types/express` (0 usos en el frontend Vite cliente; desinstalados).
  - `tsx` (0 usos; la compilación se efectúa mediante Vite/tsc y el backend en Python; desinstalado).
  - `motion` (0 usos; animaciones resueltas mediante vanilla CSS y Tailwind; desinstalado).
  - `autoprefixer` (0 usos directos; desinstalado).
  - `esbuild` (dependencia redundante de desarrollo; desinstalada).
- **Dependencia retenida con justificación:**
  - `react-is`: Aunque no es importada de forma explícita en el código fuente de usuario, es un requisito transitivo estricto de `recharts/es6/util/ReactUtils.js`. Su ausencia aborta `vite build` en la resolución de chunks de Rollup. Se mantuvo instalada.

### 5.2 Componentes y Archivos de Código Muerto Eliminados
Tras confirmar con `grep` 0 referencias e importaciones en el proyecto:
- `src/components/HUD/MetricsPanel.tsx` (reemplazado por `LiveMetricsPill` en el viewport 3D).
- `src/components/HUD/PolicyPanel.tsx` (reemplazado por drawer de políticas minimalista flotante).
- `src/components/HUD/TimelineController.tsx` (reemplazado por scrubber integrado en `DigitalTwin3DView`).
- `src/components/Modals/AIEngineModal.tsx` (reemplazado por la vista completa de primer nivel `AIEngineView`).
- `src/components/Modals/DatasetManagerModal.tsx` (reemplazado por la vista `DatasetsReportsView`).
- `src/components/Modals/ExportReportsModal.tsx` (reemplazado por la pestaña de exportación en `DatasetsReportsView`).

### 5.3 Limpieza de Configuración (`vite.config.ts` y `tsconfig.json`)
- `vite.config.ts`: Eliminados comentarios y directivas obsoletas heredadas de Google AI Studio (`DISABLE_HMR` y `.system_generated`).
- `tsconfig.json`: Añadida la directiva `"types": ["vite/client"]`, resolviendo de forma canónica los 4 errores de tipado `TS2339` sobre `import.meta.env`.

### 5.4 Mocks y Fuentes de Datos Reales (`api.ts`, `mockData.ts`, `aiEngineMockData.ts`)
- **Datos con endpoint real en backend FastAPI:**
  - Escenarios: Conectados a `/api/v1/simulations/scenarios`.
  - Métricas estructurales: Conectadas a `/api/v1/simulations/metrics`.
  - Datasets oficiales: Conectados a `/api/v1/datasets` y `/api/v1/datasets/active`.
  - Modelos de Machine Learning: Conectados a `/api/v1/ml/models` y `/api/v1/ml/active-model`.
  - Historial de simulaciones: Conectado a `/api/v1/simulations/history`.
- **Tratamiento en desconexión:** Si el servidor backend no responde, la UI captura el error y despliega el aviso `"Backend no disponible"` con opción de reintento; **no se inventan datos ficticios en caso de falla**.
- **Datos sin endpoint:** Renombrados con prefijo `DEMO_` (`DEMO_USERS`, `DEMO_FIRMS`, `DEMO_DATASETS`, `DEMO_COHORTS`, etc.) y marcados con la etiqueta visible `"Datos de demostración"` en la interfaz (`UserManagementModal`, `DatasetsReportsView`, `CrossValidationTab`, `HyperparamsStatsTab`, `CohortProjectionsTab`, `DigitalTwin3DView`).

### 5.5 Carga Perezosa (Lazy Loading) y Memoización del HUD
- **Carga perezosa:** `DigitalTwin3DView` y la librería pesada `Three.js` ahora se cargan dinámicamente mediante `React.lazy` y `React.Suspense` con un componente indicador de carga.
- **Memoización:** Para prevenir re-renderizados costosos en cada tick de la simulación mensual (0 a 120 meses), se envolvieron en `React.memo`:
  - `TopNavigationBar`
  - `LiveMetricsPill`
  - `AgentInspectorModal`
  - `DigitalTwin3DView`

### 5.6 Comparativa del Tamaño del Bundle (Antes vs Después)

| Archivo / Chunk | Tamaño Antes de Parte 3 | Tamaño Después de Parte 3 | Variación neta |
|---|---|---|---|
| **Bundle Inicial JS (`index-*.js`)** | **1,517.81 kB** | **923.48 kB** | **-594.33 kB (-39.2 %)** |
| **Chunk Dinámico 3D (`DigitalTwin3DView-*.js`)** | *(no existía, embebido)* | **595.09 kB** | Separado en carga perezosa |
| **Estilos CSS (`index-*.css`)** | 84.88 kB | 85.69 kB | +0.81 kB (nuevos badges) |
| **HTML Raíz (`index.html`)** | 1.43 kB | 1.43 kB | 0.00 kB |

*Resultado: La carga inicial de la aplicación se redujo en casi 600 kB (~40 %), permitiendo un inicio mucho más rápido y difiriendo Three.js solo a cuando el usuario navega a la vista 3D.*

### 5.7 Verificaciones Finales de Integridad
- `npm run lint` (`tsc --noEmit`): **0 errores**.
- `npm run build` (`vite build`): **0 errores (éxito en 6.02s)**.
- `python -m pytest`: **24/24 pruebas pasadas exitosamente**.
- **Integridad econométrica:** 12/12 archivos CSV en `outputs/` idénticos byte a byte a la línea base.

