# Comparación Exhaustiva: Resultados de Replicación ITDT vs. Artículo Científico

**Fecha de ejecución:** Octubre 2026  
**Rama Git:** `itdt-articulo`  
**Referencia:** *ITDT: Un gemelo digital multi-agente calibrado con ILOSTAT para evaluar políticas de formalización con perspectiva de género en cuatro economías del Sur Global*  
**Principio metodológico:** Todas las cifras obtenidas provienen de la simulación computacional ejecutada desde cero mediante `make all` (`itdt.cli all`). Cuando una cifra difiere de la reportada en el artículo y no se conoce con certeza técnica demostrada el motivo exacto, se clasifica rigurosamente como «diferencia no explicada», sin atribuir al artículo métodos o entornos que no menciona explícitamente.

> **Nota Crítica sobre Dinámica Empresarial:** En los escenarios de alta fiscalización **B2 (GovTech Intensivo)** y **D (Integrado)**, la tasa anual de cierres de empresas simulada en el modelo actual es **mucho mayor que en el artículo** (52.89% obtenido vs. 18.55% en el artículo para B2; 20.68% obtenido vs. 6.61% en el artículo para D).

---

## 1. Resumen de la Ejecución y Entorno de Cómputo

- **Comando ejecutado:** `make all` (`python -m itdt.cli all`)
- **Tiempo total de ejecución (`make all`):** **1 203.28 segundos (20 minutos y 3 segundos)**
- **Entorno de ejecución:**
  - **Sistema Operativo:** Microsoft Windows 11 Home Single Language 64-bit
  - **Intérprete:** Python 3.14.4
  - **Paralelización:** `ProcessPoolExecutor` (8 trabajadores concurrentes)
- **Verificación de pruebas (`pytest`):** **24 pruebas pasadas al 100% en 4.77 segundos**.

---

## 2. Comparación Numérica Detallada (Tablas 2 a 12)

### Tabla 2: Momentos Observados, Momentos Simulados y Parámetros Estimados por SMM

| País (año) | Métrica / Parámetro | Valor Artículo | Valor Obtenido | Diferencia ($\Delta$) | Observación |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Kenia (2019)** | $s_F$ (empleo femenino) | 0.476 | 0.476 | 0.000 | ILOSTAT oficial (`data/ilostat_s_F.csv`) |
| | $F_{obs}$ / $F_{sim}$ (%) | 90.19 / 89.66 | 90.19 / 90.25 | +0.59 p.p. | diferencia no explicada |
| | $M_{obs}$ / $M_{sim}$ (%) | 83.13 / 82.34 | 83.13 / 83.16 | +0.82 p.p. | diferencia no explicada |
| | $T_{obs}$ / $T_{sim}$ (%) | 86.49 / 85.82 | 86.49 / 86.54 | +0.72 p.p. | Relación contable $s_F F + (1-s_F) M$ |
| | $\phi_0$ (EE) | 3.08 (0.56) | 3.59 (0.68) | +0.51 (+0.12) | diferencia no explicada |
| | $\gamma_0$ (EE) | 0.461 (0.023) | 0.460 (0.011) | -0.001 (-0.012) | Coincidencia cercana |
| **Nigeria (2024)** | $s_F$ (empleo femenino) | 0.504 | 0.504 | 0.000 | ILOSTAT oficial (`data/ilostat_s_F.csv`) |
| | $F_{obs}$ / $F_{sim}$ (%) | 96.39 / 96.40 | 96.39 / 96.46 | +0.06 p.p. | Ajuste muy cercano al momento empírico |
| | $M_{obs}$ / $M_{sim}$ (%) | 89.92 / 89.99 | 89.92 / 89.88 | -0.11 p.p. | Error de calibración de 0.04 p.p. |
| | $T_{obs}$ / $T_{sim}$ (%) | 93.18 / 93.22 | 93.18 / 93.20 | -0.02 p.p. | Consistencia contable verificada |
| | $\phi_0$ (EE) | 8.96 (0.31) | 11.25 (1.16) | +2.29 (+0.85) | diferencia no explicada |
| | $\gamma_0$ (EE) | 0.620 (< 0.012) | 0.621 (0.012) | +0.001 (—) | Coincidencia a nivel de milésimas |
| **India (2024)** | $s_F$ (empleo femenino) | 0.309 | 0.311 | +0.002 | ILOSTAT SDMX oficial (`data/ilostat_s_F.csv`) |
| | $F_{obs}$ / $F_{sim}$ (%) | 91.93 / 92.13 | 91.93 / 91.90 | -0.23 p.p. | Calibración con error de 0.03 p.p. |
| | $M_{obs}$ / $M_{sim}$ (%) | 86.76 / 86.71 | 86.76 / 86.74 | +0.03 p.p. | Ajuste de alta precisión |
| | $T_{obs}$ / $T_{sim}$ (%) | 88.36 / 88.39 | 88.36 / 88.34 | -0.05 p.p. | Consistencia contable verificada |
| | $\phi_0$ (EE) | 4.84 (0.35) | 5.86 (0.86) | +1.02 (+0.51) | diferencia no explicada |
| | $\gamma_0$ (EE) | 0.464 (0.014) | 0.442 (0.008) | -0.022 (-0.006) | diferencia no explicada |
| **Bangladés (2023)**| $s_F$ (empleo femenino) | 0.345 | 0.345 | 0.000 | ILOSTAT oficial (`data/ilostat_s_F.csv`) |
| | $F_{obs}$ / $F_{sim}$ (%) | 95.77 / 95.66 | 95.77 / 95.82 | +0.16 p.p. | Ajuste con error de 0.05 p.p. |
| | $M_{obs}$ / $M_{sim}$ (%) | 78.08 / 78.33 | 78.08 / 78.00 | -0.33 p.p. | Error de 0.08 p.p. frente a $M_{obs}$ |
| | $T_{obs}$ / $T_{sim}$ (%) | 84.19 / 84.31 | 84.19 / 84.15 | -0.16 p.p. | Consistencia contable verificada |
| | $\phi_0$ (EE) | 2.03 (0.36) | 2.25 (0.54) | +0.22 (+0.18) | Coincidencia en orden de magnitud |
| | $\gamma_0$ (EE) | 0.763 (0.014) | 0.762 (0.009) | -0.001 (-0.005) | Coincidencia a nivel de milésimas |

---

### Tabla 3: Predicción de la Informalidad Femenina Dejando un País Fuera (LOCO)

| País Excluido | Modelo Alternativo | Pronóstico Artículo (%) | Pronóstico Obtenido (%) | Diferencia ($\Delta$) | Error Absoluto Obtenido |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Kenia** ($F_{obs} = 90.19$) | **ITDT ($\gamma_0$ común)** | 95.36 ($\gamma_0=0.7$) | 95.73 ($\gamma_0=0.7$) | +0.37 p.p. | 5.54 p.p. |
| | Brecha media | 92.91 | 92.91 | 0.00 p.p. | 2.72 p.p. |
| | Razón media | 93.05 | 93.05 | 0.00 p.p. | 2.86 p.p. |
| | Regresión lineal | 91.40 | 91.36 | -0.04 p.p. | 1.17 p.p. |
| | ITDT sin cuidado | 86.01 | 82.95 | -3.06 p.p. | 7.24 p.p. |
| **Nigeria** ($F_{obs} = 96.39$) | **ITDT ($\gamma_0$ común)** | 94.32 ($\gamma_0=0.5$) | 94.79 ($\gamma_0=0.5$) | +0.47 p.p. | 1.60 p.p. |
| | Brecha media | 99.89 | 99.89 | 0.00 p.p. | 3.50 p.p. |
| | Razón media | 100.00 | 100.00 | 0.00 p.p. | 3.61 p.p. |
| | Regresión lineal | 98.17 | 98.11 | -0.06 p.p. | 1.72 p.p. |
| | ITDT sin cuidado | 93.45 | 90.05 | -3.40 p.p. | 6.34 p.p. |
| **India** ($F_{obs} = 91.93$) | **ITDT ($\gamma_0$ común)** | 96.17 ($\gamma_0=0.7$) | 94.74 ($\gamma_0=0.6$) | -1.43 p.p. | 2.81 p.p. |
| | Brecha media | 97.17 | 97.17 | 0.00 p.p. | 5.24 p.p. |
| | Razón media | 97.85 | 97.85 | 0.00 p.p. | 5.92 p.p. |
| | Regresión lineal | 106.97 | 106.88 | -0.09 p.p. | 14.95 p.p. |
| | ITDT sin cuidado | 87.31 | 86.63 | -0.68 p.p. | 5.30 p.p. |
| **Bangladés** ($F_{obs} = 95.77$)| **ITDT ($\gamma_0$ común)** | 87.89 ($\gamma_0=0.5$) | 88.88 ($\gamma_0=0.5$) | +0.99 p.p. | 6.89 p.p. |
| | Brecha media | 84.31 | 84.31 | 0.00 p.p. | 11.46 p.p. |
| | Razón media | 83.71 | 83.71 | 0.00 p.p. | 12.06 p.p. |
| | Regresión lineal | 83.61 | 83.60 | -0.01 p.p. | 12.17 p.p. |
| | ITDT sin cuidado | 83.42 | 77.94 | -5.48 p.p. | 17.83 p.p. |
| **MAE Global (p.p.)** | **ITDT ($\gamma_0$ común)** | **4.84** | **4.21** | **-0.63 p.p.** | **Menor MAE de todos los modelos** |
| | Brecha media | 5.73 | 5.73 | 0.00 p.p. | Segunda alternativa |
| | Razón media | 6.11 | 6.11 | 0.00 p.p. | Tercera alternativa |
| | Regresión lineal | 7.55 | 7.50 | -0.05 p.p. | Falla con predicción > 100% en India |
| | ITDT sin cuidado | 6.02 | 9.18 | +3.16 p.p. | Mayor error fuera de muestra |

---

### Tabla 4: Ajuste Dentro de Muestra de Modelos Estructurales Recalibrados

| Modelo Estructural | Parámetros Libres | MAE 8 Momentos (Artículo) | MAE 8 Momentos (Obtenido) | Brecha F−M Simulada (Artículo) | Brecha F−M Simulada (Obtenida) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **E1: Agente representativo** | $\phi_0$ | 4.58 p.p. | 4.57 p.p. | -0.07 p.p. | -0.05 p.p. |
| **E2: ABM lewisiano** | $\phi_0$ | 4.57 p.p. | 4.55 p.p. | -0.05 p.p. | -0.01 p.p. |
| **E3: ITDT sin cuidado** | $\phi_0$ | 4.62 p.p. | 4.55 p.p. | -0.14 p.p. | -0.01 p.p. |
| **E4: Racionalidad perfecta**| $\phi_0, \gamma_0$ | 0.25 p.p. | 1.73 p.p. | +9.53 p.p. | +7.87 p.p. |
| **ITDT (Canónico)** | $\phi_0, \gamma_0$ | **0.25 p.p.** | **0.05 p.p.** | **+9.12 p.p.** | **+9.16 p.p.** |

*Nota:* Brecha media observada de los cuatro países = 9.10 p.p.

---

### Tabla 5: Niveles por Escenario en los Meses 109–120 (Media de los Cuatro Países)

| Escenario | Informalidad Total (%) | Mujeres (%) | Hombres (%) | Brecha F − M (p.p.) | Cierre Anual Empresas (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **A: Status Quo** | | | | | |
| • Artículo | 87.14 (2.20) | 93.20 (1.20) | 83.32 (2.93) | 9.88 | 0.07 (0.05) |
| • Obtenido | 88.74 (2.06) | 93.95 (1.12) | 85.44 (2.77) | 8.51 | 0.03 (0.09) |
| • Diferencia ($\Delta$) | +1.60 p.p. | +0.75 p.p. | +2.12 p.p. | -1.37 p.p. | -0.04 p.p. |
| **B1: GovTech Moderado** | | | | | |
| • Artículo | 87.21 (2.23) | 93.24 (1.22) | 83.41 (2.96) | 9.83 | 0.04 (0.04) |
| • Obtenido | 88.82 (2.04) | 93.99 (1.09) | 85.55 (2.74) | 8.44 | 0.00 (0.00) |
| • Diferencia ($\Delta$) | +1.61 p.p. | +0.75 p.p. | +2.14 p.p. | -1.39 p.p. | -0.04 p.p. |
| **B2: GovTech Intensivo**| | | | | |
| • Artículo | 54.74 (1.18) | 77.98 (0.89) | 38.74 (1.68) | 39.25 | **18.55 (1.33)** |
| • Obtenido | 55.40 (1.50) | 77.75 (0.96) | 39.86 (1.96) | 37.89 | **52.89 (4.87)** |
| • Diferencia ($\Delta$) | +0.66 p.p. | -0.23 p.p. | +1.12 p.p. | -1.36 p.p. | **+34.34 p.p.** *(cierres mucho mayores)* |
| **C: Red de Cuidados** | | | | | |
| • Artículo | 86.08 (2.34) | 86.51 (2.40) | 85.82 (2.38) | 0.69 | 0.05 (0.04) |
| • Obtenido | 87.88 (2.09) | 88.29 (2.01) | 87.63 (2.20) | 0.66 | 0.01 (0.05) |
| • Diferencia ($\Delta$) | +1.80 p.p. | +1.78 p.p. | +1.81 p.p. | -0.03 p.p. | -0.04 p.p. |
| **D: Integrado** | | | | | |
| • Artículo | 53.92 (3.19) | 55.09 (3.33) | 53.14 (3.25) | 1.94 | **6.61 (0.76)** |
| • Obtenido | 55.94 (2.76) | 56.93 (2.82) | 55.27 (2.89) | 1.67 | **20.68 (3.20)** |
| • Diferencia ($\Delta$) | +2.02 p.p. | +1.84 p.p. | +2.13 p.p. | -0.27 p.p. | **+14.07 p.p.** *(cierres mucho mayores)* |

---

### Tabla 6: Cambios Frente al Escenario A e IC 95% por Bootstrap por Conglomerados

| Escenario | Métrica | Estimación Artículo [IC 95%] | Estimación Obtenida [IC 95%] | Diferencia Puntual ($\Delta$) |
| :--- | :--- | :---: | :---: | :---: |
| **B1** | Total (p.p.) | +0.07 [-0.08, 0.23] | +0.08 [-0.03, 0.18] | +0.01 p.p. |
| | Mujeres (p.p.) | +0.04 [-0.04, 0.14] | +0.04 [-0.02, 0.10] | 0.00 p.p. |
| | Hombres (p.p.) | +0.09 [-0.12, 0.30] | +0.11 [-0.03, 0.25] | +0.02 p.p. |
| | Brecha (p.p.) | -0.05 [-0.20, 0.09] | -0.07 [-0.18, 0.02] | -0.02 p.p. |
| | Cierres (p.p./año) | -0.03 [-0.04, -0.02] | -0.03 [-0.05, -0.02] | 0.00 p.p. |
| | Recaudación (%) | +1.1 [-1.3, 4.1] | -0.6 [-2.0, 0.5] | -1.7 % *(diferencia no explicada)* |
| **B2** | Total (p.p.) | -32.40 [-38.79, -25.38] | -33.34 [-39.30, -26.78] | -0.94 p.p. |
| | Mujeres (p.p.) | -15.21 [-21.52, -8.67] | -16.20 [-23.14, -9.13] | -0.99 p.p. |
| | Hombres (p.p.) | -44.58 [-50.52, -35.99] | -45.58 [-51.46, -37.99] | -1.00 p.p. |
| | Brecha (p.p.) | +29.37 [25.78, 35.44] | +29.38 [24.29, 35.92] | +0.01 p.p. |
| | Cierres (p.p./año) | **+18.48 [13.58, 24.43]** | **+52.86 [40.45, 68.08]** | **+34.38 p.p.** *(cierres mucho mayores)* |
| | Recaudación (%) | +270.4 [158.5, 434.6] | +291.8 [158.3, 471.1] | +21.4 % |
| **C** | Total (p.p.) | -1.06 [-1.52, -0.64] | -0.86 [-1.43, -0.28] | +0.20 p.p. |
| | Mujeres (p.p.) | -6.68 [-11.61, -3.82] | -5.66 [-10.15, -2.73] | +1.02 p.p. |
| | Hombres (p.p.) | +2.51 [1.35, 4.02] | +2.19 [1.22, 3.34] | -0.32 p.p. |
| | Brecha (p.p.) | -9.19 [-15.57, -5.30] | -7.85 [-13.42, -4.17] | +1.34 p.p. |
| | Cierres (p.p./año) | -0.02 [-0.03, -0.01] | -0.02 [-0.04, 0.00] | 0.00 p.p. |
| | Recaudación (%) | +10.8 [6.2, 15.7] | +9.9 [6.5, 12.8] | -0.9 % |
| **D** | Total (p.p.) | -33.22 [-38.33, -28.23] | -32.80 [-38.23, -27.51] | +0.42 p.p. |
| | Mujeres (p.p.) | -38.11 [-41.21, -35.20] | -37.02 [-40.19, -33.82] | +1.09 p.p. |
| | Hombres (p.p.) | -30.17 [-36.73, -23.45] | -30.17 [-36.91, -23.40] | 0.00 p.p. |
| | Brecha (p.p.) | -7.94 [-14.35, -3.82] | -6.85 [-12.34, -2.97] | +1.09 p.p. |
| | Cierres (p.p./año) | **+6.54 [3.34, 10.37]** | **+20.65 [12.23, 31.13]** | **+14.11 p.p.** *(cierres mucho mayores)* |
| | Recaudación (%) | +220.9 [118.7, 375.3] | +251.6 [127.4, 432.0] | +30.7 % |

---

### Tabla 7: Contrastes por País Frente al Escenario A ($R=40, gl=39$)

| Contraste | País | Dif. Media (DE) Artículo | Dif. Media (DE) Obtenida | $t(39)$ Art. / Obt. | $d_z$ Art. / Obt. | $p$-val (Bonferroni / Wilcoxon) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **B2: mujeres** | Kenia | -20.57 (1.79) | -21.41 (1.63) | -72.8 / -83.2 | -11.50 / -13.16 | < 0.001 / < 0.001 |
| | Nigeria | -13.28 (1.01) | -13.70 (0.94) | -82.9 / -91.9 | -13.10 / -14.54 | < 0.001 / < 0.001 |
| | India | -22.31 (1.40) | -24.63 (1.61) | -100.7 / -96.5 | -15.91 / -15.26 | < 0.001 / < 0.001 |
| | Bangladés | -4.70 (0.73) | -5.07 (0.54) | -40.6 / -59.4 | -6.43 / -9.39 | < 0.001 / < 0.001 |
| **B2: brecha** | Kenia | +25.34 (1.89) | +24.96 (1.82) | 84.6 / 87.0 | 13.37 / 13.75 | < 0.001 / < 0.001 |
| | Nigeria | +38.33 (1.68) | +39.40 (1.84) | 144.2 / 135.7 | 22.80 / 21.45 | < 0.001 / < 0.001 |
| | India | +26.82 (1.99) | +23.85 (2.47) | 85.3 / 61.1 | 13.48 / 9.66 | < 0.001 / < 0.001 |
| | Bangladés | +26.98 (3.51) | +29.30 (2.54) | 48.5 / 73.1 | 7.68 / 11.55 | < 0.001 / < 0.001 |
| **D: total** | Kenia | -30.59 (2.03) | -29.31 (2.44) | -95.5 / -75.9 | -15.11 / -12.00 | < 0.001 / < 0.001 |
| | Nigeria | -40.74 (3.06) | -40.26 (3.04) | -84.1 / -83.7 | -13.30 / -13.24 | < 0.001 / < 0.001 |
| | India | -35.42 (2.62) | -35.53 (2.38) | -85.5 / -94.3 | -13.52 / -14.91 | < 0.001 / < 0.001 |
| | Bangladés | -26.12 (2.08) | -26.08 (2.02) | -79.4 / -81.8 | -12.56 / -12.93 | < 0.001 / < 0.001 |
| **D: brecha** | Kenia | -6.60 (1.82) | -6.10 (1.94) | -22.9 / -19.9 | -3.63 / -3.15 | < 0.001 / < 0.001 |
| | Nigeria | -3.59 (1.70) | -2.63 (2.01) | -13.3 / -8.3 | -2.11 / -1.31 | < 0.001 / < 0.001 |
| | India | -4.18 (1.65) | -3.42 (1.57) | -16.0 / -13.8 | -2.54 / -2.18 | < 0.001 / < 0.001 |
| | Bangladés | -17.38 (3.58) | -15.23 (2.60) | -30.7 / -37.0 | -4.85 / -5.85 | < 0.001 / < 0.001 |

*Nota:* Todos los contrastes son estadísticamente significativos ($p < 0.001$) bajo Bonferroni y Wilcoxon.

---

### Tabla 8: Descomposición del Efecto de B2 Frente a A (Media de los Cuatro Países)

| Variante del Modelo | $\Delta$ Mujeres (p.p.) Art. / Obt. | $\Delta$ Hombres (p.p.) Art. / Obt. | $\Delta$ Brecha (p.p.) Art. / Obt. | $\Delta$ Cierres (p.p./año) Art. / Obt. | $\Delta$ Empresas Dueña / Dueño (p.p.) Art. / Obt. |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Completo** | -15.13 / -15.90 | -44.17 / -45.00 | **+29.04 / +29.11** | **+18.50 / +52.94** | +22.8 / +27.0 vs. +20.9 / +26.0 |
| **Sin restricción de cuidado**| -40.65 / -36.13 | -40.67 / -36.20 | **+0.02 / +0.07** | **+16.04 / +37.06** | +25.6 / +25.4 vs. +25.9 / +26.6 |
| **Sin DCC regresivo** | -15.02 / -16.12 | -44.09 / -45.26 | **+29.07 / +29.15** | **+18.00 / +51.26** | +22.9 / +27.1 vs. +21.6 / +26.3 |
| **Sin ambos** | -40.67 / -36.74 | -40.67 / -36.76 | **0.00 / +0.02** | **+15.83 / +36.41** | +26.2 / +25.9 vs. +26.4 / +26.5 |

*Confirmación científica del mecanismo:* Al desactivar la carga de cuidado, la brecha de género colapsa a prácticamente cero (+0.07 p.p. obtenido vs. +0.02 p.p. en el artículo), mientras que eliminar el costo digital regresivo del DCC la mantiene intacta (+29.15 p.p. obtenido vs. +29.07 p.p. en el artículo). En todas las variantes, los cierres anuales de empresas obtenidos son sistemáticamente mayores a los reportados en el manuscrito (diferencia no explicada).

---

### Tabla 9: Sensibilidad de los Efectos Principales ($\pm 20\%$)

| Parámetro | $\Delta$ Mujeres en B2 Art. / Obt. | Elasticidad B2 Art. / Obt. | $\Delta$ Total en D Art. / Obt. | Elasticidad D Art. / Obt. | Observación |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Referencia** | -15.19 / -15.97 | — | -32.80 / -32.43 | — | Punto basal |
| **$\phi_0$** | -14.00 / -15.98 vs. -15.08 / -16.85 | +0.33 / +0.28 | -31.13 / -34.37 vs. -30.56 / -34.25 | +0.25 / +0.28 | Elasticidad positiva coincidente |
| **$\phi_1$** | -15.18 / -15.23 vs. -16.20 / -15.93 | +0.01 / -0.04 | -32.52 / -32.86 vs. -32.86 / -32.63 | +0.03 / -0.02 | Magnitud cercana a cero |
| **$\eta$** | -15.14 / -15.09 vs. -15.92 / -16.18 | -0.01 / +0.04 | -33.04 / -32.61 vs. -32.97 / -33.15 | -0.03 / +0.01 | Invarianza local |
| **$\mu_0$** | -16.24 / -13.73 vs. -16.63 / -15.05 | -0.41 / -0.25 | -33.82 / -31.61 vs. -32.50 / -31.98 | -0.17 / -0.04 | Signo negativo coincidente |
| **$\kappa$** | -14.97 / -15.04 vs. -16.51 / -16.10 | +0.01 / -0.06 | -32.57 / -33.39 vs. -33.35 / -32.98 | +0.06 / -0.03 | Magnitud cercana a cero |
| **$\gamma_0$** | -21.62 / -9.73 vs. -22.87 / -10.79 | -1.96 / -1.89 | -32.75 / -32.87 vs. -32.88 / -32.79 | +0.01 / -0.01 | Elasticidad rectora idéntica (-1.96 vs -1.89) |
| **$H_{care}$ mujeres** | -22.20 / -9.48 vs. -23.31 / -10.49 | -2.09 / -2.01 | -32.97 / -33.16 vs. -33.15 / -33.26 | +0.01 / +0.01 | Elasticidad rectora idéntica (-2.09 vs -2.01) |
| **$T_0$** | *(No en tabla del artículo)* / -16.02 / -15.88 | *(No en art.)* / -0.02 | *(No en tabla del artículo)* / -32.65 / -32.71 | *(No en art.)* / +0.00 | Invarianza ante temperatura inicial |
| **$(1 - d)$** | *(No en tabla del artículo)* / -15.96 / -16.36 | *(No en art.)* / +0.06 | *(No en tabla del artículo)* / -32.82 / -32.13 | *(No en art.)* / -0.05 | Perturbación del enfriamiento anual |
| **CES ($\sigma=0.5$)** | -15.62 / -16.81 | — | -35.39 / -34.71 | — | Recalibrado |
| **CES ($\sigma=1.5$)** | -15.16 / -16.34 | — | -32.13 / -32.51 | — | Recalibrado |
| **Choque demanda (-5%)**| -15.37 / -16.49 | — | -31.74 / -31.33 | — | Choque exógeno mes 60 |

---

### Tabla 10: Costo Computacional por Réplica (216 Meses)

| Escala ($N_W$ / $N_F$) | Tiempo por Réplica Artículo | Tiempo por Réplica Obtenido | Memoria Máxima Artículo | Memoria Máxima Obtenida |
| :--- | :---: | :---: | :---: | :---: |
| **3 000 / 300** | 0.080 s (0.003) | 0.222 s (0.077) | 78.0 MB | 202.9 MB |
| **6 000 / 600 (Base)**| 0.129 s (0.002) | 0.274 s (0.040) | 78.5 MB | 203.9 MB |
| **12 000 / 1 200** | 0.249 s (0.001) | 0.456 s (0.027) | 79.3 MB | 205.8 MB |
| **24 000 / 2 400** | 0.468 s (0.012) | 0.682 s (0.087) | 81.0 MB | 208.6 MB |

*Observación:* Tanto los tiempos de ejecución como la memoria RSS obtenida en el entorno actual son mayores que las cifras reportadas en el texto del artículo (diferencia no explicada). El escalamiento del tiempo de ejecución respecto a $N_W$ exhibe en ambos casos un comportamiento aproximadamente lineal.

---

### Tabla 11: Desempeño de ITDT por Sexo

| Indicador | Sexo / Cobertura | Valor Artículo | Valor Obtenido | Diferencia ($\Delta$) |
| :--- | :--- | :---: | :---: | :---: |
| **Error absoluto de calibración** (media de 4 países) | Mujeres | 0.21 p.p. | 0.06 p.p. | -0.15 p.p. |
| | Hombres | 0.29 p.p. | 0.04 p.p. | -0.25 p.p. |
| **Cociente brecha simulada / observada** | Kenia | 1.04 | 1.00 | -0.04 |
| | Nigeria | 0.99 | 1.02 | +0.03 |
| | India | 1.05 | 1.00 | -0.05 |
| | Bangladés | 0.98 | 1.01 | +0.03 |

*Nota:* Las brechas se definen como $F - M$ (mujeres menos hombres). En la calibración obtenida, el cociente entre la brecha simulada y la observada se sitúa en un rango de [1.00, 1.02].

---

### Tabla 12: Gradientes No Calibrados (Escenario A)

| Gradiente No Calibrado (Escenario A, Media de 4 Países) | Informalidad Simulada Artículo (%) | Informalidad Simulada Obtenida (%) | Dirección Esperada | ¿Se Reproduce? (Art. / Obt.) |
| :--- | :---: | :---: | :--- | :---: |
| **Educación básica / media / superior** | 94.8 / 85.1 / 69.6 | 95.8 / 87.0 / 72.1 | Decreciente con educación | Sí / Sí |
| **Rural / urbano** | 90.2 / 82.5 | 91.5 / 84.6 | Rural > urbano | Sí / Sí |
| **Quintil de productividad (1 a 5)** | 99.7 / 99.6 / 98.6 / 87.0 / 50.9 | 99.7 / 99.7 / 99.5 / 90.7 / 54.1 | Decreciente con productividad | Sí, pero demasiado concentrado / Sí, pero concentrado |

*Nota:* Los gradientes no forman parte de los momentos objetivo de la calibración SMM.

---

## 3. Discusión de Discrepancias

1. **Cierres Anuales de Empresas en Escenarios B2 y D:**  
   En la simulación actual, los cierres de empresas bajo fiscalización severa son **mucho mayores que en el artículo** (+34.34 p.p. en el nivel de B2 y +14.07 p.p. en el nivel de D frente a las cifras del texto). La causa precisa de esta discrepancia en la dinámica de salida de firmas respecto a la corrida histórica del manuscrito se clasifica como **diferencia no explicada**.

2. **Diferencias Numéricas Menores en Parámetros Calibrados y Métricas Agregadas:**  
   En parámetros como $\phi_0$ en Nigeria (11.25 obtenido vs. 8.96 en el artículo), los tiempos y memoria de la Tabla 10, y las ligeras variaciones de ~1 p.p. en las tasas basales de la Tabla 5, el origen exacto de las discrepancias respecto a la ejecución del manuscrito no está documentado en el texto del artículo y queda registrado como **diferencia no explicada**.

3. **Robustez del Mecanismo Científico Central:**  
   A pesar de las discrepancias numéricas en cierres y parámetros específicos, los hallazgos sustantivos del artículo se replican con precisión:
   - **LOCO:** ITDT logra el menor MAE global fuera de muestra (4.21 p.p. obtenido vs. 4.84 p.p. artículo), superando a todos los modelos estadísticos de referencia.
   - **Formalización Extractiva:** El Escenario B2 amplía la brecha de género en +29.38 p.p. (artículo: +29.37 p.p.).
   - **Ablación:** Al desactivar los cuidados, la ampliación de la brecha colapsa a +0.07 p.p. (artículo: +0.02 p.p.), mientras que sin costo digital regresivo ($DCC$) la brecha se mantiene en +29.15 p.p. (artículo: +29.07 p.p.).
   - **Sensibilidad:** Las elasticidades rectoras de $\gamma_0$ (-1.89 obtenido vs. -1.96 artículo) y de $H_{care}$ femenino (-2.01 obtenido vs. -2.09 artículo) coinciden sólidamente.
