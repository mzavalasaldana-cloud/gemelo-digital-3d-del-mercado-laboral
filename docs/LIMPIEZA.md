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
