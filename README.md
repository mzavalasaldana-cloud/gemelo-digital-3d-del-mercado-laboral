# 🌐 Gemelo Digital 3D del Mercado Laboral y Transición a la Formalidad

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/mzavalasaldana-cloud/gemelo-digital-3d-del-mercado-laboral)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/mzavalasaldana-cloud/gemelo-digital-3d-del-mercado-laboral)

Prototipo interactivo de visualización 3D y simulador de políticas laborales para ilustrar transiciones hacia el empleo formal bajo directrices estadísticas de la OIT (ODS 8).

> [!NOTE]
> **Aviso Metodológico y Datos de Demostración:**
> - Los microdatos incluidos en `data_store/` (`SINTETICO_...csv`) son **conjuntos de datos sintéticos de demostración** generados mediante distribuciones estadísticas en `backend/ml_engine.py`. **No son microdatos censales oficiales.**
> - El modelo econométrico y el artículo científico del proyecto utilizan exclusivamente **tasas macroeconómicas agregadas de ILOSTAT** y parámetros de literatura internacional (p. ej. Addati et al., 2018), no microdatos individuales.
> - La comparativa técnica detallada entre el artículo de investigación y la implementación actual de la plataforma se encuentra documentada en [`docs/DIAGNOSTICO.md`](docs/DIAGNOSTICO.md).

---

## 🏛️ Componentes del Sistema

1. **Frontend Interactivo (React 19 + Vite + Three.js / Tailwind CSS):**
   - Visualización de enjambres 3D (2,500 partículas de trabajadores) con cinemática orbital (sector formal) y movimiento browniano en valles topográficos (sector informal).
   - Panel de control de palancas de política pública (subsidios PyME, reducción de costos de registro, capacitación y fiscalización inteligente).
   - Módulo exploratorio de Machine Learning (EDA, validación cruzada y telemetría de demostración).

2. **Dashboard Ejecutivo (Streamlit):**
   - Cuadros de mando con métricas de Trabajo Decente OIT, índice de Gini y recaudación fiscal.
   - Catálogo de datasets sintéticos y generador de informes descargables en PDF, Excel y HTML.
   - Selector de temas (Modo Claro nativo y Modo Oscuro).

3. **Backend de Inferencia & API (FastAPI + Python 3.12):**
   - Endpoints REST para ingesta de datos, previsualización tabular y análisis exploratorio.
   - Conexión WebSocket para streaming en tiempo real de coordenadas 3D y métricas de simulación con caché en memoria.

4. **Motor de Simulación Compartido (`web_demo/` & `itdt/`):**
   - Módulo `web_demo/simulation.py` que centraliza el cálculo de métricas estructurales conectadas a `itdt.model.ITDTModel`, elevación topográfica y cinemática de agentes.
   - Adaptadores compatibles para FastAPI (`backend/simulation_engine.py`) y Streamlit (`streamlit_app/simulation_engine.py`).

---

## 📁 Estructura del Repositorio

```text
.
├── backend/                  # API REST FastAPI, WebSocket de simulación, motor ML y modelos SQLAlchemy
│   ├── main.py               # Servidor principal FastAPI y endpoints
│   ├── ml_engine.py          # Pipelines de Machine Learning (XGBoost, LightGBM, Random Forest, SHAP)
│   ├── database.py           # Conexión asíncrona a PostgreSQL / SQLite
│   └── models.py             # Modelos de base de datos (SimulationRunModel, DatasetModel)
├── streamlit_app/            # Cuadros de mando ejecutivos en Streamlit
│   ├── app.py                # Punto de entrada de la aplicación Streamlit
│   ├── views/                # Vistas: Dashboard, Gemelo 3D, Motor IA, Datasets, OIT, Copiloto
│   └── utils/                # Generador de reportes (PDF, Excel, HTML) y componentes de UI
├── web_demo/                 # Motor de simulación para web y puente con el modelo canónico
│   └── simulation.py         # SimulationEngine (partículas 3D) y calculate_structural_metrics
├── itdt/                     # Paquete canónico del modelo basado en agentes (SMM Calibrado)
│   ├── model.py              # ITDTModel: agentes trabajadores y firmas con burn-in de 96 meses
│   ├── parameters.py         # COUNTRY_DATABASE y parámetros fijos del artículo
│   ├── metrics.py            # Métricas mensuales, Gini y gradientes distributivos
│   ├── calibrate.py          # Calibración SMM por bisección anidada 9x9
│   ├── experiments.py        # Escenarios A, B1, B2, C, D (R=40 réplicas, bootstrap)
│   ├── loco.py               # Validación Leave-One-Country-Out fuera de muestra
│   └── cli.py                # Orquestador de replicación (make all, make smoke, etc.)
├── src/                      # Frontend interactivo React 19 + Vite + Three.js + Tailwind CSS
│   ├── components/           # Vistas (Dashboard, Gemelo 3D con carga perezosa, Motor IA, Datasets)
│   ├── data/                 # mockData.ts y aiEngineMockData.ts (conectados a API con aviso de desconexión)
│   └── services/             # api.ts (cliente HTTP REST y WebSocket para simulación en vivo)
├── data/                     # Datos oficiales de calibración (data/ilostat_s_F.csv)
├── data_store/               # Almacenamiento local de datasets subidos
├── models_store/             # Artefactos entrenados serializados (XGBoost, LightGBM, Random Forest)
├── outputs/                  # Tablas 2–12 y Figuras 4–7 generadas por el modelo econométrico
├── tests/                    # Suite de 24 pruebas pytest (unitarias, integración y metamórficas)
├── docs/                     # Diagnóstico técnico, tablas del artículo y registro de limpieza
├── requirements.txt          # Requisitos fijados para la aplicación (backend + Streamlit)
├── requirements-itdt.txt     # Requisitos fijados para la replicación del modelo ITDT
├── Makefile                  # Objetivos make para replicación en Linux/macOS
└── make.bat                  # Script de conveniencia para ejecutar make en Windows
```

---

## 🏗️ Arquitectura de Despliegue

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│        Vercel (Frontend)        │       │         Render (Backend)        │
│   React 19 + Vite + Three.js    │ ────> │ FastAPI + Python 3.12 + Uvicorn │
│  https://<tu-app>.vercel.app    │ <──── │ https://<tu-api>.onrender.com   │
└─────────────────────────────────┘       └─────────────────────────────────┘
                │                                         │
          REST / WebSockets                         REST / WebSockets
                │                                         │
                └─────────────────┬───────────────────────┘
                                  ▼
                 ┌─────────────────────────────────┐
                 │       Streamlit Cloud           │
                 │      (Dashboard Ejecutivo)      │
                 │     streamlit_app/app.py        │
                 └─────────────────────────────────┘
```

---

## 🚀 Despliegue Rápido

### 1. Backend en Render
1. Haz clic en el botón **Deploy to Render**:
   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/mzavalasaldana-cloud/gemelo-digital-3d-del-mercado-laboral)
2. Render detectará automáticamente [`render.yaml`](./render.yaml).
3. Una vez completado, copia la URL asignada (ejemplo: `https://gemelo-laboral-backend.onrender.com`).

### 2. Frontend en Vercel
1. Haz clic en el botón **Deploy with Vercel**:
   [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/mzavalasaldana-cloud/gemelo-digital-3d-del-mercado-laboral)
2. Configura la variable de entorno:
   - **`VITE_API_URL`**: URL pública del backend en Render (sin barra inclinada al final).
3. Haz clic en **Deploy**.

### 3. Dashboard Streamlit en Streamlit Cloud
1. Accede a [share.streamlit.io](https://share.streamlit.io/).
2. Conecta el repositorio (`gemelo-digital-3d-del-mercado-laboral`) y la rama deseada (`main` o `limpieza`).
3. Especifica como archivo principal: `app.py`.

---

## 💻 Ejecución Local

### Prerrequisitos
- Node.js 18+ y npm
- Python 3.12+ (o 3.10+)

### 1. Iniciar Backend (FastAPI)
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
# Documentación interactiva Swagger: http://localhost:8000/docs
```

### 2. Iniciar Frontend (React + Vite)
```bash
npm install
npm run dev
# Aplicación web disponible en: http://localhost:3000
```

### 3. Iniciar Dashboard Streamlit
```bash
streamlit run app.py
# Dashboard disponible en: http://localhost:8501
```

### 4. Ejecutar Replicación del Modelo
```bash
make all      # o bien: python -m itdt.cli all
```

---

## 🔬 Paquete de Replicación del Artículo

Este repositorio incluye la implementación canónica y el paquete de replicación computacional para el artículo científico:  
***ITDT: Un gemelo digital multi-agente calibrado con ILOSTAT para evaluar políticas de formalización con perspectiva de género en cuatro economías del Sur Global***.

Todos los resultados, tablas (Tablas 2–12) y figuras (Figuras 4–7) se generan de forma determinista y reproducible a partir de la simulación basada en agentes implementada en `itdt/`.

### 📋 Prerrequisitos
- **Python:** 3.10 o superior (recomendado: 3.12 / 3.14).
- **Dependencias:** `pip install -r requirements-itdt.txt` (incluye `numpy`, `scipy`, `pandas`, `matplotlib`, `tabulate` y `pytest`).
- **GNU Make:** Opcional (si no dispone de `make`, ejecute directamente `python -m itdt.cli <objetivo>`).
- **Docker:** Opcional (imagen lista para replicación en contenedores: `python:3.12.9-slim`).

---

### 🚀 Comandos de Replicación

Puede ejecutar cualquier etapa de forma aislada mediante `make <objetivo>` o `python -m itdt.cli <objetivo>`:

```bash
# 1. Prueba rápida de humo y suite de pruebas unitarias (< 1 minuto)
make smoke

# 2. Calibración SMM por bisección anidada (9x9) de los 4 países
make calibrate

# 3. Estimación de errores estándar de calibración (10 conjuntos de semillas independientes)
make calib_se

# 4. Validación fuera de muestra Leave-One-Country-Out (LOCO)
make loco

# 5. Modelos estructurales de referencia dentro de muestra (E1–E4)
make baselines

# 6. Barrido del multiplicador de sanciones (1.0 a 4.0 bajo B1)
make sweep

# 7. Escenarios de política (A, B1, B2, C, D; R=40 réplicas; bootstrap B=4000)
make scenarios

# 8. Descomposición por ablación de B2 frente a A con recalibración de variantes
make mechanism

# 9. Análisis de sensibilidad (+-20%), especificaciones CES y choque exógeno
make sensitivity

# 10. Benchmarking de costo computacional (NW = 3k, 6k, 12k, 24k)
make cost

# 11. REPLICACIÓN COMPLETA DESDE CERO (regenera outputs/ y mide tiempo total)
make all
```

#### Ejecución con Docker:
```bash
# Construir la imagen
docker build -t itdt .

# Ejecutar la prueba de humo rápida
docker run --rm itdt make smoke

# Ejecutar la replicación completa y extraer los artefactos generados a outputs/
docker run --rm -v "$(pwd)/outputs:/app/outputs" itdt make all
```

#### Ejecución de la Suite de Pruebas (Pytest):
```bash
python -m pytest tests/test_itdt_canonical.py tests/test_itdt.py -v
```
Incluye pruebas unitarias con valores calculados a mano ($U_F$, $U_I$, $\Pi_F$, $\Pi_I$, $DCC$, $P_{aud}$, Metropolis) y pruebas metamórficas de simetría de género sin cuidados, monotonía de sanciones e invarianza de semilla.

---

### 📊 Mapeo de Objetivos Make a Tablas y Figuras del Artículo

| Objetivo `make` | Descripción Metodológica | Salida Generada en `outputs/` | Tabla / Figura del Artículo | Tiempo Estimado |
| :--- | :--- | :--- | :---: | :---: |
| `make smoke` | Pruebas unitarias, metamórficas y corrida rápida de integración | Reporte pytest + log de integración | Validación técnica | < 30 s |
| `make calibrate` | Calibración SMM basal ($S=6$ semillas, bisección anidada $9\times 9 = 81$ evals.) | `table2_calibration.*`<br>`table11_equity.*`<br>`figure4_calibration.png` | **Tabla 2**, **Tabla 11** y **Figura 4** | ~1.5 min |
| `make calib_se` | Errores estándar Monte Carlo mediante 10 calibraciones independientes | `calibration_estimates.json`<br>`table2_calibration.*` | **Tabla 2** (columnas EE) | ~4.0 min |
| `make loco` | Validación fuera de muestra LOCO ($\gamma_0$ común en rejilla $[0.0, 1.2]$) | `table3_loco.*`<br>`loco_insumos.md`<br>`loco_results.json` | **Tabla 3** y Documento de insumos | ~1.0 min |
| `make baselines` | Ajuste dentro de muestra de modelos estructurales de referencia | `table4_baselines.*` | **Tabla 4** (E1, E2, E3, E4, ITDT) | ~15 s |
| `make sweep` | Barrido de intensidad de sanción (1.0 a 4.0 bajo B1) y umbral no lineal | `sanctions_sweep_data.csv`<br>`figure5_sanctions_sweep.png` | **Figura 5** | ~1.5 min |
| `make scenarios` | Escenarios A, B1, B2, C, D ($R=40$ réplicas) + Bootstrap ($B=4000$) | `table5_levels.*`<br>`table6_changes.*`<br>`table7_contrasts.*`<br>`figure6_trajectories.png`<br>`figure7_policy_effects.png`<br>`policy_experiments_results.json` | **Tabla 5**, **Tabla 6**, **Tabla 7**, **Figura 6** y **Figura 7** | ~1.5 min |
| `make mechanism` | Ablación de B2 frente a A (cuidado y DCC) con recalibración de cada variante | `table8_ablation.*` | **Tabla 8** | ~2.5 min |
| `make sensitivity` | Sensibilidad $\pm 20\%$ (9 parámetros), robustez CES ($\sigma \in \{0.5, 1.5\}$) y choque | `table9_sensitivity.*` | **Tabla 9** | ~3.5 min |
| `make cost` | Costo computacional por réplica ($N_W \in \{3\,000, 6\,000, 12\,000, 24\,000\}$) | `table10_cost.*` | **Tabla 10** | ~10 s |
| `make all` | **Pipeline integral:** regenera `outputs/` desde cero y reporta tiempo | **Todas las Tablas (2–12), Figuras (4–7) y JSONs** | **Replicación total** | ~18 min |

---

## 📚 Documentación y Diagnóstico Científico
- Consulta [`docs/DIAGNOSTICO.md`](docs/DIAGNOSTICO.md) para el inventario completo de ecuaciones del artículo científico vs. la arquitectura del código.
- Consulta [`outputs/loco_insumos.md`](outputs/loco_insumos.md) para la auditoría de aislamiento de información en la validación fuera de muestra.
- Consulta [`LICENSE`](LICENSE) para los términos de la Licencia MIT.
