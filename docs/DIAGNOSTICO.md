# Diagnóstico Técnico y Comparativo Integral: Artículo ITDT vs. Código del Repositorio

**Rama:** `itdt-articulo`  
**Fecha:** Octubre 2026  
**Documento de referencia:** *ITDT: Un gemelo digital para la evaluación ex ante de políticas de formalización laboral y sus efectos distributivos por sexo* (`Claude outputs/ITDT_IntArtif_anonimo_v5.docx` / `extracted_article_full.txt`)

---


> [!IMPORTANT]
> **Criterio de Fidelidad Científica e Implementación:**
> 1. **Ecuaciones Canónicas:**
>    - **Utilidad formal (Sección 3.2):**
>      $$U_{i,F} = \ln\left[\omega_F h_i(1-\tau_w)\left(1 - \gamma_0 \frac{H_{care,i}}{48}\right) - c_{tr}(1+r_i)\right] + \beta + \varepsilon_i$$
>      donde $\beta$ y $\varepsilon_i$ operan estrictamente **fuera del logaritmo**.
>    - **Probabilidad de auditoría (Sección 3.3):**
>      $$P_{aud,j} = \left[1 + \exp\left(-\kappa\left(D_{syst}(t)\frac{Y_j}{\bar{Y}} - \theta_{th}\right)\right)\right]^{-1}$$
>      donde $\kappa$ multiplica a todo el binomio $\left(D_{syst}(t)\frac{Y_j}{\bar{Y}} - \theta_{th}\right)$ y $D_{syst}(t)$ modula únicamente la escala $Y_j/\bar{Y}$.
> 2. **Evaluaciones Reales de Calibración:** La bisección anidada $9 \times 9$ produce exactamente **81 evaluaciones** de la función objetivo por país (no 100); se reportará el número real obtenido al implementarse.
> 3. **Resultados Genuinos del Modelo:** No se debe optimizar artificialmente el código para forzar los tiempos de la Tabla 10 ni ninguna otra cifra del artículo. Los resultados (tiempos, memoria, momentos calibrados y tasas de informalidad) deben emerger de forma limpia, rigurosa y transparente de la ejecución del modelo.

## 1. Resumen Ejecutivo del Diagnóstico

El análisis exhaustivo del artículo de investigación y del estado actual del repositorio revela una **discrepancia estructural y metodológica fundamental**:

1. **La naturaleza del proyecto en el artículo:** Es un **modelo computacional basado en agentes (ABM - Agent-Based Model)** de economía laboral y cumplimiento tributario. Modela decisiones microeconómicas fundadas de trabajadores y firmas con racionalidad acotada (dinámica de Metropolis con recocido simulado), calibrado mediante el **Método de Momentos Simulados (SMM)** contra únicamente dos momentos macroeconómicos empíricos por país publicados por **ILOSTAT** (tasas de informalidad femenina y masculina) y parámetros de cuidados de la OIT (Addati et al., 2018). El artículo **no utiliza microdatos empíricos ni encuestas individuales**, y evalúa contrastes estadísticos rigurosos con semillas pareadas ($R=40$), pruebas $t$, Wilcoxon con corrección de Bonferroni, validación fuera de muestra Leave-One-Country-Out (LOCO) y bootstrap por conglomerados ($B=4000$).
2. **La implementación actual en el código:** El repositorio alberga una aplicación interactiva (Fullstack React/Three.js + FastAPI + Streamlit) diseñada como un visor 3D y demostrador de Machine Learning tabular supervisado. 
   - La "simulación" de agentes en `backend/simulation_engine.py` y `streamlit_app/simulation_engine.py` no ejecuta el modelo de agentes del artículo: es un motor cinemático/visual de partículas 3D (movimiento browniano en un plano $XZ$ y trayectorias orbitales trigonométricas hacia 5 firmas fijas). Las métricas macroeconómicas no emergen de las decisiones de los agentes, sino que se calculan mediante **fórmulas fijas heurísticas y lineales ad-hoc**.
   - El subsistema de analítica en `backend/ml_engine.py`, `src/data/aiEngineMockData.ts`, `src/data/mockData.ts` y `data_store/*.csv` implementa un flujo de clasificación supervisada (XGBoost / Random Forest sobre si un individuo es formal o informal), alimentado por **microdatos totalmente sintéticos/inventados** que simulan ser encuestas oficiales nacionales (PLFS de India, KISS de Kenia, NLSS de Nigeria, QLFS de Bangladés).
   - Ninguna de las ecuaciones formales del artículo (utilidad logarítmica con penalización de cuidados, Cobb-Douglas con demanda laboral, costo digital regresivo $DCC_j$, probabilidad de auditoría logística $P_{aud,j}$, regla de Metropolis $T_k = T_0 d^k$, calibración SMM por bisección anidada, escenarios A/B1/B2/C/D, ni el diseño inferencial) se encuentra actualmente implementada en el código.

---

## 2. Tabla Comparativa Integral: Artículo vs. Código

| Lo que dice el artículo | Lo que hace hoy el código | Archivo |
| :--- | :--- | :--- |
| **3.1 Arquitectura y Escala del Modelo**<br>• Sistema dinámico discreto mensual ($t$ = mes).<br>• Población de agentes: $N_W = 6\,000$ trabajadores y $N_F = 600$ empresas por país.<br>• Módulo de gobernanza $G$ que fija impuestos, sanciones, cobertura digital, subsidios y red de cuidados.<br>• Cada empresa tiene como dueño a un trabajador de la población.<br>• Quienes no obtienen vacante formal trabajan en empresas informales o por cuenta propia (informal).<br>• Horizonte temporal: 96 meses de calentamiento (burn-in) + 120 meses de aplicación de política (total 216 meses). | • Simula una población fija de 2,500 trabajadores (partículas) y solo 5 firmas fijas con coordenadas cartesianas arbitrarias (`MOCK_FIRMS_COORDS`).<br>• No existe el módulo de gobernanza $G$ estructurado.<br>• No hay concepto de dueño de empresa vinculado a la población trabajadora.<br>• La "dinámica" es una animación visual en bucle de 0 a 120 meses con velocidad de reproducción en frontend/backend.<br>• No hay período de calentamiento (burn-in) de 96 meses. | [simulation_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/backend/simulation_engine.py#L5-L115)<br>[simulation_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/streamlit_app/simulation_engine.py#L94-L157) |
| **3.2 Submodelo de Trabajadores**<br>• Atributos individuales: sexo $g_i \in \{0, 1\}$ ($s_F$ según país), educación $e_i \in \{0, 1, 2\}$, residencia rural $r_i \in \{0, 1\}$ (60% rural), alfabetización digital $K_{dig,i}$, preferencia formal $\varepsilon_i \sim \mathcal{N}(0, 0.3^2)$.<br>• Productividad individual: $h_i = \exp(0.35 e_i - 0.20 r_i + 0.45 z_i)$, normalizada a media 1.<br>• Horas de cuidado: $H_{care,i} \sim \mathcal{N}(30.9, 6^2)$ en mujeres y $\mathcal{N}(9.7, 4^2)$ en hombres (Addati et al. 2018).<br>• Utilidad formal:<br>$U_{i,F} = \ln\left[\omega_F h_i(1-\tau_w)\left(1 - \gamma_0 \frac{H_{care,i}}{48}\right) - c_{tr}(1+r_i)\right] + \beta + \varepsilon_i$<br>• Utilidad informal: $U_{i,I} = \ln(\omega_I h_i)$.<br>• Oferta laboral formal si $U_{i,F} > U_{i,I}$.<br>• Parámetros: $\omega_F=1.30$, $\omega_I=1.00$, $\tau_w=0.10$, $c_{tr}=0.08$, $\beta=0.25$. | • `backend/simulation_engine.py`: Los agentes son simples objetos `WorkerAgentSim` con atributos de animación: `id_num`, `sector`, `human_capital` (entero aleatorio 15–100), `formalization_month`, coordenadas `(x, y, z)` y velocidades de Brownian motion `(vx, vz)`. No tienen sexo, horas de cuidado, ruralidad ni preferencias $\varepsilon_i$.<br>• `streamlit_app/simulation_engine.py`: Genera atributos visuales como `gender` (asignado por residuo cíclico `i % 3`: "Femenino", "Masculino", "No binario"), `income_usd`, `social_capital`, `risk_tolerance`, `flexibility_pref`.<br>• **Ausencia total** de las utilidades $U_{i,F}$ y $U_{i,I}$, de la penalización por horas de cuidado $\gamma_0 \frac{H_{care,i}}{48}$, del costo de transporte rural $c_{tr}(1+r_i)$ y del valor de protección social $\beta$.<br>• La condición formal se determina de forma determinista mediante un mes asignado al azar (`formalization_month = 18 + (100 - hc)*1.1 + noise`). | [simulation_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/backend/simulation_engine.py#L32-L63)<br>[simulation_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/streamlit_app/simulation_engine.py#L122-L229) |
| **3.3 Submodelo de Empresas**<br>• Productividad $A_j \sim \text{LogNormal}(0, 0.8^2)$, capital $\ln K_j = 1 + 0.8 \ln A_j + 0.3 z_j$, y dueño extraído al azar.<br>• Penalización a dueñas mujeres: si la dueña es mujer, $A_j = A_j\left(1 - 0.5 \gamma_0 \frac{H_{care,owner}}{48}\right)$.<br>• Demanda laboral: $L_j = \min\{40, \max\{1, \text{round}(0.5 A_j^{1/(1-\alpha)})\}\}$ con $\alpha = 0.62$.<br>• Producción Cobb-Douglas: $Y_j = 1.6 A_j L_j^\alpha K_j^{1-\alpha}$.<br>• Beneficio formal: $\Pi_{j,F} = (1-\tau_c)Y_j - \omega_F(1+\tau_w)L_j - r K_j - DCC_j$.<br>• Beneficio informal: $\Pi_{j,I} = Y_j - \omega_I L_j - r_I K_j - P_{aud,j}(\mu_0 Y_j + \mu_1 Y_j^\xi)$.<br>• Costo digital regresivo: $DCC_j = \bar{Y}\left[\phi_0 + \phi_1 \left(\frac{\bar{Y}}{Y_j}\right)^\eta (1 - K_{dig,j})\right]$.<br>• Probabilidad de auditoría logística: $P_{aud,j} = \left[1 + \exp\left(-\kappa\left(D_{syst}(t)\frac{Y_j}{\bar{Y}} - \theta_{th}\right)\right)\right]^{-1}$.<br>• Parámetros: $\tau_c=0.20$, $r=0.08$, $r_I=0.16$, $\phi_1=0.30$, $\eta=0.42$, $\mu_0=0.25$, $\mu_1=0.02$, $\xi=1.35$, $\kappa=4.12$, $\theta_{th}=1.0$, $D_{sys0}=0.30$. | • En `backend/simulation_engine.py`: Solo existe una lista fija `MOCK_FIRMS_COORDS` con 5 posiciones `(x, z)` y alturas de prismas 3D (`height: 4.0 - 6.0`). No hay cálculo de producción $Y_j$, capital $K_j$, ni demanda laboral $L_j$.<br>• En `streamlit_app/data/mock_data.py` y `src/data/mockData.ts`: Existen 5 o 7 empresas con descripciones textuales inventadas ("Apex Synth & Tech Corp", "Vanguard Industrial Textiles", etc.) con campos estáticos (`sizeEmployees`, `productivityScore`, `formalizationCostUSD`, `taxComplianceRate`).<br>• **Ausencia total** de: función de producción Cobb-Douglas, beneficios $\Pi_{j,F}$ y $\Pi_{j,I}$, costo digital de cumplimiento $DCC_j$, función logística de auditoría $P_{aud,j}$, y penalización sobre dueñas mujeres por carga de cuidados. | [simulation_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/backend/simulation_engine.py#L12-L18)<br>[mock_data.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/streamlit_app/data/mock_data.py#L74-L155)<br>[mockData.ts](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/src/data/mockData.ts#L109-L281) |
| **3.4 Racionalidad Acotada y Dinámica**<br>• Frecuencia de revisión: cada mes, cada empresa revisa su estado con probabilidad 1/3.<br>• Ventaja relativa de formalidad: $\rho_j = (\Pi_{j,F} - \Pi_{j,I})/Y_j$.<br>• Regla de Metropolis con enfriamiento: Informal se formaliza con prob $\exp(\min\{\rho_j, 0\} / T_k)$; formal se informaliza con prob $\exp(\min\{-\rho_j, 0\} / T_k)$.<br>• Temperatura de recocido simulado: $T_k = T_0 d^k$, con $T_0 = 0.5$, $d = 0.85$, $k = \lfloor t/12 \rfloor$.<br>• Salida por quiebra: Si $\Pi_j < 0$ en su estado actual, quiebra con prob mensual 0.10 y es reemplazada por una entrante informal (población $N_F$ constante).<br>• Emparejamiento de vacantes: Las vacantes de empresas formales se asignan a trabajadores dispuestos ($U_{i,F} > U_{i,I}$), ordenados por productividad con ruido multiplicativo del 10%. Dueños de empresas formales son formales. | • No existe la regla de decisión de Metropolis ni el esquema de recocido simulado $T_k = T_0 d^k$.<br>• No existe probabilidad mensual de quiebra (0.10) ni reemplazo por entrantes.<br>• No existe asignación de vacantes laborales por ranking de productividad con ruido del 10%.<br>• En `backend/simulation_engine.py`: La transición de informal a formal es una simple interpolación geométrica del progreso de cada trabajador (`w.current_progress += (target_prog - w.current_progress) * 0.25`) y el cómputo de coordenadas espaciales `(x, y, z)` para su visualización.<br>• Las métricas agregadas (`informalityRate`, `giniIndex`, salarios, etc.) se calculan evaluando una fórmula polinómica determinista en `calculate_metrics()`, completamente desvinculada de decisiones de agentes. | [simulation_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/backend/simulation_engine.py#L165-L211)<br>[simulation_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/backend/simulation_engine.py#L224-L285)<br>[simulation_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/streamlit_app/simulation_engine.py#L232-L291) |
| **3.5 Datos y Calibración por SMM**<br>• Insumos empíricos: Únicamente las tasas de informalidad agregadas por sexo de ILOSTAT [2] (Kenia 2019, Nigeria 2024, India 2024, Bangladés 2023) y horas de cuidado de Addati et al. (2018). No se usan microdatos.<br>• Estimación por Método de Momentos Simulados (SMM): $\Theta_c = (\phi_0, \gamma_0) = \arg\min_\Theta [m_c^e - m_c^s(\Theta)]^\top W [m_c^e - m_c^s(\Theta)]$ con $W = I$.<br>• Momentos simulados $m_c^s$: promedio de $S=6$ simulaciones con semillas comunes (1000–1005), 96 meses de burn-in + 24 meses evaluados.<br>• Algoritmo de optimización: Bisección anidada (9 iteraciones externas sobre $\gamma_0 \in [0, 1.5]$ y 9 internas sobre $\phi_0 \in [0, 12]$ que igualan $M_c$), bisección anidada 9×9 que da 81 evaluaciones reales por país (el texto del artículo menciona 100 por posibles puntos de borde, pero el producto exacto es 9×9 = 81; al implementarse se reportará el número real obtenido sin forzar la cifra).<br>• Errores estándar Monte Carlo: 3 recalibraciones independientes con semillas 5000–5205.<br>• Valores estimados: Kenia ($\phi_0=3.08, \gamma_0=0.461$), Nigeria ($\phi_0=8.96, \gamma_0=0.620$), India ($\phi_0=4.84, \gamma_0=0.464$), Bangladés ($\phi_0=2.03, \gamma_0=0.763$). | • No existe el algoritmo SMM, ni la bisección anidada, ni la función de pérdida cuadrática, ni las 100 evaluaciones por país, ni las semillas comunes 1000–1005.<br>• En su lugar, el código contiene diccionarios fijos estáticos (`COUNTRY_BASELINES` en backend y `COUNTRY_PROFILES` en Streamlit/Frontend) con números hardcodeados que ni siquiera coinciden con las tasas del paper:<br>  - Kenia: informalidad base fijada en 82.7% o 83.2% (el paper reporta ILOSTAT F=90.19%, M=83.13%, Total=86.49%).<br>  - Nigeria: fijada en 92.9% o 88.5% (el paper reporta F=96.39%, M=89.92%, Total=93.18%).<br>  - India: fijada en 88.6% o 81.4% (el paper reporta F=91.93%, M=86.76%, Total=88.36%).<br>  - Bangladés: fijada en 84.9% (el paper reporta F=95.77%, M=78.08%, Total=84.19%).<br>• No existen en todo el código los parámetros estructurales calibrados $\phi_0$ y $\gamma_0$. | [simulation_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/backend/simulation_engine.py#L5-L10)<br>[mock_data.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/streamlit_app/data/mock_data.py#L7-L64)<br>[mockData.ts](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/src/data/mockData.ts#L30-L99) |
| **3.6 Validación y Modelos de Referencia**<br>• Validación dentro de muestra frente a 4 modelos estructurales recalibrados: E1 (agente representativo), E2 (ABM lewisiano), E3 (ITDT sin cuidado), E4 (ITDT con racionalidad perfecta).<br>• Validación fuera de muestra Leave-One-Country-Out (LOCO): para cada país $c$, estima un $\gamma_0$ común en rejilla de 0 a 1.2 usando solo los otros 3 países; predice la tasa femenina $F_c$ de $c$ y compara contra 4 referencias: Brecha media, Razón media, Regresión lineal sobre $s_F$ e ITDT sin cuidado (E3).<br>• Reporta MAE (ITDT = 4.84 p.p., Brecha media = 5.73, Razón media = 6.11, Regresión lineal = 7.55, ITDT sin cuidado = 6.02). | • `backend/ml_engine.py`: La función `run_stratified_cv` no tiene ninguna relación con la validación LOCO del modelo ABM. Ejecuta un `StratifiedKFold(n_splits=5)` de scikit-learn para entrenar un clasificador supervisado binario (`ESTADO_LABORAL`) con XGBoost, Random Forest o HistGradientBoosting sobre una tabla sintética.<br>• En el frontend (`src/data/aiEngineMockData.ts`): Se presentan métricas mock fijas de validación cruzada con matrices de confusión prefabricadas (`CV_PRESET_RESULTS`).<br>• **Ausencia total** de: validación LOCO país por país sobre el modelo de agentes, modelos de referencia E1–E4, y benchmarks analíticos (Brecha media, Razón media, Regresión lineal de la brecha). | [ml_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/backend/ml_engine.py#L409-L605)<br>[aiEngineMockData.ts](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/src/data/aiEngineMockData.ts#L164-L304) |
| **3.7 Escenarios de Política (A, B1, B2, C, D)**<br>• Tras 96 meses de burn-in, aplicación durante 120 meses:<br>  - **Escenario A (Status quo):** Cobertura digital crece 0.15 p.p./mes ($+0.0015$/mes).<br>  - **Escenario B1 (GovTech moderado):** $\kappa \times 2.5$, crecimiento de $D_{syst} \times 3$, facturación electrónica obligatoria ($\phi_1 \times 1.5$).<br>  - **Escenario B2 (GovTech intensivo):** B1 con sanciones $\mu_0, \mu_1 \times 3$.<br>  - **Escenario C (Red de cuidados):** Reducción del 60% de $H_{care}$ para mujeres.<br>  - **Escenario D (Integrado):** B2 + C + subsidio del 80% al DCC de empresas con $L_j \le 10$ + $\beta \times 1.5$.<br>  - Barrido de intensidad de sanciones de $1\times$ a $4\times$ para localizar el umbral no lineal (Figura 5). | • En `backend/simulation_engine.py` y `streamlit_app/simulation_engine.py`, los escenarios son nombres inventados con efectos arbitrarios:<br>  - `SCENARIO_A_REGISTRATION`: reduce costo de registro un 80% y añade subsidio de $40/mes.<br>  - `SCENARIO_B_WORKER_SUBSIDY`: subsidio de $75/mes y capacitación del 60%.<br>  - `SCENARIO_E_AUTOMATION_SHOCK`: añade +10.5 de choque si el mes $\ge 20$.<br>  - `BASELINE`: todo en 0.<br>• El impacto en la tasa de informalidad no emerge de la simulación sino de una **fórmula lineal heurística directa**:<br>`net_inf = base_inf - reg*0.085 - sub*0.073 - train*0.065 - insp*0.045 + tax*0.35 + shift`.<br>• Ninguno de los escenarios reales del paper (A, B1, B2, C, D) ni el barrido de sanciones existen en el código. | [simulation_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/backend/simulation_engine.py#L148-L187)<br>[simulation_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/streamlit_app/simulation_engine.py#L43-L61) |
| **3.8 Diseño Inferencial y Pruebas Estadísticas**<br>• Unidad experimental: Réplica $r$ en país $c$.<br>• $R = 40$ réplicas por país y escenario con semillas comunes (20260–20299).<br>• Resultado por réplica: promedio de los meses 109–120.<br>• Por país: Diferencia media pareada frente a Escenario A, desviación estándar, estadístico $t$ con $df=39$ ($t = d_z \sqrt{R}$), $d_z$ de Cohen pareada, prueba de rangos con signo de Wilcoxon, y corrección de Bonferroni para familia de 20 contrastes por país (4 escenarios $\times$ 5 métricas: informalidad total, femenina, masculina, brecha y cierres de empresas).<br>• Efecto agregado: Intervalo de confianza del 95% por bootstrap por conglomerados en dos etapas ($B=4\,000$ iteraciones) remuestreando países y réplicas. | • El simulador corre una única ejecución determinista con fórmulas lineales o números pseudoaleatorios aislados; no realiza réplicas Monte Carlo ni usa semillas pareadas.<br>• No existen contrastes pareados frente a un escenario base.<br>• No se calcula el estadístico $t(39)$, ni Wilcoxon, ni la corrección de Bonferroni para 20 contrastes, ni el tamaño del efecto $d_z$ de Cohen.<br>• No existe el algoritmo de bootstrap por conglomerados en dos etapas ($B=4000$).<br>• En `src/data/aiEngineMockData.ts`: Existe una tabla estática inventada `STATISTICAL_TESTS_RESULTS` con pruebas que nada tienen que ver con el diseño inferencial del paper (Kolmogorov-Smirnov de salario y horas, Shapiro-Wilk de log-productividad, VIF de multicolinealidad y paridad demográfica). | [simulation_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/backend/simulation_engine.py#L213-L293)<br>[aiEngineMockData.ts](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/src/data/aiEngineMockData.ts#L441-L487)<br>[ml_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/backend/ml_engine.py#L18) |
| **3.9 Sensibilidad, Robustez, Costo y Equidad**<br>• Sensibilidad: perturbación de $\pm 20\%$ en 7 parámetros ($\phi_0, \phi_1, \eta, \mu_0, \kappa, \gamma_0, H_{care}^{mujeres}$) con 8 réplicas por país (32 por celda) y cálculo de elasticidades $\varepsilon = \frac{\Delta y / y_0}{\Delta p / p_0}$.<br>• Robustez estructural: reestimación con función de producción CES ($\sigma = 0.5$ y $\sigma = 1.5$) y choque exógeno de demanda ($-5\%$ de $A_j$ en mes 60).<br>• Costo computacional: benchmarking de tiempo por réplica y memoria RAM para $N_W \in \{3000, 6000, 12000, 24000\}$ y $N_F \in \{300, 600, 1200, 2400\}$.<br>• Equidad del modelo: verificación de gradientes no calibrados (educación decreciente, rural > urbano, quintil de productividad). | • No existe ninguna rutina de perturbación de parámetros ni cálculo de elasticidades $\varepsilon$.<br>• No existe implementación de función de producción CES ni inyección de choque en mes 60.<br>• No existe script ni test de evaluación de escalabilidad computacional.<br>• No se computan ni contrastan gradientes distributivos no calibrados sobre los resultados del modelo de agentes. | Todo el repositorio (código ausente) |
| **Datos Usados y Filosofía Empírica**<br>• El artículo utiliza **única y exclusivamente estadísticas macroeconómicas agregadas** de ILOSTAT [2] (tasas de informalidad nacional por sexo) y promedios de horas de cuidado de Addati et al. (2018).<br>• **El artículo declara explícitamente:** *"No se usan microdatos ni información identificable"* (Sección 3.5 y Declaraciones éticas). | • El repositorio asume falsamente que el sistema se alimenta de **microdatos a nivel individual de encuestas de hogares**.<br>• En `backend/ml_engine.py`, la función `generate_country_preset_dataset` genera artificialmente cientos de miles de registros de supuestos microdatos con decenas de variables inventadas (`INGRESO_NETO_DIA`, `HORAS_SEMANA`, `APORTE_SEG_SOC`, `M_PESA_TURNOVER_MONTH`, `CAC_REGISTRATION`, `GENERATOR_COST_RATIO`, `RMG_SUBCONTRACT`, etc.).<br>• Los archivos CSV en `data_store/` son datasets fabricados con distribuciones estadísticas aleatorias que pretenden ser las encuestas PLFS (India), KISS (Kenia), NLSS (Nigeria) y QLFS (Bangladés). | [ml_engine.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/backend/ml_engine.py#L46-L196)<br>[main.py](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/backend/main.py#L91-L101)<br>[data_store/](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/data_store) |

---

## 3. Inventario Crítico de Datos Inventados y Fórmulas Fijas

A continuación se detalla exactamente qué partes del sistema emplean datos artificiales, números mágicos o ecuaciones heurísticas fijadas a mano, contrastando su falsedad frente a la formulación del artículo:

### 3.1. `backend/simulation_engine.py`
1. **Líneas 5–10 (`COUNTRY_BASELINES`):**
   ```python
   COUNTRY_BASELINES = {
       "KENYA": {"baseInformality": 82.7, "baseGini": 0.408},
       "NIGERIA": {"baseInformality": 92.9, "baseGini": 0.351},
       "INDIA": {"baseInformality": 88.6, "baseGini": 0.357},
       "BANGLADESH": {"baseInformality": 84.9, "baseGini": 0.324},
   }
   ```
   *Problema:* Datos estáticos inventados/aproximados. El paper utiliza las tasas exactas de ILOSTAT: Kenia (F: 90.19, M: 83.13, T: 86.49), Nigeria (F: 96.39, M: 89.92, T: 93.18), India (F: 91.93, M: 86.76, T: 88.36), Bangladés (F: 95.77, M: 78.08, T: 84.19).
2. **Líneas 12–18 (`MOCK_FIRMS_COORDS`):**
   5 empresas con coordenadas espaciales fijas (`x: 0.0, z: 0.0, height: 6.0`, etc.) creadas con el único fin de servir como centros de rotación gráfica 3D.
3. **Líneas 48–61 (`WorkerAgentSim`):**
   Atributos puramente cinemáticos (`informal_x`, `informal_z`, `vx`, `vz`, `orbit_radius`, `orbit_speed`, `orbit_angle`). No existe el modelo de capital humano, costo de transporte ni preferencia de cuidados del paper.
4. **Líneas 170–187 (`calculate_metrics`):**
   Fórmula fija polinómica con pesos arbitrarios:
   ```python
   phase_progress = min(1.0, math.pow(self.month / 120.0, 0.75))
   reg_impact = ((self.policy_params["registrationCostReduction"] / 100.0) * 8.5) * phase_progress
   sub_impact = ((self.policy_params["smeSubsidyUSDMonth"] / 150.0) * 11.0) * phase_progress
   train_impact = ((self.policy_params["skillsTrainingCoverage"] / 100.0) * 6.5) * phase_progress
   insp_impact = ((self.policy_params["smartInspectionCoverage"] / 100.0) * 4.5) * phase_progress
   tax_burden = ((self.policy_params["socialProtectionTax"] - 25.0) * 0.35 * phase_progress) ...
   net_informality = max(32.0, min(96.0, base_informality - reg_impact - sub_impact - train_impact - insp_impact + tax_burden + scenario_shift))
   ```
   *Problema:* Los coeficientes (`8.5`, `11.0`, `6.5`, `4.5`, `0.35`, `0.0014`) son números mágicos inventados. Las tasas no emergen de las decisiones agregadas de los agentes.

---

### 3.2. `streamlit_app/simulation_engine.py`
1. **Líneas 28–77 (`calculate_structural_metrics`):**
   Idéntica fórmula heurística artificial que en el backend. Además, inventa salarios e ingresos mediante fórmulas fijas:
   ```python
   avg_formal_wage = profile["formalWageBaselineUSD"] + (skills_cov / 100.0) * 6.0 + phase_progress * 9.0
   avg_informal_wage = profile["informalWageBaselineUSD"] + (sme_subsidy / 150.0) * 3.5 + phase_progress * 2.5
   fiscal_revenue = (formal_count * (tax_rate / 100.0) * avg_formal_wage * 30 * 12) / 1_000_000.0
   policy_cost = (sme_subsidy * 1200 + skills_cov * 800 + reg_reduction * 350) / 1000.0
   decent_work_index = int(round(max(20, min(95, 55 + (100.0 - net_informality) * 0.42))))
   ```
2. **Líneas 115–229 (`generate_worker_population`):**
   Población de 2500 partículas con atributos aleatorios falsos:
   - Géneros asignados con `genders[i % 3]` ("Femenino", "Masculino", "No binario"), cuando el modelo del paper es estrictamente bivariado en género ($g_i \in \{0, 1\}$) para calibrar con ILOSTAT.
   - Atributos inventados: `social_capital`, `risk_tolerance`, `flexibility_pref`, `formalization_prob`.
   - Fecha de formalización inventada: `base_month = int(round(18 + (100.0 - human_capital) * 1.1 + (random.random() - 0.5) * 16))`.

---

### 3.3. `src/data/aiEngineMockData.ts`
1. **Líneas 35–42 (`EDA_KPIS`):**
   ```typescript
   export const EDA_KPIS = {
     dataQuality: 98.4,
     totalRecords: 1245900,
     totalVariables: 42,
     nullPercentage: 0.8,
     imputationMethod: 'MICE Multivariada (Iterative SVD)',
     surveySource: 'Microdatos Armonizados de Encuestas Continuas de Hogares y Empleo',
   };
   ```
   *Problema:* Cifras inventadas de calidad de datos, registros (1.24 millones) y método de imputación. En el paper no existen microdatos ni 42 variables.
2. **Líneas 44–80 (`EDA_HISTOGRAMS`):**
   Distribuciones inventadas de salarios mensuales en USD, horas trabajadas y educación, con conteos fijos (`formalCount: 12000, informalCount: 145000`, etc.).
3. **Líneas 91–98 (`CORRELATION_MATRIX`):**
   Matriz simétrica de $6 \times 6$ con valores correlacionales inventados a mano (`0.68, 0.62, 0.74, 0.84`, etc.).
4. **Líneas 198–304 (`CV_PRESET_RESULTS`):**
   Resultados prefijados de validación cruzada para XGBoost, LightGBM y Random Forest (Accuracy: 92.6%, Precision: 92.4%, Recall: 90.1%, F1: 91.2%, ROC-AUC: 94.8%). Presentan supuestas matrices de confusión con 48,250 verdaderos positivos y 48,520 verdaderos negativos.
5. **Líneas 322–393 (`EXTENDED_COHORTS`):**
   Cinco cohortes inventadas con valores SHAP falsos simulados (`shapValue: '+0.34'`, `shapValue: '+0.41'`).
6. **Líneas 396–429 (`OPTIMAL_HYPERPARAMS_JSON`):**
   JSON simulado de optimización bayesiana con Optuna para XGBoost con GPU CUDA, completamente estático.
7. **Líneas 441–487 (`STATISTICAL_TESTS_RESULTS`):**
   Pruebas estadísticas con valores p falsos (`Kolmogorov-Smirnov D = 0.482, p < 0.00001`, `Shapiro-Wilk W = 0.988`, `VIF = 2.84`, `Paridad Demográfica Ratio = 0.962`). Ninguna de estas pruebas corresponde al diseño inferencial del paper (Sección 3.8: pruebas $t$ pareadas, Wilcoxon con Bonferroni y cluster bootstrap).

---

### 3.4. `src/data/mockData.ts`
1. **Líneas 30–99 (`COUNTRY_PROFILES`):**
   Perfiles de países con tasas de informalidad erróneas (Kenia 83.2%, Nigeria 88.5%, India 81.4%, Bangladés 84.9%), parámetros de relieve para shaders de Three.js (`peakFrequency`, `valleyDepth`, `colorTint`), y nombres ficticios de encuestas oficiales ("KNBS-ILFS", "NBS-NLFS", "PLFS MoSPI", "BBS-LFS").
2. **Líneas 109–281 (`MOCK_FIRMS`):**
   Empresas con nombres corporativos de ficción ("Apex Synth & Tech Corp", "Metropolis Port Logistics Ltd", "Enjambre Micro-Talleres Jua Kali") y métricas estáticas (`productivityScore: 92`, `taxComplianceRate: 98`, `formalizationCostUSD: 2400`).
3. **Líneas 283–334 (`MOCK_ML_ALGORITHMS`):**
   Métricas estáticas de algoritmos de ML (XGBoost F1: 0.914, Random Forest F1: 0.887, Deep Residual Network F1: 0.928, Cox Proportional Hazards F1: 0.854).
4. **Líneas 375–428 (`MOCK_DATASETS`):**
   Metadatos ficticios de encuestas de hogares: supuestos 1,245,900 registros para India PLFS, 312,000 para Kenia KISS, 489,000 para Nigeria NLSS y 520,000 para Bangladés QLFS.
5. **Líneas 430–480 (`MOCK_USERS`):**
   Cuentas de usuario de muestra ("Dra. Amina Diallo", "Lic. Mateo Rossi", "Ing. Chen Wei").

---

### 3.5. `streamlit_app/data/mock_data.py`
1. **Líneas 7–64 (`COUNTRY_PROFILES`):**
   Versión en Python del diccionario de países con salarios base arbitrarios (`formalWageBaselineUSD: 27.4`, `informalWageBaselineUSD: 7.8`) y puntajes inventados (`iloComplianceScore: 58`).
2. **Líneas 74–160 (`MOCK_FIRMS`):**
   Lista de firmas formales e informales con coordenadas fijas en $[-10.0, 10.0]$ y colores `#00f0ff` para Plotly 3D.
3. **Líneas 163–250 (`MOCK_COHORTS`, `MOCK_ML_METRICS`, `MOCK_DATASETS`):**
   Duplicación de las métricas inventadas de algoritmos de ML y cohortes para el entorno de Streamlit.

---

### 3.6. Los CSVs en `data_store/` generados por `generate_country_preset_dataset` en `backend/ml_engine.py`
En `backend/ml_engine.py` (Líneas 46–196), la función `generate_country_preset_dataset(preset_id)` fabrica artificialmente microdatos usando distribuciones de `numpy`:
- **`PLFS_India_Periodic_Labour_Force_Survey_2023-24.csv` (48,500 filas):**  
  Genera columnas aleatorias como:
  ```python
  ages = np.random.randint(18, 64, size=num_records)
  educ_years = np.clip(np.random.normal(8.5, 4.2, size=num_records).astype(int), 0, 20)
  human_capital = np.clip((educ_years / 20.0) * 80 + np.random.normal(12, 10, size=num_records), 5, 100)
  score = 0.05 * human_capital + 0.07 * educ_years - np.random.exponential(2.2, size=num_records)
  is_formal = (score > 2.8).astype(int)
  ```
  Añade etiquetas falsas como `INDUSTRY_NIC_2008` ('NIC-01 Agricultura', 'NIC-62 IT/BPO') y `VOCATIONAL_TRAINING` ('Formal ITI', 'No Formal').
- **`KNBS_Kenya_Informal_Sector_Survey_2024.csv` (38,000 filas):**  
  Genera microdatos sintéticos con columnas específicas como `JUA_KALI_CLUSTER` ('Kamukunji Metalworks', 'Gikomba Garments') y `M_PESA_TURNOVER_MONTH` (`ingreso * 28.0 * uniform(1.2, 3.5)`).
- **`NBS_Nigeria_National_Living_Standard_Survey_2023.csv` (42,000 filas):**  
  Genera columnas sintéticas como `CAC_REGISTRATION` ('Registrado CAC Formal') y `GENERATOR_COST_RATIO` (`uniform(0.08, 0.32) * 100`).
- **`BBS_Bangladesh_Labour_Force_Survey_2023-24.csv` (36,000 filas):**  
  Genera columnas inventadas como `RMG_SUBCONTRACT` ('Export Tier 1', 'Subcontrato Informal Tier 3') y `RURAL_MICROFINANCE` ('Grameen / BRAC', 'Prestamista Informal').
- **`benchmark_microdatos_armonizados.csv` (15,420 filas):**  
  Submuestra sintética del generador de Kenia guardada automáticamente al iniciar el servidor en `backend/main.py`.

*Conclusión sobre los datos:* Estos archivos simulan ser bases de datos oficiales gubernamentales de encuestas continuas de empleo, pero son **100% inventados mediante generadores pseudoaleatorios**. El artículo científico nunca utilizó microdatos de encuestas, sino únicamente los 8 momentos macroeconómicos observados de ILOSTAT (Tabla 2 del artículo).

---

## 4. Matriz de Parámetros Estructurales: Artículo (Tabla A1) vs. Código

| Parámetro | Símbolo | Valor en el Artículo | Valor / Estado en el Código Actual | Estado |
| :--- | :---: | :---: | :---: | :---: |
| Participación salarial | $\alpha$ | $0.62$ | Inexistente (no hay función de producción) | ❌ Ausente |
| Contribución del trabajador | $\tau_w$ | $0.10$ | Deslizador con defecto $15.0$ o $12.0$ | ⚠️ Distorsionado |
| Impuesto a sociedades | $\tau_c$ | $0.20$ | Inexistente (fórmulas fijas usan $0.18$) | ❌ Ausente |
| Salario formal unitario | $\omega_F$ | $1.30$ | Fórmulas fijas usan salarios en USD ($28.5$) | ❌ Ausente |
| Salario informal unitario | $\omega_I$ | $1.00$ | Fórmulas fijas usan salarios en USD ($8.2$) | ❌ Ausente |
| Costo de transporte base | $c_{tr}$ | $0.08$ (doble en rural) | Inexistente | ❌ Ausente |
| Valor de protección social | $\beta$ | $0.25$ | Inexistente | ❌ Ausente |
| Tasa de interés formal | $r$ | $0.08$ | Inexistente | ❌ Ausente |
| Tasa de interés informal | $r_I$ | $0.16$ | Inexistente | ❌ Ausente |
| Componente regresivo DCC | $\phi_1, \eta$ | $0.30, 0.42$ | Inexistente | ❌ Ausente |
| Sanción base informal | $\mu_0$ | $0.25$ | Inexistente | ❌ Ausente |
| Sanción no lineal | $\mu_1, \xi$ | $0.02, 1.35$ | Inexistente | ❌ Ausente |
| Sensibilidad de detección | $\kappa$ | $4.12$ | Inexistente | ❌ Ausente |
| Umbral de detección | $\theta_{th}$ | $1.0$ | Inexistente | ❌ Ausente |
| Cobertura digital inicial | $D_{sys0}$ | $0.30$ | Inexistente | ❌ Ausente |
| Crecimiento cobertura status quo | $\Delta D_{syst}$ | $0.0015$ / mes ($0.15$ p.p./mes) | Inexistente | ❌ Ausente |
| Temperatura inicial de recocido | $T_0$ | $0.50$ | Inexistente | ❌ Ausente |
| Tasa de enfriamiento | $d$ | $0.85$ (anual, $k=\lfloor t/12 \rfloor$) | Inexistente | ❌ Ausente |
| Horas cuidado mujeres | $H_{care}^{mujeres}$ | $\mathcal{N}(30.9, 6^2)$ | Inexistente | ❌ Ausente |
| Horas cuidado hombres | $H_{care}^{hombres}$ | $\mathcal{N}(9.7, 4^2)$ | Inexistente | ❌ Ausente |
| Probabilidad de revisión mensual | $p_{rev}$ | $1/3$ ($0.333$) | Inexistente | ❌ Ausente |
| Probabilidad mensual de quiebra | $p_{exit}$ | $0.10$ si $\Pi < 0$ | Inexistente | ❌ Ausente |
| Calibrado: Costo fijo cumplimiento | $\phi_0$ | Kenia: 3.08, Nigeria: 8.96, India: 4.84, BD: 2.03 | Inexistente | ❌ Ausente |
| Calibrado: Penalización de cuidado | $\gamma_0$ | Kenia: 0.461, Nigeria: 0.620, India: 0.464, BD: 0.763 | Inexistente | ❌ Ausente |

---

## 5. Hoja de Ruta para Reconstruir el Simulador Fiel al Artículo

Para que el repositorio refleje con fidelidad científica el artículo `ITDT_IntArtif_anonimo_v5.docx`, los siguientes módulos deberán ser desarrollados e integrados:

1. **Implementar el Núcleo ABM Vectorizado en Python/NumPy (`itdt_abm_core.py`):**
   - Agentes trabajadores ($N_W = 6000$): inicialización con proporciones $s_F$, educación $(0.45, 0.40, 0.15)$, ruralidad ($60\%$), $h_i = \exp(0.35 e_i - 0.20 r_i + 0.45 z_i)$, $H_{care} \sim \mathcal{N}(\mu, \sigma^2)$, y utilidades $U_{i,F}$ vs $U_{i,I}$.
   - Agentes firmas ($N_F = 600$): capital $K_j$, productividad $A_j$ con penalización a dueñas mujeres, demanda laboral $L_j$, Cobb-Douglas $Y_j = 1.6 A_j L_j^\alpha K_j^{1-\alpha}$, costos $DCC_j$, auditoría $P_{aud,j}$, y beneficios $\Pi_{j,F}$ vs $\Pi_{j,I}$.
   - Dinámica de Metropolis con recocido $T_k = 0.5 \times (0.85)^{\lfloor t/12 \rfloor}$, quiebras (10%) y emparejamiento por ranking de productividad con 10% de ruido.
   - Vectorización eficiente en NumPy para garantizar el rendimiento reportado en la Tabla 10 (~0.13 s por réplica de 216 meses).
2. **Implementar el Calibrador SMM (`itdt_smm_calibrator.py`):**
   - Algoritmo de bisección anidada (9 iteraciones externas sobre $\gamma_0 \in [0, 1.5]$, 9 internas sobre $\phi_0 \in [0, 12]$).
   - Función objetivo de momentos de ILOSTAT con semillas comunes (1000–1005).
   - Generación automática de la Tabla 2 y Figura 4 del artículo.
3. **Implementar la Validación LOCO y Benchmarks (`itdt_loco_validation.py`):**
   - Validación Leave-One-Country-Out con rejilla para $\gamma_0$ común.
   - Cálculo de benchmarks analíticos: Brecha media, Razón media, Regresión lineal e ITDT sin cuidado (E3).
   - Generación de las Tablas 3 y 4 del artículo.
4. **Implementar el Motor de Escenarios de Política e Inferencia (`itdt_policy_experiments.py`):**
   - Escenarios A, B1, B2, C y D con sus parámetros exactos.
   - $R = 40$ réplicas con semillas fijadas (20260–20299).
   - Pruebas estadísticas pareadas: $t(39)$, $d_z$ de Cohen, prueba de Wilcoxon con Bonferroni para los 20 contrastes por país.
   - Cluster bootstrap en dos etapas ($B=4000$) para efectos agregados.
   - Generación de Tablas 5, 6, 7 y Figuras 5, 6, 7.
5. **Implementar los Módulos de Sensibilidad, Robustez y Costo (`itdt_sensitivity_robustness.py`):**
   - Perturbación $\pm 20\%$ en los 7 parámetros y cálculo de elasticidades $\varepsilon$.
   - Reestimación con función CES ($\sigma=0.5, 1.5$) y choque de demanda en mes 60 (Tabla 9).
   - Benchmarking de costo computacional (Tabla 10).
   - Gradientes no calibrados por educación, ruralidad y quintiles (Tabla 12).
6. **Conectar el Backend FastAPI y el Frontend con los Resultados Reales:**
   - Exponer endpoints que sirvan los datos y trayectorias reales generados por el motor ITDT calibrado.
   - Permitir que el visualizador 3D y Streamlit reflejen las variables y trayectorias auténticas del modelo, erradicando los datos inventados y las fórmulas mágicas.
