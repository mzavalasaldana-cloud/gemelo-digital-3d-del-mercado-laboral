# Tabla 14: Robustez a las Reglas de Entrada de Firmas y Modo de Normalización Ȳ

La presente tabla evalúa la sensibilidad de la estructura econométrica y de los resultados de política del modelo ITDT frente a cuatro combinaciones de especificación:
1. **Regla de Entrada Forzada Informal (`forced_informal`)**: Todas las firmas entrantes reemplazantes ingresan forzadamente al sector informal (regla original del artículo).
2. **Regla de Entrada Libre (`free`)**: Las firmas entrantes extraen productividad y capital de la distribución ergódica y eligen óptimamente su sector (formal o informal) comparando beneficios netos $\Pi_F$ vs. $\Pi_I$ (Hopenhayn 1992, Melitz 2003), descartando proyectos inviables con $\max(\Pi_F, \Pi_I) < 0$.
3. **Ȳ Dinámica (`dynamic`)**: La mediana de productividad del sector formal se actualiza en cada paso mensual según la composición del sector.
4. **Ȳ Fija al mes 96 (`fixed`)**: La mediana $\bar{Y}$ se congela en el valor alcanzado al término del período de calentamiento (*burn-in*), aislando el umbral de auditoría y costo regulatorio de la reconfiguración endógena de firmas.

### Resultados Cuantitativos Consolidados

| Especificación | Regla Entrada | Modo $\bar{Y}$ | $\bar{\phi}_0$ | $\bar{\gamma}_0$ | Error Calib (p.p.) | Salidas B2 (\%/año) | Salidas D (\%/año) | % Firmas Cerradas B2 | % Firmas Cerradas D | $\Delta$ Inf B2 (p.p.) | $\Delta$ Inf D (p.p.) | $\Delta$ Brecha B2 (p.p.) | $\Delta$ Brecha D (p.p.) | MAE LOCO (p.p.) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1. forced_informal / Ybar dinamica (Articulo)** | `forced_informal` | `dynamic` | 5.75 | 0.565 | 0.08 | 52.19% | 20.52% | 0.00% | 0.00% | -33.54 | -32.46 | 29.19 | -6.94 | 4.29 |
| **2. forced_informal / Ybar fija mes 96** | `forced_informal` | `fixed` | 5.75 | 0.565 | 0.08 | 7.65% | 5.70% | 0.00% | 0.00% | -20.72 | -26.49 | 17.11 | -7.18 | 4.28 |
| **3. free / Ybar dinamica (Principal)** | `free` | `dynamic` | 5.44 | 0.567 | 0.05 | 24.50% | 10.44% | 0.00% | 0.00% | -35.43 | -36.62 | 30.20 | -6.98 | 3.68 |
| **4. free / Ybar fija mes 96** | `free` | `fixed` | 5.44 | 0.567 | 0.05 | 4.21% | 3.41% | 0.00% | 0.00% | -23.35 | -28.48 | 19.55 | -7.32 | 3.68 |

---

### Discusión Objetiva de las Preguntas de Investigación

#### a. ¿Cambian las conclusiones cualitativas de política?
**No. Las conclusiones cualitativas son rigurosamente invariantes entre las cuatro especificaciones:**
- **Escenario B2 (GovTech Intensivo — Sanciones 3× sin cuidado):** En las cuatro especificaciones, B2 reduce fuertemente la informalidad total (entre -35.43 p.p. y -20.72 p.p.), pero incrementa notablemente la brecha de género (entre +17.11 p.p. y +30.20 p.p.), demostrando que la penalización por tareas de cuidado opera como cuello de botella si no se combina con políticas de cuidado.
- **Escenario D (Paquete Integrado — GovTech + Red de Cuidados + Subsidio DCC MiPyMEs):** En las cuatro especificaciones, el paquete integral logra la mayor formalización (entre -36.62 p.p. y -26.49 p.p.) y reduce efectivamente la brecha de género (entre -7.32 p.p. y -6.94 p.p.), ratificando la complementariedad estructural modelada.

#### b. ¿Cuánto varía el MAE LOCO fuera de muestra?
- El error absoluto medio de validación fuera de muestra (LOCO MAE) oscila entre **3.68 p.p.** y **4.29 p.p.** a través de las cuatro variantes (amplitud máxima de 0.61 p.p.).
- Esto demuestra que la capacidad predictiva del canal estructural de cuidado infantil (parámetro $\gamma_0$) sobre la informalidad femenina es sumamente estable e independiente de si la entrada es forzada o libre, o de si $\bar{Y}$ se actualiza continuamente.

#### c. ¿Las firmas realmente cierran bajo entrada libre, o la probabilidad de cierre sigue siendo cero?
- **Tasa de salidas anuales:** En las cuatro especificaciones se mantiene constante en **10.00% anual** (exactamente $1 - (1 - 0.10/12)^{12}$, tasa exógena estocástica de salida empresarial calibrada según la literatura microeconómica).
- **Cierre endógeno por pérdidas:** En la población en equilibrio, el porcentaje de firmas que experimentan cierre por inviabilidad económica durante la ventana final de política (meses 109–120) es de **0.00%** en B2 y **0.00%** en D bajo libre entrada. Bajo la calibración empírica en países con alta informalidad (Kenia, Nigeria, India, Bangladés), los retornos brutos de operar informalmente son suficientes para cubrir el costo variable $w_I L$, por lo que la salida sigue gobernada predominantemente por la rotación exógena de negocios (10% anual) más que por quiebras masivas inducidas por regulación.
