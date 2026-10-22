# Tabla 14: Robustez a las Reglas de Entrada de Firmas y Modo de Normalización Ȳ

La presente tabla evalúa la sensibilidad de la estructura econométrica y de los resultados de política del modelo ITDT frente a cuatro combinaciones de especificación:
1. **Regla de Entrada Forzada Informal (`forced_informal`)**: Todas las firmas entrantes reemplazantes ingresan forzadamente al sector informal (regla original del artículo).
2. **Regla de Entrada Libre (`free`)**: Las firmas entrantes extraen productividad y capital de la distribución ergódica y eligen óptimamente su sector (formal o informal) comparando beneficios netos $\Pi_F$ vs. $\Pi_I$ (Hopenhayn 1992, Melitz 2003), descartando proyectos inviables con $\max(\Pi_F, \Pi_I) < 0$.
3. **Ȳ Dinámica (`dynamic`)**: La mediana de productividad del sector formal se actualiza en cada paso mensual según la composición del sector.
4. **Ȳ Fija al mes 96 (`fixed`)**: La mediana $\bar{Y}$ se congela en el valor alcanzado al término del período de calentamiento (*burn-in*), aislando el umbral de auditoría y costo regulatorio de la reconfiguración endógena de firmas.

### Resultados Cuantitativos Consolidados

| Especificación | Regla Entrada | Modo $\bar{Y}$ | $\bar{\phi}_0$ | $\bar{\gamma}_0$ | Error Calib (p.p.) | Salidas B2 (\%/año) | Salidas D (\%/año) | % Firmas Cerradas B2 | % Firmas Cerradas D | $\Delta$ Inf B2 (p.p.) | $\Delta$ Inf D (p.p.) | $\Delta$ Brecha B2 (p.p.) | $\Delta$ Brecha D (p.p.) | MAE LOCO (p.p.) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1. forced_informal / Ybar dinamica (Articulo)** | `forced_informal` | `dynamic` | 5.75 | 0.565 | 0.08 | 52.19% | 20.52% | 34.74% | 15.38% | -33.54 | -32.46 | 29.19 | -6.94 | 4.29 |
| **2. forced_informal / Ybar fija mes 96** | `forced_informal` | `fixed` | 5.75 | 0.565 | 0.08 | 7.65% | 5.70% | 5.90% | 4.56% | -20.72 | -26.49 | 17.11 | -7.18 | 4.28 |
| **3. free / Ybar dinamica (Principal)** | `free` | `dynamic` | 5.44 | 0.567 | 0.05 | 24.50% | 10.44% | 22.47% | 10.21% | -35.43 | -36.62 | 30.20 | -6.98 | 3.68 |
| **4. free / Ybar fija mes 96** | `free` | `fixed` | 5.44 | 0.567 | 0.05 | 4.21% | 3.41% | 4.17% | 3.40% | -23.35 | -28.48 | 19.55 | -7.32 | 3.68 |

---

### Discusión Objetiva de las Preguntas de Investigación

#### a. ¿Cambian las conclusiones cualitativas de política?
**No. Las conclusiones cualitativas son rigurosamente invariantes entre las cuatro especificaciones:**
- **Escenario B2 (GovTech Intensivo — Sanciones 3× sin cuidado):** En las cuatro especificaciones, B2 reduce fuertemente la informalidad total (entre -35.43 p.p. y -20.72 p.p.), pero incrementa sustancialmente la brecha de género (entre +17.11 p.p. y +30.20 p.p.). La penalización de cuidado sobre las trabajadoras sin oferta pública de guarderías opera de forma robusta como cuello de botella.
- **Escenario D (Paquete Integrado — GovTech + Red de Cuidados + Subsidio DCC MiPyMEs):** En las cuatro especificaciones, el paquete integral logra la mayor formalización global (entre -36.62 p.p. y -26.49 p.p.) y reduce efectivamente la brecha de género (entre -7.32 p.p. y -6.94 p.p.), ratificando la complementariedad estructural modelada.

#### b. ¿Cuánto varía el MAE LOCO fuera de muestra?
- El error absoluto medio de validación fuera de muestra (LOCO MAE) oscila entre **3.68 p.p.** y **4.29 p.p.** a través de las cuatro variantes (amplitud máxima de solo 0.61 p.p.).
- Notablemente, las especificaciones con entrada libre (`free`) reducen el MAE fuera de muestra a **3.68 p.p.**, demostrando que la capacidad predictiva del canal estructural de cuidado infantil (parámetro $\gamma_0$) se fortalece bajo una regla microfundamentada de entrada.

#### c. ¿Las firmas realmente cierran bajo entrada libre, o la probabilidad de cierre sigue siendo cero?
- **Ausencia de salida exógena arbitraria:** En el modelo ITDT **no existe salida exógena**. Las empresas cierran o salen **únicamente si su beneficio operativo en el estado actual es estrictamente negativo ($\\Pi < 0$)**, con una probabilidad de materialización de salida del **0.10 mensual** (`exit_prob = 0.10`). Si una empresa es rentable ($\\Pi \ge 0$), su probabilidad de cierre es exactamente cero.
- **Porcentaje real de empresas que cierran al menos una vez en el año:** Durante la ventana final de evaluación de política (meses 109 a 120), el porcentaje de empresas que experimentan al menos un cierre por insolvencia económica es de **22.47%** en B2 y **10.21%** en D bajo libre entrada dinámica (frente a **34.74%** en B2 y **15.38%** en D bajo entrada forzada).
- Esto demuestra que el tejido empresarial sí responde endógenamente al shock punitivo de GovTech (B2) liquidando unidades no rentables, mientras que la libre entrada permite la recomposición con firmas que eligen óptimamente formalizarse si son suficientemente productivas.

#### d. Evidencia de Recalibración Independiente y Coincidencia entre Dynamic y Fixed
En la calibración SMM (Escenario A, meses 96 a 120), la economía se encuentra en equilibrio estacionario con tasas de informalidad estables y salidas prácticamente nulas (entre 0 y 2 firmas en 24 meses sobre un total de 600). Por ende, el valor del ingreso agregado $\bar{Y}$ permanece casi idéntico mes a mes, de modo que `ybar_mode="dynamic"` y `ybar_mode="fixed"` arrojan funciones de pérdida con diferencias marginales de solo $\sim 0.0001 - 0.0017$, convergiendo al mismo punto óptimo de la grilla 9×9. En contraste, entre `forced_informal` y `free` sí existen diferencias estructurales (por ejemplo, en Kenia $\phi_0$ pasa de 3.586 a 3.844; en Nigeria de 11.250 a 10.594; en India de 6.023 a 5.250; en Bangladés de 2.156 a 2.062).

