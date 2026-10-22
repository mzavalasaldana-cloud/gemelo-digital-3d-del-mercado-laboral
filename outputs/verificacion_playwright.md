# Reporte Oficial de Verificación Automática con Playwright

- **Fecha y hora:** 2026-10-22 10:27:18
- **Entorno:** Playwright Chromium (modo interactivo/renderizado 3D real y visual de imágenes)
- **Resultado Global:** APROBADO

## 1. Verificación del Gemelo Digital 3D (window.__itdtDebug)

| Escenario | Mes | Inf. Modelo | Partículas Inf. | Partículas Form. | Total Partículas | Inf. Dibujada (%) | Δ (p.p.) | Torres Form. (D / E) | Partículas > 0 | Estado |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A** | Mes 1 | 87.24% | 2181 | 319 | 2500 | 87.24% | **+0.00** | 1 / 1 | Sí | **PASS** |
| **A** | Mes 60 | 87.36% | 2184 | 316 | 2500 | 87.36% | **+0.00** | 1 / 1 | Sí | **PASS** |
| **A** | Mes 120 | 87.14% | 2179 | 321 | 2500 | 87.16% | **+0.02** | 1 / 1 | Sí | **PASS** |
| **B2** | Mes 1 | 80.54% | 2014 | 486 | 2500 | 80.56% | **+0.02** | 1 / 1 | Sí | **PASS** |
| **B2** | Mes 60 | 64.23% | 1606 | 894 | 2500 | 64.24% | **+0.01** | 2 / 2 | Sí | **PASS** |
| **B2** | Mes 120 | 49.17% | 1229 | 1271 | 2500 | 49.16% | **+0.01** | 4 / 4 | Sí | **PASS** |

## 2. Verificación del Gráfico de Trayectoria en Dashboard (120 Puntos y DOM SVG)

| País | Escenario | Puntos Memoria | Puntos DOM SVG | Esperado | Dif. Máxima (p.p.) | Mes 1 (Dash / JSON) | Mes 60 (Dash / JSON) | Mes 120 (Dash / JSON) | Estado |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **KENYA** | A | 120 | 120 | 120 | **0.000** | 87.24% / 87.24% | 87.36% / 87.36% | 87.14% / 87.14% | **PASS** |
| **KENYA** | B2 | 120 | 120 | 120 | **0.000** | 80.54% / 80.54% | 64.23% / 64.23% | 49.17% / 49.17% | **PASS** |

## 3. Prueba Visual Automática de Imágenes PNG (No Vacías ni Uniformes)

| Archivo Captura | Tipo | Dimensiones | Desv. Estándar Píxeles | Mínimo Requerido | Colores Distintos | Mínimo Requerido | Estado Visual |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `fig_dashboard_kenia_escenarioA.png` | dashboard | 4800x2700 | **31.43** | >= 12.0 | **5628** | >= 150 | **PASS** |
| `fig_dashboard_kenia_escenarioD.png` | dashboard | 4800x2700 | **31.58** | >= 12.0 | **7210** | >= 150 | **PASS** |
| `fig_gemelo3d_kenia_escenarioA_m60.png` | 3d | 4800x2700 | **35.90** | >= 12.0 | **46336** | >= 150 | **PASS** |
| `fig_gemelo3d_kenia_escenarioA.png` | 3d | 4800x2700 | **36.07** | >= 12.0 | **48001** | >= 150 | **PASS** |
| `fig_gemelo3d_kenia_escenarioB2_m60.png` | 3d | 4800x2700 | **37.10** | >= 12.0 | **47224** | >= 150 | **PASS** |
| `fig_gemelo3d_kenia_escenarioB2.png` | 3d | 4800x2700 | **39.65** | >= 12.0 | **51199** | >= 150 | **PASS** |
