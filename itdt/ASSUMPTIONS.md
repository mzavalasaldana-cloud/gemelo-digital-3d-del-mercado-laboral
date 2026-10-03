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

## 3. Momento del Cálculo de la Producción Mediana ($\bar{Y}$)

- **Lo que el artículo indica:**  
  El artículo estipula que $\bar{Y} = \text{mediana}(Y)$, pero no aclara si se calcula una única vez al inicio de la simulación o si se actualiza dinámicamente cada mes ante la entrada y salida de empresas.

- **Criterio adoptado:**  
  $\bar{Y}_t$ se calcula **dinámicamente en cada mes $t$** sobre el conjunto completo de las $N_F = 600$ empresas activas, inmediatamente después de la resolución de quiebras y entrada de reemplazos (Paso 3) y antes de calcular las utilidades y demandas laborales del mes.

- **Justificación:**  
  Al mantenerse constante el tamaño de la población de empresas ($N_F = 600$) y ser la productividad $A_j$ estacionaria, la mediana mensual es extraordinariamente estable, al tiempo que preserva la consistencia macroeconómica endógena frente a choques de fiscalización o reestructuración empresarial.

---

## 4. Atributos de las Empresas Entrantes

- **Lo que el artículo indica:**  
  La Sección 3.4 señala que *"Las empresas cuyo beneficio en su estado actual es negativo salen con probabilidad mensual 0.10 y son reemplazadas por entrantes informales, lo que mantiene constante la población de empresas"*, sin detallar la distribución de atributos de las nuevas unidades.

- **Criterio adoptado:**  
  Cada nueva empresa entrante que sustituye a una unidad liquidada extrae sus atributos de las mismas distribuciones estructurales iniciales:
  1. Productividad intrínseca: $A_{entrante} \sim \text{LogNormal}(0, 0.8^2)$.
  2. Ruido de capital: $z_{entrante} \sim \mathcal{N}(0, 1)$, $\ln K_{entrante} = 1 + 0.8 \ln A_{entrante} + 0.3 z_{entrante}$.
  3. Dueño: Un trabajador extraído con probabilidad uniforme de la población activa $N_W$.
  4. Si la dueña es mujer: $\tilde{A}_{entrante} = A_{entrante} \cdot \max\left(10^{-6}, \; 1 - 0.5 \gamma_0 \frac{H_{care,dueña}}{48}\right)$.
  5. Demanda laboral y producción: $L_{entrante} = \min\left(40, \max\left(1, \text{round}\left(0.5 \tilde{A}_{entrante}^{1/(1-\alpha)}\right)\right)\right)$, $Y_{entrante} = 1.6 \tilde{A}_{entrante} L^\alpha K^{1-\alpha}$.
  6. Estado inicial: **Estrictamente informal** (`is_formal = False`), tal como prescribe el artículo.

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
