# Tabla 8: Matriz de Robustez a las Reglas de Entrada de Empresas y Normalización Ȳ

| especificacion                                | regla_entrada   | ybar_mode   |   phi0_media |   gamma0_media |   error_calib |   salidas_anuales_B2 |   salidas_anuales_D |   pct_firmas_cerradas_B2 |   pct_firmas_cerradas_D |   delta_inf_B2 |   delta_inf_D |   delta_gap_B2 |   delta_gap_D |   mae_loco |
|:----------------------------------------------|:----------------|:------------|-------------:|---------------:|--------------:|---------------------:|--------------------:|-------------------------:|------------------------:|---------------:|--------------:|---------------:|--------------:|-----------:|
| 1. forced_informal / Ybar dinamica (Articulo) | forced_informal | dynamic     |         5.75 |          0.565 |          0.08 |                52.19 |               20.52 |                    34.74 |                   15.38 |         -33.54 |        -32.46 |          29.19 |         -6.94 |       4.29 |
| 2. forced_informal / Ybar fija mes 96         | forced_informal | fixed       |         5.75 |          0.565 |          0.08 |                 7.65 |                5.7  |                     5.9  |                    4.56 |         -20.72 |        -26.49 |          17.11 |         -7.18 |       4.28 |
| 3. free / Ybar dinamica (Principal)           | free            | dynamic     |         5.44 |          0.567 |          0.05 |                24.5  |               10.44 |                    22.47 |                   10.21 |         -35.43 |        -36.62 |          30.2  |         -6.98 |       3.68 |
| 4. free / Ybar fija mes 96                    | free            | fixed       |         5.44 |          0.567 |          0.05 |                 4.21 |                3.41 |                     4.17 |                    3.4  |         -23.35 |        -28.48 |          19.55 |         -7.32 |       3.68 |

---

### Explicabilidad Metodológica

> **Descripción y Fuentes:**
> Evaluación de sensibilidad de la estructura econométrica de ITDT bajo cuatro combinaciones metodológicas: 1) forced_informal / dynamic (especificación histórica preliminar), 2) forced_informal / fixed (normalización Ȳ fija al mes 96), 3) free / dynamic (especificación principal microfundamentada tipo Hopenhayn 1992/Melitz 2003), 4) free / fixed (entrada libre con Ȳ fija).

> **Interpretación de Resultados:**
> 1. Invarianza cualitativa de conclusiones de política: En las cuatro variantes, B2 genera expansión severa de la brecha (+17.1 a +30.2 p.p.) y D logra la mayor formalización con cierre de brecha (−6.9 a −7.3 p.p.). 2. Coherencia microfundamentada: La regla de entrada libre reduce los cierres artificiales en B2 (de 52.19% a 24.50%/año) y mejora el ajuste fuera de muestra LOCO a 3.68 p.p. (frente a 4.29 p.p. en entrada forzada). 3. Ausencia de salida exógena: Las empresas cierran únicamente por insolvencia económica real (beneficio neto strictly negative con probabilidad mensual de liquidación del 10%).
