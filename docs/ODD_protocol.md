# Protocolo ODD del modelo ITDT

Descripción del modelo basado en agentes ITDT (*Informality and Taxation Digital Twin*) según el protocolo ODD (*Overview, Design concepts, Details*) en su segunda actualización (Grimm et al., 2020, *JASSS* 23(2), 7). Todo lo que sigue se corresponde con el código de `itdt/model.py`, `itdt/parameters.py`, `itdt/metrics.py`, `itdt/calibrate.py` y `itdt/experiments.py`; si el código cambia, este documento debe actualizarse.

## 1. Propósito y patrones

**Propósito.** Evaluar *ex ante* políticas de formalización (fiscalización digital, red de cuidados y una política integrada) según su efecto sobre la informalidad total y por sexo, la brecha de género, el cierre de empresas y la recaudación, en Kenia, Nigeria, India y Bangladés. También permite contrastar dos explicaciones del efecto de género: el costo digital regresivo (H1) y la restricción de cuidado (H2).

**Patrones que el modelo debe reproducir.**
- Las tasas de informalidad por sexo de ILOSTAT (EMP_NIFL_SEX_RT) de cada país: son los momentos de calibración.
- La tasa femenina de un país excluido, a partir de los otros tres (validación LOCO).
- La dirección de los gradientes de informalidad por educación y por zona de ILOSTAT, que no se usan en la calibración.

## 2. Entidades, variables de estado y escalas

**Trabajadores** (N_W = 6 000 por país):
- sexo g (1 = mujer), con P(g = 1) = s_F (participación femenina en el empleo, ILOSTAT);
- educación e ∈ {0, 1, 2}, con probabilidades 0.45, 0.40 y 0.15;
- zona rural r ∈ {0, 1}, con P(r = 1) = 0.60;
- productividad h = exp(0.35e − 0.20r + 0.45z), con z ∼ N(0, 1), normalizada a media 1;
- horas semanales de cuidado H_care ∼ N(30.9, 6²) en mujeres y N(9.7, 4²) en hombres, truncadas en 0 (Addati et al., 2018);
- alfabetización digital K_dig = min{1, max{0, 0.20 + 0.25e − 0.15r − 0.05g + ν}}, con ν ∼ N(0, 0.1²);
- preferencia fija por el empleo formal ε ∼ N(0, 0.3²);
- estado laboral: formal o informal (incluye cuenta propia).

**Empresas** (N_F = 600 por país):
- productividad A ∼ LogNormal(0, 0.8²);
- capital ln K = 1 + 0.8 ln A + 0.3z, con z ∼ N(0, 1);
- dueño elegido al azar entre los trabajadores; la empresa hereda su K_dig;
- productividad efectiva Ã = A(1 − 0.5γ₀H_care/48) si la dueña es mujer, y Ã = A si es hombre;
- demanda laboral L = min{40, max{1, round(0.5Ã^(1/(1−α)))}};
- producción Y = 1.6ÃL^αK^(1−α) (o CES en la prueba de robustez);
- estado: formal o informal.

**Entorno (Estado):** cobertura digital D_sys(t), impuestos, contribuciones, sanciones, subsidio al costo digital y red de cuidados, según el escenario.

**Escalas.** Un paso es un mes. Cada simulación tiene 96 meses de calentamiento y 120 de política (216 en total). El espacio no es explícito: la posición de los agentes en la vista 3D de la interfaz es solo ilustrativa.

## 3. Visión general del proceso y programación

En cada mes t, y en este orden:

1. **Escenario.** Durante la política (t ≥ 96) se activan los instrumentos del escenario (A, B1, B2, C o D; ver 7.5).
2. **Entorno.** D_sys aumenta en su tasa mensual.
3. **Beneficios.** Se calculan Π_F y Π_I de todas las empresas (7.2).
4. **Revisión de estado.** Cada empresa revisa su estado con probabilidad 1/3 y aplica la regla de Metropolis (7.3).
5. **Salida y entrada.** Una empresa con beneficio negativo en su estado actual sale con probabilidad 0.10 y es reemplazada por una entrante (7.4). Luego se recalculan la producción y los beneficios.
6. **Vacantes formales.** Su número es la suma de L de las empresas formales. Se asignan a los trabajadores dispuestos (U_F > U_I), ordenados por h × (1 + u), con u ∼ U(−0.10, 0.10).
7. **Estado laboral.** Los dueños de empresas formales son formales; el resto de quienes no obtienen vacante formal es informal.
8. **Registro.** Se calculan las métricas del mes (7.6).

La actualización es sincrónica: todas las empresas revisan su estado con los beneficios calculados al inicio del mes.

## 4. Conceptos de diseño

- **Principios básicos.** Elección discreta de los trabajadores entre empleo formal de horario rígido e informal flexible; elección de estado de las empresas por beneficio relativo; entrada libre al estilo de Hopenhayn (1992) y Melitz (2003).
- **Emergencia.** Las tasas de informalidad, la brecha de género, los cierres y el umbral de la respuesta a las sanciones surgen de las decisiones individuales; no se imponen.
- **Adaptación.** Las empresas cambian de estado según ρ = (Π_F − Π_I)/Y.
- **Aprendizaje.** La "temperatura" T_k de la regla de Metropolis baja cada año, de modo que las empresas cometen menos errores con la experiencia. No hay otro aprendizaje.
- **Predicción.** Los agentes no predicen el futuro: deciden con los valores del mes.
- **Detección.** Las empresas conocen sus beneficios en ambos estados y la probabilidad de auditoría; los trabajadores conocen sus utilidades.
- **Interacción.** Es indirecta, a través de las vacantes formales (competencia por ranking de productividad) y de Ȳ, la producción mediana que escala el costo digital y la auditoría.
- **Estocasticidad.** Atributos iniciales, revisión mensual, regla de Metropolis, salida, entrantes y ruido del ranking.
- **Colectivos.** No hay.
- **Observación.** Ver 7.6.

## 5. Inicialización

1. Se generan trabajadores y empresas con las distribuciones de la Sección 2, usando el generador `numpy.random.default_rng(semilla)`.
2. Cada empresa empieza formal si Π_F > Π_I.
3. D_sys(0) = 0.30.
4. Los parámetros del país (s_F, φ₀, γ₀) se leen de `data/ilostat_s_F.csv` y `outputs/calibration_estimates.json`.

**Semillas:**
- calibración: 1000–1005;
- réplicas de política: 20260–20299, idénticas en todos los países y escenarios para que los contrastes sean pareados;
- barrido, ablación y sensibilidad: las primeras 6, 20 y 8 de esa lista.

## 6. Datos de entrada

No hay series externas que cambien durante la simulación. Los datos empíricos se usan solo para parametrizar y calibrar:
- tasas de informalidad por sexo: `data/ilostat_calibracion.csv`;
- participación femenina en el empleo: `data/ilostat_s_F.csv`;
- gradientes por educación y zona, usados solo para validación: `data/ilostat_gradientes.csv`.

Todos se descargan de la API SDMX de ILOSTAT con los scripts del repositorio.

## 7. Submodelos

### 7.1. Decisión del trabajador

- U_F = ln(ω_F h(1 − τ_w)(1 − γ₀H_care/48) − c_tr(1 + r)) + β + ε
- U_I = ln(ω_I h)

El trabajador está dispuesto a aceptar un empleo formal si el argumento del logaritmo es positivo y U_F > U_I. Valores: ω_F = 1.30, ω_I = 1.00, τ_w = 0.10, c_tr = 0.08 (doble en zona rural), β = 0.25.

### 7.2. Beneficios de la empresa

- Π_F = (1 − τ_c)Y − ω_F(1 + τ_w)L − rK − DCC, con τ_c = 0.20 sobre la producción y r = 0.08.
- Π_I = Y − ω_I L − r_I K − P_aud(μ₀Y + μ₁Y^ξ), con r_I = 0.16, μ₀ = 0.25, μ₁ = 0.02 y ξ = 1.35.
- DCC = Ȳ[φ₀ + φ₁(Ȳ/Y)^η(1 − K_dig)], con φ₁ = 0.30 y η = 0.42.
- P_aud = [1 + exp(−κ(D_sys Y/Ȳ − θ_th))]⁻¹, con κ = 4.12 y θ_th = 1.0.

Ȳ es la mediana de Y y se recalcula cada mes; en la variante "fija" se congela en el mes 96.

### 7.3. Regla de Metropolis

Una empresa informal se formaliza con probabilidad exp(min{ρ, 0}/T_k); una formal se informaliza con exp(min{−ρ, 0}/T_k). La temperatura es T_k = 0.5 · 0.85^k, con k = ⌊t/12⌋: baja de 0.50 a 0.16 durante el calentamiento.

### 7.4. Entrada y salida

No hay salida exógena: solo sale una empresa con beneficio negativo, con probabilidad mensual de 0.10.
- **Regla de referencia (entrada libre):** la entrante extrae A, K y dueño de las distribuciones iniciales y elige el estado de mayor beneficio. Si ambos beneficios son negativos, repite la extracción hasta 10 veces.
- **Regla alternativa:** toda entrante nace informal.

### 7.5. Escenarios (desde el mes 96)

- **A (statu quo):** D_sys crece 0.0015 por mes.
- **B1 (GovTech moderado):** κ × 2.5, crecimiento de D_sys × 3 y φ₁ × 1.5.
- **B2 (GovTech intensivo):** B1 más μ₀ y μ₁ × 3.
- **C (red de cuidados):** las horas de cuidado de las mujeres bajan 60 %.
- **D (integrado):** B2 + C, más un subsidio del 80 % al DCC de las empresas con L ≤ 10 y β × 1.5.

El barrido de sanciones repite B1 multiplicando μ₀ y μ₁ por un factor de 1 a 4 (3.0 equivale a la sanción de B2).

### 7.6. Métricas

Cada mes se registran:
- informalidad total, femenina y masculina (%);
- brecha (mujeres − hombres);
- tasa anualizada de salida de empresas: salidas del mes / N_F × 12 × 100;
- recaudación: τ_c · ΣY de las empresas formales + τ_w · ω_F · Σh de los trabajadores formales;
- índice de Gini del ingreso simulado;
- gradientes de informalidad por educación, por zona y por quintil de h.

El resultado de cada réplica es el promedio de los meses 109 a 120 de la política.

### 7.7. Calibración y validación

- **SMM por país:** se busca (φ₀, γ₀) en una rejilla 9 × 9 por bisección anidada, minimizando la distancia cuadrática a (F_obs, M_obs), con W = I. Cada momento promedia 6 simulaciones (semillas 1000–1005) en los 24 meses que siguen al calentamiento.
- **Validación LOCO:** se estima un γ₀ común con tres países y, con el φ₀ que reproduce la tasa masculina del país excluido, se predice su tasa femenina.

Las rutinas están en `itdt/calibrate.py` e `itdt/loco.py`.
