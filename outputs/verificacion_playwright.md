# Reporte Oficial de Verificación Automática con Playwright

- **Fecha y hora:** 2026-10-22 00:24:02
- **Entorno:** Playwright Chromium (modo interactivo/renderizado 3D real)
- **Resultado Global:** APROBADO

## 1. Verificación del Gemelo Digital 3D (window.__itdtDebug)

| Escenario | Mes | Inf. Modelo | Partículas Inf. | Partículas Form. | Total Partículas | Inf. Dibujada (%) | Δ (p.p.) | Torres Form. (D / E) | Partículas > 0 | Estado |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A** | Mes 1 | 86.26% | 2157 | 343 | 2500 | 86.28% | **+0.02** | 1 / 1 | Sí | **PASS** |
| **A** | Mes 60 | 86.85% | 2171 | 329 | 2500 | 86.84% | **+0.01** | 1 / 1 | Sí | **PASS** |
| **A** | Mes 120 | 85.90% | 2148 | 352 | 2500 | 85.92% | **+0.02** | 1 / 1 | Sí | **PASS** |
| **B2** | Mes 1 | 79.95% | 1999 | 501 | 2500 | 79.96% | **+0.01** | 1 / 1 | Sí | **PASS** |
| **B2** | Mes 60 | 66.38% | 1659 | 841 | 2500 | 66.36% | **+0.02** | 2 / 2 | Sí | **PASS** |
| **B2** | Mes 120 | 50.10% | 1253 | 1247 | 2500 | 50.12% | **+0.02** | 3 / 3 | Sí | **PASS** |

## 2. Verificación del Gráfico de Trayectoria en Dashboard (120 Puntos)

| País | Escenario | Puntos Obtenidos | Esperado | Dif. Máxima (p.p.) | Mes 1 (Dash / JSON) | Mes 60 (Dash / JSON) | Mes 120 (Dash / JSON) | Estado |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **KENYA** | A | 120 | 120 | **0.000** | 86.26% / 86.26% | 86.85% / 86.85% | 85.90% / 85.90% | **PASS** |
| **KENYA** | B2 | 120 | 120 | **0.000** | 79.95% / 79.95% | 66.38% / 66.38% | 50.10% / 50.10% | **PASS** |
