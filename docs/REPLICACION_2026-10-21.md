# Reporte de Replicación y Validación con Datos Reales (2026-10-21)

Este informe documenta la replicación integral del modelo **ITDT** (*Informality Twin with Demographic Transitions*), la eliminación sistemática de todo dato sintético/inventado en el frontend y backend, la validación empírica frente a microdatos agregados de ILOSTAT (Tabla 13) y la captura de figuras en ultra-alta resolución para el manuscrito académico.

---

## 1. Entorno de Ejecución y Tiempos

- **Sistema Operativo:** Windows 11 Home / AMD64 (`AMD64 Family 23 Model 96 Stepping 1, AuthenticAMD`)
- **Procesador (CPU):** AMD Ryzen (arquitectura x86_64, multi-hilo)
- **Entorno Virtual:** `.venv` con Python 3.13.14
- **Librerías Clave:**
  - `numpy`: 2.2.6
  - `scipy`: 1.15.3
  - `pandas`: 2.3.3
  - `scikit-learn`: 1.7.2
  - `pytest`: 8.3.5
  - `fastapi`: 0.128.0
  - `playwright`: 1.58.0
  - `pillow (PIL)`: 13.0.0
  - `streamlit`: 1.54.0
  - `vite`: 6.4.3
- **Tiempo Total de Ejecución de `make all`:** **1,312.78 segundos** (~21 minutos 52 segundos), registrado fielmente en `outputs/log_make_all.txt`.

---

## 2. Resultado de las Pruebas de Software

1. **Pruebas Canónicas y Metamórficas (`pytest`):**
   - Comando: `python -m pytest tests/test_itdt_canonical.py tests/test_itdt.py -v`
   - Resultado: **15 pruebas superadas exitosamente (100 % pass)** en 1.43 segundos.
   - Componentes validados:
     - Calibración y simulación canónica para Kenia, Nigeria, India y Bangladés.
     - Reproducibilidad estricta con semillas fijas.
     - Pruebas unitarias: funciones de utilidad, beneficios formales/informales, costos de cumplimiento digital (DCC), probabilidad de auditoría y regla de metrópolis.
     - Pruebas metamórficas: monotonicidad de sanciones, determinismo de semillas, invarianza ante $\phi_1 = 0$, y neutralidad de género cuando el cuidado es nulo ($\gamma_0 = 0$).

2. **Prueba de Humo Rápida (`make smoke`):**
   - Comando: `cmd /c make.bat smoke`
   - Resultado: **10/10 pruebas pasadas** y réplica de prueba rápida (12 meses) ejecutada en **1.75 segundos**.

---

## 3. Descarga y Cobertura de Microdatos Agregados de ILOSTAT

A través del script automatizado `scripts/fetch_ilostat_gradientes.py`, se consultó la API SDMX oficial de ILOSTAT (`https://sdmx.ilo.org/rest/data/ILO,DF_...`), descargando los indicadores de validación externa:
1. `EMP_NIFL_SEX_EDU_RT`: Tasa de informalidad por sexo y nivel educativo agregado.
2. `EMP_NIFL_SEX_GEO_RT`: Tasa de informalidad por sexo y área geográfica (rural/urbana).

### Resumen de Descarga:
- **Archivo resultante limpio:** `data/ilostat_gradientes.csv` (96 observaciones reales).
- **Respuestas crudas preservadas:** `data/raw/ilostat_*_raw.json` y `data/raw/ilostat_gradientes_manifest.json`.

### Datos Descargados y Combinaciones Faltantes Reportadas:
| País | Indicador | Año Obtenido | Cobertura | Estado / Combinaciones Faltantes |
|:---|:---|:---:|:---|:---|
| **Kenia (KEN)** | `EMP_NIFL_SEX_EDU_RT` | 2019 | Básica, Media, Superior por Sexo | Completa (año de calibración exacto) |
| **Kenia (KEN)** | `EMP_NIFL_SEX_GEO_RT` | 2019 | Rural, Urbana por Sexo | Completa |
| **Nigeria (NGA)** | `EMP_NIFL_SEX_EDU_RT` | 2022 | Básica, Media, Superior por Sexo | Disponible más cercano (2024 sólo tiene total nacional) |
| **Nigeria (NGA)** | `EMP_NIFL_SEX_GEO_RT` | 2022 | Rural, Urbana por Sexo | Disponible más cercano |
| **India (IND)** | `EMP_NIFL_SEX_EDU_RT` | 2012 | Básica, Media, Superior por Sexo | Serie anual armonizada oficial más reciente en ILOSTAT |
| **India (IND)** | `EMP_NIFL_SEX_GEO_RT` | 2012 | Rural, Urbana por Sexo | Serie anual armonizada oficial más reciente en ILOSTAT |
| **Bangladés (BGD)** | `EMP_NIFL_SEX_EDU_RT` | 2022 | Básica, Media, Superior por Sexo | Disponible en LFS 2022 |
| **Bangladés (BGD)** | `EMP_NIFL_SEX_GEO_RT` | 2017 | Rural, Urbana por Sexo | **Faltante en 2022–2023**: ILOSTAT no reporta desglose rural/urbano en la ronda 2022-2023, tomándose 2017 como última ronda oficial con cobertura geográfica completa. |

*Nota conforme a la Regla 3:* Ninguna combinación ausente fue rellenada ni imputada; se mantienen exclusivamente las series empíricas oficiales descargadas.

---

## 4. Comparación con la Versión Previa de Salidas (`outputs/`)

Se realizó una comparación directa contra la versión confirmada en el repositorio (`git show HEAD:outputs/...`):

| Componente | Parámetro / Métrica | Versión Actual | Versión Previa (HEAD) | Naturaleza de la Diferencia |
|:---|:---|:---:|:---:|:---:|
| **Calibración KEN** | $\phi_0$ | 3.5859375 | 3.5859375 | **Exacta (0 diff)** |
| **Calibración KEN** | $\gamma_0$ | 0.4599609 | 0.4599609 | **Exacta (0 diff)** |
| **Calibración NGA** | $\phi_0$ | 11.2500000 | 11.2500000 | **Exacta (0 diff)** |
| **Calibración NGA** | $\gamma_0$ | 0.6210938 | 0.6210938 | **Exacta (0 diff)** |
| **Calibración IND** | $\phi_0$ | 5.8593750 | 5.8593750 | **Exacta (0 diff)** |
| **Calibración IND** | $\gamma_0$ | 0.4423828 | 0.4423828 | **Exacta (0 diff)** |
| **Calibración BGD** | $\phi_0$ | 2.2500000 | 2.2500000 | **Exacta (0 diff)** |
| **Calibración BGD** | $\gamma_0$ | 0.7617188 | 0.7617188 | **Exacta (0 diff)** |
| **Validación LOCO** | MAE ITDT global | 4.20803 pp | 4.20803 pp | **Exacta (0 diff)** |
| **Tabla 5 (Niveles)** | Todas las celdas | Ver Tabla 5 | Ver Tabla 5 | **Exacta (0 diff)** |
| **Tabla 6 (Cambios)** | Todas las celdas | Ver Tabla 6 | Ver Tabla 6 | **Exacta (0 diff)** |
| **Tabla 8 (Ablación)**| Todas las celdas | Ver Tabla 8 | Ver Tabla 8 | **Exacta (0 diff)** |
| **Tabla 10 (Costo)** | Todas las celdas | Ver Tabla 10 | Ver Tabla 10 | **Exacta (0 diff)** |

### Cifras Clave del Modelo (Meses 109–120):
- **Cierres de Empresas en B2:** **52.89 % anual** (un incremento neto de **+52.86 p.p./año** respecto al Status Quo A).
- **Cierres de Empresas en D:** **20.68 % anual** (reducción notable del costo colateral de salida empresarial frente a B2, gracias a la compensación por subsidio al DCC).
- **Variación de Brecha de Género en B2 ($\Delta \text{Brecha}_{B2 - A}$):** **+29.38 p.p.** (la brecha pasa de 8.51 p.p. en A a 37.89 p.p. en B2, evidenciando el efecto adverso no intencionado de la fiscalización ciega al género).
- **Variación de Brecha de Género en D ($\Delta \text{Brecha}_{D - A}$):** **-6.85 p.p.** (la brecha desciende a 1.67 p.p. en el escenario integrado con red de cuidados).

---

## 5. Resultados de la Validación de Gradientes (Tabla 13)

Generada mediante `scripts/validar_gradientes_ilostat.py` sin alterar el núcleo de `itdt/`:

| País | Dimensión | Categoría | Año Obs. | Tasa Obs. ILOSTAT (%) | Tasa Sim. ITDT (%) | Error Abs. (pp) |
|:---|:---|:---|:---:|:---:|:---:|:---:|
| **Kenia** | Educación | Básica ($e = 0$) | 2019 | 88.77 | 94.77 | 6.00 |
| **Kenia** | Educación | Media ($e = 1$) | 2019 | 80.84 | 83.87 | 3.03 |
| **Kenia** | Educación | Superior ($e = 2$) | 2019 | 31.71 | 66.05 | 34.34 |
| **Kenia** | Zona | Rural | 2019 | 93.08 | 89.48 | 3.60 |
| **Kenia** | Zona | Urbana | 2019 | 73.82 | 81.09 | 7.27 |
| **Nigeria** | Educación | Básica ($e = 0$) | 2022 | 98.05 | 98.75 | 0.70 |
| **Nigeria** | Educación | Media ($e = 1$) | 2022 | 93.74 | 94.58 | 0.84 |
| **Nigeria** | Educación | Superior ($e = 2$) | 2022 | 73.38 | 84.52 | 11.14 |
| **Nigeria** | Zona | Rural | 2022 | 97.94 | 96.47 | 1.47 |
| **Nigeria** | Zona | Urbana | 2022 | 90.35 | 92.68 | 2.33 |
| **India** | Educación | Básica ($e = 0$) | 2012 | 90.61 | 96.93 | 6.32 |
| **India** | Educación | Media ($e = 1$) | 2012 | 73.40 | 88.59 | 15.19 |
| **India** | Educación | Superior ($e = 2$) | 2012 | 49.03 | 71.55 | 22.52 |
| **India** | Zona | Rural | 2012 | 92.74 | 92.47 | 0.27 |
| **India** | Zona | Urbana | 2012 | 72.51 | 85.82 | 13.31 |
| **Bangladés** | Educación | Básica ($e = 0$) | 2022 | 85.87 | 92.60 | 6.73 |
| **Bangladés** | Educación | Media ($e = 1$) | 2022 | 71.85 | 80.98 | 9.14 |
| **Bangladés** | Educación | Superior ($e = 2$) | 2022 | 53.45 | 66.40 | 12.95 |
| **Bangladés** | Zona | Rural | 2017 | 96.60 | 87.63 | 8.97 |
| **Bangladés** | Zona | Urbana | 2017 | 89.79 | 78.65 | 11.14 |

### Error Medio Absoluto (MAE) por País:
- **Kenia:** 10.85 pp
- **Nigeria:** 3.30 pp
- **India:** 11.52 pp
- **Bangladés:** 9.78 pp
- **MAE Global Ponderado (4 países):** **8.86 pp**

---

## 6. Saneamiento de la Aplicación Web y Fuentes Reales Conectadas

En estricto cumplimiento del **Principio General**, se depuró toda la aplicación (React frontend, FastAPI backend y Streamlit):

### Elementos Archivados y Desactivados:
1. `data_store/SINTETICO_*.csv` $\rightarrow$ movidos a `data_store/_archivado/`.
2. `models_store/*.joblib` $\rightarrow$ movidos a `models_store/_archivado/`.
3. `src/data/aiEngineMockData.ts` y `mock_data.py` $\rightarrow$ respaldados en `_archivado/`; sus variables exportadas en uso fueron vaciadas a arreglos vacíos o `null`.
4. `backend/ml_engine.py`: `generate_country_preset_dataset()` fue permanentemente desactivada con excepción explícita para evitar toda re-creación sintética.

### Indicadores Eliminados y Nuevas Fuentes Reales:
| Elemento Anterior en la UI | Razón de Eliminación | Nueva Representación y Fuente Real |
|:---|:---|:---|
| **Índice de Trabajo Decente** | Ponderación heurística sin base empírica oficial. | **Eliminado completamente**. Se sustituyó por la ventana modal `ILODecentWorkModal` con indicadores empíricos reales de ILOSTAT (`EMP_NIFL_SEX_RT`, `EMP_NIFL_SEX_EDU_RT`, `EMP_NIFL_SEX_GEO_RT`). |
| **Salarios en USD (`avgFormalWageUSD`)** | El modelo es abstracto y no modela tasas cambiarias ni paridad de poder adquisitivo. | **Eliminado de KPIs y gráficas**. Se enfoca en tasas de formalidad y ratios relativos de productividad. |
| **Costo de Política en Millones USD** | Cifras presupuestarias inventadas sin sustento fiscal. | **Eliminado de la interfaz**. |
| **Recaudación en Millones USD** | La recaudación del modelo no está denominada en dólares. | Se presenta estrictamente en **"Unidades del Modelo"** (`unidades del modelo`). |
| **Métricas del Motor IA (F1, ROC, AUC)** | Entrenadas sobre microdatos sintéticos. | **Estado vacío implementado**: Muestra `"Sin microdatos reales cargados"`. Si no existen archivos en `data/microdatos_reales/<pais>/`, no se calcula ni proyecta ninguna métrica. |
| **Valores por defecto en Copiloto** | El asistente inventaba indicadores cuando el contexto estaba vacío. | Si no hay datos, el copiloto responde explícitamente: `"Sin datos reales disponibles"`. |
| **Etiqueta "Datos de demostración"** | Obsoleta una vez conectado a salidas calibradas. | Removida de todas las pestañas analíticas. En el login institucional se rotula como `"Usuarios de prueba"` (excepción c). |

---

## 7. Catálogo de Capturas en Ultra-Alta Resolución (4K) — Rehechas y Validadas

Todas las capturas anteriores fueron archivadas en `outputs/capturas/_archivado/`. Las nuevas imágenes fueron tomadas con Playwright en Chromium (modo ventana visible `headless=False`, viewport 1600x900 con `device_scale_factor = 3` $\rightarrow$ **4800 x 2700 px**, tema claro, servidores backend y frontend activos, y verificación estricta en el DOM de ausencia del banner de error "Backend no disponible"):

| Archivo | Dimensiones (px) | Tamaño (MB) | Escenario / Vista | Mes | Cifras Clave Mostradas en la Captura |
|:---|:---:|:---:|:---:|:---:|:---|
| `fig_dashboard_kenia_escenarioA.png` | 4800 x 2700 | 0.77 MB | Dashboard Kenia | **Mes 120** | **Tasa Informalidad: 86.1 %** (Base: 86.49%, −0.4%)<br>Gini: **0.288**<br>Recaudación: **+1381.0 u.m.** (Sociedades +1194.8, Seg. Social +186.2)<br>Brecha Género: **+7.20 pp** (Mujeres 89.9%, Hombres 82.7%) |
| `fig_dashboard_kenia_escenarioD.png` | 4800 x 2700 | 0.80 MB | Dashboard Kenia | **Mes 120** | **Tasa Informalidad: 56.8 %** (Base: 86.49%, −29.7%)<br>Gini: **0.298**<br>Recaudación: **+3259.1 u.m.** (Sociedades +2816.3, Seg. Social +442.8)<br>Brecha Género: **+1.10 pp** (Mujeres 57.4%, Hombres 56.3%) |
| `fig_gemelo3d_kenia_escenarioA_m60.png` | 4800 x 2700 | 3.77 MB | Gemelo 3D Kenia | **Mes 60** | Control: **«Mes 60 - Enero 2029»**<br>Informalidad: **86.3 %**<br>Gini: **0.288**<br>Brecha Género: **+7.1 pp** |
| `fig_gemelo3d_kenia_escenarioA.png` | 4800 x 2700 | 2.60 MB | Gemelo 3D Kenia | **Mes 120** | Control: **«Mes 120 - Diciembre 2033»**<br>Informalidad: **86.1 %**<br>Gini: **0.288**<br>Brecha Género: **+7.2 pp** |
| `fig_gemelo3d_kenia_escenarioB2_m60.png` | 4800 x 2700 | 3.80 MB | Gemelo 3D Kenia | **Mes 60** | Control: **«Mes 60 - Enero 2029»**<br>Informalidad: **67.1 %**<br>Gini: **0.289**<br>Brecha Género: **+21.0 pp** |
| `fig_gemelo3d_kenia_escenarioB2.png` | 4800 x 2700 | 2.57 MB | Gemelo 3D Kenia | **Mes 120** | Control: **«Mes 120 - Diciembre 2033»**<br>Informalidad: **51.6 %**<br>Gini: **0.291**<br>Brecha Género: **+32.2 pp** |

Todas las imágenes fueron validadas mediante PIL cumpliendo estrictamente con el requisito de anchura mínima ($\ge 3840\text{ px}$).

---

## 8. Verificación Automática App vs Modelo Calibrado (`verificar_app_vs_modelo.py`)

Se ejecutó la prueba de congruencia econométrica automatizada en `scripts/verificar_app_vs_modelo.py` que consulta la API FastAPI en vivo (`http://127.0.0.1:8000/api/v1/simulation/metrics`) y compara las respuestas frente a las réplicas oficiales de `outputs/policy_experiments_results.json` para Kenia en el mes 120 de la política:

| Escenario | Etiqueta | Oficial Modelo (%) | Respuesta API (%) | Diferencia (p.p.) | Tolerancia | Estado |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **A** | Status Quo (Inercial) | 86.13 % | 86.13 % | +0.00 p.p. | ≤ 0.50 p.p. | **APROBADO** |
| **B1** | GovTech Moderado | 86.18 % | 86.18 % | +0.00 p.p. | ≤ 0.50 p.p. | **APROBADO** |
| **B2** | GovTech Intensivo (Sanciones 3×) | 51.58 % | 51.58 % | +0.00 p.p. | ≤ 0.50 p.p. | **APROBADO** |
| **C** | Red de Cuidados (−60% cuidado) | 85.00 % | 85.00 % | +0.00 p.p. | ≤ 0.50 p.p. | **APROBADO** |
| **D** | Paquete Integrado (B2 + C + DCC) | 56.82 % | 56.82 % | +0.00 p.p. | ≤ 0.50 p.p. | **APROBADO** |

### Cuadre de Componentes de Recaudación Fiscal:
En todos los escenarios, la suma contable de componentes coincide exactamente con la recaudación total:
$$\text{Recaudación Total} = \text{Impuesto de Sociedades } (\tau_C Y_F) + \text{Contribuciones de Seguridad Social } (\tau_W \omega_F L_F)$$
- Escenario A: $1194.83 + 186.22 = 1381.05\text{ u.m.}$ (**Cuadre Exacto**)
- Escenario B1: $1193.95 + 184.23 = 1378.18\text{ u.m.}$ (**Cuadre Exacto**)
- Escenario B2: $3453.13 + 393.54 = 3846.67\text{ u.m.}$ (**Cuadre Exacto**)
- Escenario C: $1311.81 + 203.84 = 1515.65\text{ u.m.}$ (**Cuadre Exacto**)
- Escenario D: $2816.32 + 442.78 = 3259.10\text{ u.m.}$ (**Cuadre Exacto**)

---

## 9. Fuente de Cada Indicador Visible en el Dashboard

| Indicador Visible en Dashboard | Unidad / Formato | Fuente Primaria Oficial | Justificación Metodológica |
|:---|:---:|:---|:---|
| **Tasa de Informalidad Global** | Porcentaje (%) | Modelo calibrado `ITDTModel` (`outputs/policy_experiments_results.json`) / Base ILOSTAT (`data/ilostat_s_F.csv`). | Generado por el equilibrio de decisiones individuales de los 6 000 agentes del modelo según costo de digitalización $\phi_i$, productividad $h_i$ y sanción esperada. |
| **Informalidad por Sexo (Mujeres / Hombres)** | Porcentaje (%) | Modelo calibrado `ITDTModel` y serie histórica real de ILOSTAT (`data/ilostat_series_historicas.csv`). | Emerge de la calibración con el parámetro de asimetría de cuidado no remunerado $\gamma_0$ y datos empíricos de ILOSTAT SDMX. |
| **Brecha de Género** | Puntos porcentuales (pp) | Diferencia neta $s_{\text{informal}, F} - s_{\text{informal}, M}$ de `ITDTModel`. | Medición canónica de la asimetría de informalidad femenina vs. masculina. |
| **Índice de Desigualdad de Gini** | Rango 0–1 | Distribución de ingresos netos mensuales de los agentes de `ITDTModel` (`outputs/policy_experiments_results.json`). | Calculado sobre salarios de trabajadores formales ($\omega_F h_i$), informales ($\omega_I h_i$) y beneficios netos de firmas ($\pi_j$). |
| **Recaudación Fiscal Total** | Unidades del modelo (u.m.) | Sector fiscal endógeno de `ITDTModel`. | Ingresos fiscales agregados recaudados de empresas y trabajadores formales registrados. |
| **Impuesto de Sociedades** | Unidades del modelo (u.m.) | Componente tributario empresarial de `ITDTModel`: $\tau_C \sum_{j \in \mathcal{F}} Y_j$. | Tributación formal sobre la producción formal neta. |
| **Seguridad Social (Contribuciones)** | Unidades del modelo (u.m.) | Componente tributario laboral de `ITDTModel`: $\tau_W \sum_{i \in \mathcal{W}_F} \omega_F h_i$. | Aportes previsionales y de salud del empleo formal. |
| **Serie Histórica ILOSTAT** | Porcentaje (%) anual por sexo | API oficial SDMX de ILOSTAT (`EMP_NIFL_SEX_RT`). | Datos reales sin interpolar para Kenia (2019: Mujeres 90.19%, Hombres 83.13%). |
| **Trayectoria Simulada ITDT** | Mes a mes (0 a 120) | Serie mensual promedio de réplicas de `ITDTModel` (`outputs/policy_experiments_results.json`). | Evolución dinámica mensual de la política pública bajo los escenarios A, B1, B2, C y D. |
| **Agentes Visualizados (2 500)** | Conteo de partículas | Proyección cinemática de la población $N_W = 6\,000$ de `ITDTModel`. | Las partículas reflejan espacialmente la proporción exacta de agentes formales e informales del modelo (excepción permitida b). |
| **Empresas Visualizadas (10 firmas)** | Coordenadas y atributos | Empresas generadas por `ITDTModel` (`L_j, Y_j, A_j`, formal/informal). | Excluye nombres ficticios; su tamaño y color reflejan producción real $Y_j$ y estatus formal/informal. |

