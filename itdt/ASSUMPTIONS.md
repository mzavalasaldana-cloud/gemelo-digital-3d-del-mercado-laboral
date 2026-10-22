# Supuestos Metodológicos de Implementación (ITDT)

Este documento registra de manera transparente y explícita las decisiones de diseño tomadas para aquellos aspectos operacionales que **el artículo científico no especifica formalmente**. En ningún caso se atribuyen estas decisiones al texto del artículo; son criterios razonables de ingeniería económica adoptados para garantizar la completitud, reproducibilidad y estabilidad estocástica de la simulación.

---

## 1. Distribución de la Alfabetización Digital ($K_{dig,i}$) y Brecha por Sexo

- **Lo que el artículo indica:**  
  La Sección 3.2 establece que cada trabajador posee un atributo de alfabetización digital $K_{dig,i} \in [0, 1]$, pero no define su función de distribución paramétrica, sus momentos ni si existe una disparidad sistemática entre hombres y mujeres.

- **Criterio adoptado:**  
  Modelamos $K_{dig,i}$ mediante una relación lineal con determinantes sociodemográficos más un término de perturbación gaussiana, acotado estrictamente en el intervalo $[0, 1]$:
  $$K_{dig,i} = \text{clip}\left(0.20 + 0.25 \cdot e_i - 0.15 \cdot r_i - 0.05 \cdot g_i + \nu_i, \; 0.0, \; 1.0\right), \quad \nu_i \sim \mathcal{N}(0, 0.10^2)$$
  
- **Justificación:**  
  1. **Retorno a la educación ($+0.25 \cdot e_i$):** La evidencia empírica internacional de la UIT y la UNESCO confirma que los años de escolaridad son el predictor más robusto de habilidades digitales básicas.
  2. **Penalización rural ($-0.15 \cdot r_i$):** Captura el déficit estructural de conectividad e infraestructura en zonas rurales en economías en desarrollo.
  3. **Brecha de género moderada ($-0.05 \cdot g_i$):** Introduce una brecha de 5 puntos porcentuales en detrimento de las mujeres, alineada con las estimaciones de la UIT para África Subsahariana y Asia del Sur.
  4. **Acotamiento:** La función `clip(..., 0, 1)` garantiza el cumplimiento estricto del dominio unitario $[0, 1]$.

---

## 2. Alfabetización Digital de la Empresa ($K_{dig,j}$)

- **Lo que el artículo indica:**  
  La Sección 3.3 define el Costo Digital de Cumplimiento ($DCC_j$) como:
  $$DCC_j = \bar{Y} \left[\phi_0 + \phi_1 \left(\frac{\bar{Y}}{Y_j}\right)^\eta (1 - K_{dig,j})\right]$$
  Sin embargo, el artículo no especifica cómo se genera o asigna la variable $K_{dig,j}$ para la firma $j$.

- **Criterio adoptado:**  
  Dado que la Sección 3.1 establece que *"Cada empresa tiene como dueño a un trabajador"*, asignamos directamente a la empresa la alfabetización digital de su dueño:
  $$K_{dig,j} = K_{dig,owner(j)}$$

- **Justificación:**  
  En micro, pequeñas y medianas empresas de economías emergentes, las capacidades de gestión tributaria y adopción de tecnología fiscal dependen casi exclusivamente de las habilidades personales de su titular o administrador. Este supuesto vincula orgánicamente la heterogeneidad educativa, rural y de género de los propietarios con los costos de formalización de sus empresas.

---

## 3. Momento del Cálculo de la Producción Mediana ($\bar{Y}$) y Modos de Escala (`ybar_mode`)

- **Lo que el artículo indica:**  
  El artículo estipula que $\bar{Y} = \text{mediana}(Y)$, pero no aclara si se calcula una única vez al inicio de la simulación o si se actualiza dinámicamente cada mes ante la entrada y salida de empresas.

- **Criterio adoptado (`ybar_mode`):**  
  El modelo implementa dos modos explícitos:
  1. `ybar_mode = "dynamic"` (modo activo por defecto): $\bar{Y}_t$ se calcula dinámicamente en cada mes $t$ sobre el conjunto completo de las $N_F = 600$ empresas activas, inmediatamente después de la resolución de quiebras y entrada de reemplazos (Paso 3) y antes de calcular las utilidades y demandas laborales del mes.
  2. `ybar_mode = "fixed"`: $\bar{Y}$ se evalúa dinámicamente durante el calentamiento ($t < 96$) y se congela al valor alcanzado al finalizar el mes 96 de burn-in ($\bar{Y}_{post-burnin}$), manteniéndose estrictamente fija durante los 120 meses de política.

- **Justificación:**  
  Al mantenerse constante el tamaño de la población de empresas ($N_F = 600$) y ser la productividad $A_j$ estacionaria, la mediana mensual es extraordinariamente estable. Sin embargo, la variante `fixed` permite comprobar que la reducción de informalidad bajo fiscalización GovTech no se debe a un desplazamiento espurio del umbral $\bar{Y}$.

---

## 4. Reglas de Entrada y Atributos de las Empresas Entrantes (`entry_rule`)

- **Lo que el artículo indica:**  
  La Sección 3.4 señala que *"Las empresas cuyo beneficio en su estado actual es negativo salen con probabilidad mensual 0.10 y son reemplazadas por entrantes informales, lo que mantiene constante la población de empresas"*. El artículo original forzaba a que toda unidad entrante naciera informal (`is_formal = False`), aun cuando sus condiciones de productividad y capital hicieran más rentable el registro formal inmediato.

- **Criterio adoptado (`entry_rule`):**  
  El modelo implementa dos reglas seleccionables en `FixedParameters`:
  1. `entry_rule = "free"` (nueva regla canónica por defecto):
     - Cuando una empresa sale por insolvencia ($\Pi < 0$ con probabilidad 0.10), la entrante extrae sus atributos iniciales ($A_{entrante} \sim \text{LogNormal}(0, 0.8^2)$, $z_{entrante} \sim \mathcal{N}(0, 1)$, $\ln K = 1 + 0.8 \ln A + 0.3 z$, dueño $\sim \text{Choice}(N_W)$).
     - Se calculan $\Pi_F$ y $\Pi_I$ con las condiciones de fiscalización ($D_{sys}$), sanciones y subsidios vigentes en ese mes específico.
     - **Condición de libre entrada:** Si $\max(\Pi_F, \Pi_I) < 0$, la unidad aspirante no ingresa a pérdidas y vuelve a extraer atributos, realizando hasta un máximo de 10 intentos. Si tras 10 extracciones consecutivas persiste $\max(\Pi_F, \Pi_I) < 0$, se registra con la última extracción.
     - La entrante inicia en el estado de mayor beneficio: formal si $\Pi_F > \Pi_I$, e informal en caso contrario.
     - *Justificación teórica:* Satisface la condición clásica de equilibrio con libre entrada de Hopenhayn (1992) y Melitz (2003), donde los agentes deciden su escala y régimen formal/informal en función de su productividad esperada y el entorno regulatorio vigente, eliminando el sesgo artificial de condenar a las nuevas empresas a la informalidad.
  2. `entry_rule = "forced_informal"`:
     - Réplica exacta de la especificación original del artículo: toda entrante se asigna forzosamente como informal (`is_formal = False`) con una única extracción, independientemente de sus beneficios.
     - Se preserva para auditoría y garantiza reproducibilidad exacta frente a las trayectorias iniciales.

- **Métrica Adicional de Cierres Empresariales:**
  Se registra adicionalmente el `"porcentaje de empresas que cierran al menos una vez en el año"` (`pct_firms_closed_at_least_once`), evaluado sobre la ventana final de meses 109 a 120 de la política. Esta métrica distingue la rotación bruta de empresas de la fracción de unidades del tejido empresarial afectadas por liquidación.

---

## 5. Estado Laboral Inicial y Período de Calentamiento

- **Lo que el artículo indica:**  
  El Apéndice A.1 señala que *"El estado inicial de cada empresa es formal si $\Pi_F > \Pi_I$"*, pero no especifica el estado inicial de los trabajadores previo al mes 1.

- **Criterio adoptado:**  
  1. **Empresas en $t=0$:** Se evalúan los beneficios iniciales $\Pi_F$ y $\Pi_I$ con $D_{sys}(0) = 0.30$. Aquellas con $\Pi_F > \Pi_I$ inician como formales.
  2. **Trabajadores en $t=0$:** Se computa la disposición de oferta ($U_F > U_I$) y las vacantes totales de las empresas formalizadas iniciales se asignan siguiendo los Pasos 4 a 6.
  3. **Disipación de condiciones iniciales:** La exigencia de **96 meses de calentamiento (burn-in)** antes de iniciar la evaluación de políticas garantiza que cualquier efecto de la condición inicial se haya disipado por completo, alcanzando el atractor ergódico estacionario del modelo.

---

## 6. Tratamiento de los Dueños de Empresas Formales

- **Lo que el artículo indica:**  
  La Sección 3.4 establece: *"Las vacantes de las empresas formales se asignan a los trabajadores dispuestos, ordenados por productividad con un ruido multiplicativo del 10 %; los dueños de empresas formales son formales"*.

- **Criterio adoptado:**  
  - Las vacantes $V = \sum_{j \in \text{Formal}} L_j$ se asignan entre todos los trabajadores que manifiesten disposición ($U_F > U_I$), ordenados por su puntaje con ruido $h_i \cdot (1 + \text{Uniform}(-0.10, 0.10))$.
  - Posteriormente, se asegura que los trabajadores identificados como dueños de al menos una empresa formal tengan su estado fijado como formal (`worker_is_formal[owner] = True`), reconociendo su condición de empleadores formales en la economía.
