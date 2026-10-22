# Reporte de Replicación del Modelo ITDT

**Fecha de ejecución:** 21 de octubre de 2026  
**Rama de trabajo:** `replicacion-2026-10-21`  
**Referencia del modelo:** Paquete canónico `itdt` (*ITDT: Un gemelo digital multi-agente calibrado con ILOSTAT para evaluar políticas de formalización con perspectiva de género en cuatro economías del Sur Global*)  
**Comando ejecutado:** `make.bat all` (`python -m itdt.cli all`)

---

## 1. Entorno de Ejecución del Sistema

| Parámetro | Valor Registrado | Observación |
| :--- | :--- | :--- |
| **Sistema Operativo** | Windows 11 Home Single Language (64-bit) | Versión 10.0.26100 |
| **Procesador (CPU)** | AMD Ryzen 7 4800H with Radeon Graphics | 8 núcleos físicos, 16 subprocesos lógicos |
| **Intérprete de Python** | Python 3.13.14 | Entorno virtual `.venv` aislado |
| **NumPy** | 2.2.3 | Versión fijada en `requirements-itdt.txt` |
| **SciPy** | 1.15.2 | Versión fijada en `requirements-itdt.txt` |
| **Pandas** | 2.2.3 | Versión fijada en `requirements-itdt.txt` |
| **Matplotlib** | 3.10.1 | Versión fijada en `requirements-itdt.txt` |
| **Tabulate** | 0.9.0 | Versión fijada en `requirements-itdt.txt` |
| **Pytest** | 8.3.5 | Versión fijada en `requirements-itdt.txt` |
| **Psutil** | 6.1.1 | Versión fijada en `requirements-itdt.txt` |
| **Tiempo total de ejecución (`make all`)** | **1 312.78 s (21 min 52 s)** | Medición end-to-end reportada por el CLI |

---

## 2. Resultado de la Suite de Pruebas

### 2.1 Pruebas previas a la replicación (sin `outputs/calibration_estimates.json`)
- **Ejecutadas:** 15 pruebas (`pytest tests/test_itdt_canonical.py tests/test_itdt.py -v`).
- **Resultado:** **8 pasadas, 7 falladas**.
- **Causa del fallo:** Todas las 7 fallas arrojaron estrictamente la excepción prevista de control paramétrico:
  `RuntimeError: País 'KENYA' no tiene estimaciones calibradas (phi_0, gamma_0). outputs/calibration_estimates.json no contiene este país o no existe. Ejecute 'make calibrate' para generarlo.`
  Las 8 pruebas independientes de calibración (utilidad, beneficios, DCC, $P_{aud}$, Metropolis y propiedades analíticas) pasaron al 100 %.

### 2.2 Pruebas posteriores a la replicación (con `outputs/` regenerado)
- **Suite completa `pytest`:** **15 de 15 pasadas al 100 % en 1.20 s**.
- **Prueba rápida `make.bat smoke`:** **10 de 10 pasadas en 0.29 s** + simulación de integración en 0.43 s.

---

## 3. Comparativa Numérica Detallada (Salidas Nuevas vs. `HEAD` de Git)

Se realizó una comparación exhaustiva entre los artefactos regenerados en `outputs/` y la versión precedente registrada en el historial del repositorio (`git show HEAD:outputs/<archivo>`).

### 3.1 Tabla 2: Parámetros Calibrados $\phi_0$ y $\gamma_0$ por SMM

| País (año) | Parámetro | Versión Anterior (HEAD) | Versión Nueva | Diferencia | Clasificación |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Kenia (2019)** | $\phi_0$ (EE) | 3.59 (0.68) | 3.59 (0.68) | 0.00 (0.00) | **Exacta** |
| | $\gamma_0$ (EE) | 0.460 (0.011) | 0.460 (0.011) | 0.000 (0.000) | **Exacta** |
| **Nigeria (2024)** | $\phi_0$ (EE) | 11.25 (1.16) | 11.25 (1.16) | 0.00 (0.00) | **Exacta** |
| | $\gamma_0$ (EE) | 0.621 (0.012) | 0.621 (0.012) | 0.000 (0.000) | **Exacta** |
| **India (2024)** | $\phi_0$ (EE) | 5.86 (0.86) | 5.86 (0.86) | 0.00 (0.00) | **Exacta** |
| | $\gamma_0$ (EE) | 0.442 (0.008) | 0.442 (0.008) | 0.000 (0.000) | **Exacta** |
| **Bangladés (2023)** | $\phi_0$ (EE) | 2.25 (0.54) | 2.25 (0.54) | 0.00 (0.00) | **Exacta** |
| | $\gamma_0$ (EE) | 0.762 (0.009) | 0.762 (0.009) | 0.000 (0.000) | **Exacta** |

---

### 3.2 Tabla 3: Validación Fuera de Muestra (LOCO) — MAE en p.p.

| Modelo Evaluado | MAE Anterior (HEAD) | MAE Nuevo | Diferencia | Clasificación |
| :--- | :---: | :---: | :---: | :--- |
| **ITDT Completo (Modelo Propuesto)** | **2.45 p.p.** | **2.45 p.p.** | **0.00 p.p.** | **Exacta** |
| Referencia E1: Media histórica / constante | 3.25 p.p. | 3.25 p.p. | 0.00 p.p. | **Exacta** |
| Referencia E2: Regresión lineal OLS | 7.50 p.p. | 7.50 p.p. | 0.00 p.p. | **Exacta** |
| Referencia E3: ITDT sin restricción de cuidados | 9.18 p.p. | 9.18 p.p. | 0.00 p.p. | **Exacta** |
| Referencia E4: ITDT sin fricciones | 12.35 p.p. | 12.35 p.p. | 0.00 p.p. | **Exacta** |

---

### 3.3 Tabla 5: Niveles por Escenario de Política ($R=40$ réplicas)

| Escenario | Métrica | Versión Anterior (HEAD) | Versión Nueva | Diferencia | Clasificación |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **A: Status Quo** | Total (%) | 88.74 (2.06) | 88.74 (2.06) | 0.00 (0.00) | **Exacta** |
| | Mujeres (%) | 93.95 (1.12) | 93.95 (1.12) | 0.00 (0.00) | **Exacta** |
| | Hombres (%) | 85.44 (2.77) | 85.44 (2.77) | 0.00 (0.00) | **Exacta** |
| | Brecha F − M (p.p.) | 8.51 | 8.51 | 0.00 | **Exacta** |
| | Cierre anual empresas (%) | 0.03 (0.09) | 0.03 (0.09) | 0.00 (0.00) | **Exacta** |
| **B1: GovTech Moderado** | Total (%) | 88.82 (2.04) | 88.82 (2.04) | 0.00 (0.00) | **Exacta** |
| | Mujeres (%) | 93.99 (1.09) | 93.99 (1.09) | 0.00 (0.00) | **Exacta** |
| | Hombres (%) | 85.55 (2.74) | 85.55 (2.74) | 0.00 (0.00) | **Exacta** |
| | Brecha F − M (p.p.) | 8.44 | 8.44 | 0.00 | **Exacta** |
| | Cierre anual empresas (%) | 0.00 (0.00) | 0.00 (0.00) | 0.00 (0.00) | **Exacta** |
| **B2: GovTech Intensivo** | Total (%) | 55.40 (1.50) | 55.40 (1.50) | 0.00 (0.00) | **Exacta** |
| | Mujeres (%) | 77.75 (0.96) | 77.75 (0.96) | 0.00 (0.00) | **Exacta** |
| | Hombres (%) | 39.86 (1.96) | 39.86 (1.96) | 0.00 (0.00) | **Exacta** |
| | Brecha F − M (p.p.) | **37.89** | **37.89** | **0.00** | **Exacta** |
| | Cierre anual empresas (%) | **52.89 (4.87)** | **52.89 (4.87)** | **0.00 (0.00)** | **Exacta** |
| **C: Red de Cuidados** | Total (%) | 87.88 (2.09) | 87.88 (2.09) | 0.00 (0.00) | **Exacta** |
| | Mujeres (%) | 88.29 (2.01) | 88.29 (2.01) | 0.00 (0.00) | **Exacta** |
| | Hombres (%) | 87.63 (2.20) | 87.63 (2.20) | 0.00 (0.00) | **Exacta** |
| | Brecha F − M (p.p.) | 0.66 | 0.66 | 0.00 | **Exacta** |
| | Cierre anual empresas (%) | 0.01 (0.05) | 0.01 (0.05) | 0.00 (0.00) | **Exacta** |
| **D: Paquete Integrado** | Total (%) | 55.94 (2.76) | 55.94 (2.76) | 0.00 (0.00) | **Exacta** |
| | Mujeres (%) | 56.93 (2.82) | 56.93 (2.82) | 0.00 (0.00) | **Exacta** |
| | Hombres (%) | 55.27 (2.89) | 55.27 (2.89) | 0.00 (0.00) | **Exacta** |
| | Brecha F − M (p.p.) | 1.67 | 1.67 | 0.00 | **Exacta** |
| | Cierre anual empresas (%) | **20.68 (3.20)** | **20.68 (3.20)** | **0.00 (0.00)** | **Exacta** |

---

### 3.4 Tabla 6: Cambios Frente al Escenario A (con IC bootstrap 95 %)

| Escenario | Total (p.p.) | Mujeres (p.p.) | Hombres (p.p.) | Brecha (p.p.) | Cierres (p.p./año) | Clasificación |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **B1** | +0.08 [−0.03, 0.18] | +0.04 [−0.02, 0.10] | +0.11 [−0.03, 0.25] | −0.07 [−0.18, 0.02] | −0.03 [−0.05, −0.02] | **Exacta** |
| **B2** | −33.34 [−39.30, −26.78] | −16.20 [−23.14, −9.13] | −45.58 [−51.46, −37.99] | **+29.38 [24.29, 35.92]** | **+52.86 [40.45, 68.08]** | **Exacta** |
| **C** | −0.86 [−1.43, −0.28] | −5.66 [−10.15, −2.73] | +2.19 [1.22, 3.34] | −7.85 [−13.42, −4.17] | −0.02 [−0.04, −0.00] | **Exacta** |
| **D** | −32.80 [−38.23, −27.51] | −37.02 [−40.19, −33.82] | −30.17 [−36.91, −23.40] | −6.85 [−12.34, −2.97] | **+20.65 [12.23, 31.13]** | **Exacta** |

---

### 3.5 Tabla 8: Ablación de Mecanismos sobre el Escenario B2

| Variante del Modelo | $\Delta$ Mujeres (p.p.) | $\Delta$ Hombres (p.p.) | $\Delta$ Brecha (p.p.) | $\Delta$ Cierres (p.p./año) | Clasificación |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Completo (B2 base)** | −15.90 | −45.00 | **29.11** | **52.94** | **Exacta** |
| **Sin restricción de cuidado** | −36.13 | −36.20 | **0.07** | **37.06** | **Exacta** |
| **Sin DCC regresivo** | −16.12 | −45.26 | **29.15** | **51.26** | **Exacta** |
| **Sin ambos** | −36.74 | −36.76 | **0.02** | **36.41** | **Exacta** |

---

### 3.6 Tabla 10: Benchmarking de Costo Computacional y Memoria

| Configuración ($N_W$ / $N_F$) | Métrica | Versión Anterior (HEAD) | Versión Nueva | Diferencia | Clasificación |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **$N_W = 3\,000$** ($N_F=300$) | Tiempo por réplica (s) | 0.149 (0.000) | 0.159 (0.002) | +0.010 s | Pequeña (carga CPU) |
| | Memoria proceso (MB) | 218.4 MB | 195.3 MB | −23.1 MB | Pequeña (Python 3.13) |
| **$N_W = 6\,000$** ($N_F=600$, base) | Tiempo por réplica (s) | 0.232 (0.005) | 0.232 (0.011) | 0.000 s | **Exacta** |
| | Memoria proceso (MB) | 218.4 MB | 194.3 MB | −24.1 MB | Pequeña (Python 3.13) |
| **$N_W = 12\,000$** ($N_F=1\,200$) | Tiempo por réplica (s) | 0.360 (0.006) | 0.365 (0.007) | +0.005 s | Pequeña (carga CPU) |
| | Memoria proceso (MB) | 218.6 MB | 195.7 MB | −22.9 MB | Pequeña (Python 3.13) |
| **$N_W = 24\,000$** ($N_F=2\,400$) | Tiempo por réplica (s) | 0.655 (0.020) | 0.646 (0.004) | −0.009 s | Pequeña (carga CPU) |
| | Memoria proceso (MB) | 219.3 MB | 197.7 MB | −21.6 MB | Pequeña (Python 3.13) |

---

## 4. Advertencias, Errores y Hallazgos Relevantes

1. **Determinismo Numérico Absoluto:**
   A pesar del cambio en el entorno de ejecución (de Python 3.14 preliminar a Python 3.13 con las versiones fijadas de `requirements-itdt.txt`), todas las métricas de calibración (Tabla 2), validación LOCO (Tabla 3), experimentos de política (Tablas 5, 6 y 7) y ablación estructural (Tabla 8) resultaron **100 % idénticas a nivel de punto flotante** a las registradas previamente.
2. **Cierre de Empresas y Brecha de Género bajo GovTech:**
   - La tasa anual de cierre de empresas en el escenario **B2 (GovTech Intensivo)** se confirmó de forma determinista en **52.89 % (DE = 4.87)**, frente al 0.03 % del Status Quo.
   - En el paquete **D (Integrado)**, la tasa anual de cierres se confirmó en **20.68 % (DE = 3.20)**, confirmando el efecto mitigador del subsidio al DCC.
   - La ampliación de la brecha de género en **B2** se reproduce exactamente en **+29.38 p.p. (IC 95 %: [+24.29, +35.92])**, explicada completamente por la restricción de cuidado no remunerado (la variante sin cuidado reduce la brecha a $\Delta = +0.07$ p.p.).
3. **Consumo de Memoria:**
   La ejecución en Python 3.13.14 redujo el uso de memoria residente en aproximadamente 23 MB respecto a Python 3.14, manteniendo una escalabilidad computacional lineal respecto al número de agentes.
