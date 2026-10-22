# Verificación Automática: Aplicación Web vs Modelo Calibrado ITDT

- **Fecha y hora de ejecución:** 2026-10-21 23:00:27
- **País evaluado:** Kenia (KEN)
- **Horizonte de evaluación:** Mes 120 de la política (promedio final de réplicas en meses 109–120)
- **Fuente econométrica:** `outputs/policy_experiments_results.json` (media de 40 réplicas por escenario)
- **Punto de conexión API:** `http://127.0.0.1:8000/api/v1/simulation/metrics`
- **Tolerancia máxima:** 0.50 puntos porcentuales (p.p.)

## 1. Tabla de Comparación: Tasa de Informalidad (%)

| Escenario | Etiqueta | Oficial Modelo (%) | Respuesta API (%) | Diferencia (p.p.) | Tolerancia | Estado |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **A** | Status Quo (Inercial) | 86.13 % | 86.13 % | +0.00 p.p. | ≤ 0.50 p.p. | **APROBADO** |
| **B1** | GovTech Moderado | 86.18 % | 86.18 % | +0.00 p.p. | ≤ 0.50 p.p. | **APROBADO** |
| **B2** | GovTech Intensivo (Sanciones 3×) | 51.58 % | 51.58 % | +0.00 p.p. | ≤ 0.50 p.p. | **APROBADO** |
| **C** | Red de Cuidados (−60% cuidado infantil) | 85.00 % | 85.00 % | +0.00 p.p. | ≤ 0.50 p.p. | **APROBADO** |
| **D** | Paquete Integrado (B2 + C + Subsidio DCC) | 56.82 % | 56.82 % | +0.00 p.p. | ≤ 0.50 p.p. | **APROBADO** |

## 2. Detalle Completo de Indicadores Estructurales por Escenario

| Escenario | Métrica | Oficial Modelo | Respuesta API | Diferencia | Estado |
|:---|:---|:---:|:---:|:---:|:---:|
| **A** | Informalidad Total | 86.13 % | 86.13 % | 0.00 p.p. | PASS |
| **A** | Informalidad Mujeres | 89.92 % | 89.92 % | 0.00 p.p. | PASS |
| **A** | Informalidad Hombres | 82.72 % | 82.72 % | 0.00 p.p. | PASS |
| **A** | Brecha Género (F − M) | 7.20 p.p. | 7.20 p.p. | 0.00 p.p. | PASS |
| **A** | Cierre Empresas Anual | 0.05 % | 0.05 % | 0.00 p.p. | PASS |
| **A** | Recaudación Total (u.m.) | 1381.05 | 1381.05 | 0.00 | PASS |
| **A** | Cuadre Fiscal (Soc.+Seg.) | — | 1194.83 + 186.22 = 1381.05 | 0.00 | CUADRA |
| **B1** | Informalidad Total | 86.18 % | 86.18 % | 0.00 p.p. | PASS |
| **B1** | Informalidad Mujeres | 89.95 % | 89.95 % | 0.00 p.p. | PASS |
| **B1** | Informalidad Hombres | 82.78 % | 82.78 % | 0.00 p.p. | PASS |
| **B1** | Brecha Género (F − M) | 7.17 p.p. | 7.17 p.p. | 0.00 p.p. | PASS |
| **B1** | Cierre Empresas Anual | 0.00 % | 0.00 % | 0.00 p.p. | PASS |
| **B1** | Recaudación Total (u.m.) | 1378.18 | 1378.18 | 0.00 | PASS |
| **B1** | Cuadre Fiscal (Soc.+Seg.) | — | 1193.95 + 184.23 = 1378.18 | 0.00 | CUADRA |
| **B2** | Informalidad Total | 51.58 % | 51.58 % | 0.00 p.p. | PASS |
| **B2** | Informalidad Mujeres | 68.51 % | 68.51 % | 0.00 p.p. | PASS |
| **B2** | Informalidad Hombres | 36.35 % | 36.35 % | 0.00 p.p. | PASS |
| **B2** | Brecha Género (F − M) | 32.16 p.p. | 32.16 p.p. | 0.00 p.p. | PASS |
| **B2** | Cierre Empresas Anual | 44.70 % | 44.70 % | 0.00 p.p. | PASS |
| **B2** | Recaudación Total (u.m.) | 3846.67 | 3846.67 | 0.00 | PASS |
| **B2** | Cuadre Fiscal (Soc.+Seg.) | — | 3453.13 + 393.54 = 3846.67 | 0.00 | CUADRA |
| **C** | Informalidad Total | 85.00 % | 85.00 % | 0.00 p.p. | PASS |
| **C** | Informalidad Mujeres | 85.27 % | 85.27 % | 0.00 p.p. | PASS |
| **C** | Informalidad Hombres | 84.75 % | 84.75 % | 0.00 p.p. | PASS |
| **C** | Brecha Género (F − M) | 0.52 p.p. | 0.52 p.p. | 0.00 p.p. | PASS |
| **C** | Cierre Empresas Anual | 0.02 % | 0.02 % | 0.00 p.p. | PASS |
| **C** | Recaudación Total (u.m.) | 1515.65 | 1515.65 | 0.00 | PASS |
| **C** | Cuadre Fiscal (Soc.+Seg.) | — | 1311.81 + 203.84 = 1515.65 | 0.00 | CUADRA |
| **D** | Informalidad Total | 56.82 % | 56.82 % | 0.00 p.p. | PASS |
| **D** | Informalidad Mujeres | 57.40 % | 57.40 % | 0.00 p.p. | PASS |
| **D** | Informalidad Hombres | 56.30 % | 56.30 % | 0.00 p.p. | PASS |
| **D** | Brecha Género (F − M) | 1.10 p.p. | 1.10 p.p. | 0.00 p.p. | PASS |
| **D** | Cierre Empresas Anual | 14.96 % | 14.96 % | 0.00 p.p. | PASS |
| **D** | Recaudación Total (u.m.) | 3259.10 | 3259.10 | 0.00 | PASS |
| **D** | Cuadre Fiscal (Soc.+Seg.) | — | 2816.32 + 442.78 = 3259.10 | 0.00 | CUADRA |

## 3. Conclusión de la Verificación

**RESULTADO GLOBAL: APROBADO.** Todos los escenarios (A, B1, B2, C, D) coinciden con los resultados oficiales de `outputs/policy_experiments_results.json` con una discrepancia máxima inferior a 0.50 p.p. y los componentes de recaudación fiscal cuadran de forma exacta (Impuesto de Sociedades + Contribuciones de Seguridad Social = Recaudación Total).
