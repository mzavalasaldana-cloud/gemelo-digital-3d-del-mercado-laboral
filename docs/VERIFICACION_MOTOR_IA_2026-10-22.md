# Reporte de Verificación Técnica del Motor de IA y Microdatos

**Fecha de evaluación:** 22 de octubre de 2026  
**Proyecto:** `C:\Users\PC ASUS\Desktop\gemelo-digital-3d-del-mercado-laboral`  
**Rama evaluada:** `motor-ia-microdatos-2026-10-22`  
**Rama de referencia:** `entrada-libre-2026-10-22`  
**Compromiso git evaluado:** `4773d9616cb0d0a11e1dc6484805e70a98c9e728`  
**Entorno de ejecución verificado:** Python 3.13.14 (`.venv`) en Windows 11

---

## 1. Veredicto

> **VEREDICTO: CON PROBLEMAS**  
> *El motor de IA no está conectado a los microdatos reales depositados en `data/microdatos_reales/`, no cuenta con un módulo de armonización de variables, no entrena modelos predictivos sobre las encuestas (generando excepciones inmediatas `KeyError: 'es_formal'`), carece de pruebas unitarias y la interfaz de usuario muestra pantallas bloqueadas o métricas simuladas (*mock*) cableadas en el código frontend con riesgo de fuga de información.*

---

## 2. Resumen de Estado por Pasos (1 al 7)

| Paso | Aspecto Evaluado | Estado | Resumen Técnico |
|---|---|:---:|---|
| **PASO 1** | Estado de la rama | **Completado (idéntica)** | La rama `motor-ia-microdatos-2026-10-22` apunta al mismo commit que `entrada-libre-2026-10-22` (`4773d96`). Árbol limpio. Los microdatos reales **NO** están versionados (`git ls-files` vacío) y están correctamente excluidos por `.gitignore:36`. |
| **PASO 2** | Datos de entrada reales | **Con problemas** | Los archivos de encuestas oficiales existen en disco con el conteo exacto de registros (`cperv1.csv`: 415 549 filas; `chhv1.csv`: 101 957 filas; `NLFS_..._INDIVIDUAL.sav`: 45 016 filas; `NLFS_..._HH.sav`: 8 796 filas). Sin embargo, el cargador del motor IA (`backend/ml_engine.py:49-79`) carga **0 filas**, debido a que no escanea subcarpetas ni reconoce archivos SPSS `.sav`. No hay `np.random` ni `make_classification` creando filas activas en backend. |
| **PASO 3** | Variable objetivo y calibración | **Comprobado analíticamente** | La definición OIT de informalidad se verificó con scripts sobre las encuestas crudas con factores de expansión: India PLFS 2024 arroja **87.96 %** total (ILOSTAT: 88.13 %, dif: -0.17 p.p.); Nigeria NLFS 2023 Q3 arroja **92.25 %** total (ILOSTAT 2024: 93.14 %, dif: -0.89 p.p.). Falta implementar la función de construcción de la variable en el cargador oficial del motor. |
| **PASO 4** | Entrenamiento de modelos | **Incompleto / Con problemas** | No se entrenan los modelos sobre microdatos reales. En `run_stratified_cv`: solo XGBoost, RF y HistGradientBoosting (faltan Regresión Logística, MLP y CatBoost). En `run_cross_validation_models`: espera variables de un antiguo dataset sintético (`es_formal`, `acceso_credito_pyme`, etc.) y falla al recibir encuestas reales. No hay partición por hogar (`GroupKFold`), ni uso de ponderadores de encuesta. Fuga de información en la interfaz (`CrossValidationTab.tsx:171`). |
| **PASO 5** | Ejecutar y medir | **No ejecutable / Incompleto** | No existe comando ni script ejecutable para entrenar sobre las encuestas. `models_store/` no contiene modelos entrenados. No hay métricas reales de prueba (AUC-ROC, F1, Accuracy, Brier score, ni desglose por sexo). Las únicas métricas visibles provienen de plantillas mock fijas en frontend. |
| **PASO 6** | Pruebas | **Parcial** | `pytest` reporta 22 pasadas, 11 omitidas (tests asíncronos sin pytest-asyncio activo), 0 falladas. **Cero pruebas del motor IA** en `tests/`. Las tablas del artículo en `outputs/` no sufrieron alteraciones (`git diff` vacío). |
| **PASO 7** | Integración con el sistema | **Con problemas** | En Streamlit, la pestaña "Motor IA" muestra la advertencia *"Sin microdatos reales cargados"* y bloquea la ejecución. En React (`AIEngineView.tsx`), si no se fuerza el estado, muestra pantalla bloqueada; si se activa, renderiza datos mock fijos. No existen capturas 4K del Motor IA en `outputs/capturas/`. |

---

## 3. Detalle de Verificación Paso a Paso

### PASO 1. Estado de la Rama

1. **Ramas locales y remotas (`git branch -a`):**
   ```text
     datos-reales-2026-10-21
     entrada-libre-2026-10-22
     itdt-articulo
     limpieza
     main
   * motor-ia-microdatos-2026-10-22
     replicacion-2026-10-21
     remotes/origin/itdt-articulo
     remotes/origin/limpieza
     remotes/origin/main
   ```
2. **Estado del árbol de trabajo (`git status`):**
   ```text
   On branch motor-ia-microdatos-2026-10-22
   nothing to commit, working tree clean
   ```
3. **Últimos 15 commits (`git log --oneline -15`):**
   ```text
   4773d96 fix(recalibracion-capturas): correccion metrica cierre firmas, verificacion recalibracion tabla 14 y 6 capturas 4k con prueba visual
   f8691bd feat(econometrics): especificacion de entrada libre, trazabilidad SDMX ILOSTAT 2026-10-22 y robustez Tabla 14
   4fa81e4 fix(visuals): desacoplar layout HUD 3D, ocultar palancas desconectadas, dinamizar fuentes ILOSTAT y actualizar capturas de alta resolucion
   cbb0829 fix: corregir trayectorias reales, eliminar interpolaciones y sincronizar gemelo 3D con ITDTModel (segunda revision)
   b24d421 fix(revisión): corregir C1-C8, conectar app a datos reales e ITDT calibrado y rehacer capturas 4K con backend activo
   a45e4b9 feat(datos-reales): conectar app exclusivamente a datos reales de ILOSTAT y modelo calibrado, agregar tabla 13 y capturas 4K
   49a1ae6 chore(replicacion): regenerar outputs desde cero con make all y agregar reporte REPLICACION_2026-10-21.md
   80957e8 fix(tests): diferir importacion de backend.database a fixture para tests sin dependencias de base de datos
   1db6c57 fix(deploy): agregar dominio asignado de Vercel a CORS_ORIGINS en render.yaml
   3335b16 feat(frontend): parametrizar URLs del backend y WebSocket con VITE_API_URL para despliegue en Vercel
   1bee5c9 fix(views): agregar netFiscalBalanceMillionUSD a metrics y proteger lecturas con .get() en vistas de Streamlit
   40a831b fix(deps): agregar reportlab, openpyxl y greenlet a requirements para Render y compatibilizar rangos de versiones
   84075b1 fix(copilot): migrar modelo por defecto a gemini-3.1-flash-lite y registrar error en HTTP 404
   e6eeaab feat(copilot): implementar Nivel 2 con Gemini directo vía REST, eliminar defaults de Langflow y agregar tests mock
   6c1dad8 feat(copilot): saltar llamada HTTP a Langflow de inmediato cuando no este configurado
   ```
4. **Diferencias respecto a `entrada-libre-2026-10-22` (`git diff --stat entrada-libre-2026-10-22`):**
   *Salida:* Vacía (0 archivos modificados, 0 inserciones, 0 eliminaciones).  
   *Hash comparativo:* Ambas ramas apuntan exactamente a `4773d9616cb0d0a11e1dc6484805e70a98c9e728`.
5. **Comprobación de exclusión en Git (`git ls-files | findstr microdatos_reales`):**
   *Salida:* Vacía (código de retorno 1 de findstr).  
   *Archivo `.gitignore` (línea 36):*
   ```gitignore
   data/microdatos_reales/
   ```

---

### PASO 2. Datos de Entrada Reales y Detección de Datos Sintéticos

1. **Archivos presentes físicamente en disco y conteo de filas:**
   - **India (PLFS 2024, MoSPI):**
     - Archivo de personas: `data/microdatos_reales/india/plfs_2024/cperv1.csv`  
       *Líneas en disco:* 415 550 (415 549 personas + encabezado). Coincide al 100 % con lo esperado.
     - Archivo de hogares: `data/microdatos_reales/india/plfs_2024/chhv1.csv`  
       *Líneas en disco:* 101 958 (101 957 hogares + encabezado). Coincide al 100 % con lo esperado.
   - **Nigeria (NLFS 2023 Q3, NBS):**
     - Archivo de personas: `data/microdatos_reales/nigeria/nlfs_2023q3/NLFS_2023Q3_INDIVIDUAL.sav`  
       *Registros leídos con `pyreadstat` (codificación latin1):* 45 016 personas, 182 columnas. Coincide al 100 % con lo esperado.
     - Archivo de hogares: `data/microdatos_reales/nigeria/nlfs_2023q3/NLFS_2023Q3_HOUSEHOLD_IDENTIFICATION.sav`  
       *Registros leídos con `pyreadstat`:* 8 796 hogares, 12 columnas. Coincide al 100 % con lo esperado.

2. **Filas que realmente carga el código del motor:**
   - Al ejecutar `scan_real_microdatasets()` en `backend/ml_engine.py`:
     ```python
     scan_real_microdatasets() -> []
     ```
     **Resultado:** Carga **0 filas**.  
     *Causa en el código (`backend/ml_engine.py:65-70`):*
     ```python
     for c_dir, (c_code, c_name) in country_dirs.items():
         dir_path = os.path.join(REAL_MICRODATA_DIR, c_dir)
         if os.path.exists(dir_path):
             for fname in os.listdir(dir_path):
                 if fname.lower().endswith((".csv", ".tsv", ".parquet")):
     ```
     La función busca directamente dentro de `data/microdatos_reales/<pais>/` sin explorar subdirectorios (`plfs_2024/`, `nlfs_2023q3/`) y no incluye la extensión SPSS `.sav`.
   - Consecuentemente, `load_real_country_microdata("india")` y `load_real_country_microdata("nigeria")` retornan `None`.

3. **Búsqueda exhaustiva de datos sintéticos o simulados en el código:**
   - `make_classification`: 0 coincidencias en todo el repositorio.
   - `np.random` para fabricar filas: 0 coincidencias en código activo. (En `backend/ml_engine.py:121-129` y `568-571`, las funciones sintéticas antiguas como `generate_country_preset_dataset` y `generate_synthetic_benchmark_dataset` están explícitamente desactivadas con `raise RuntimeError`).
   - `"dummy"`: Únicamente 9 apariciones en `src/components/DigitalTwin3D/DigitalTwinScene.tsx` (líneas 915, 1115-1119, 1203-1207), donde corresponde al objeto auxiliar `new THREE.Object3D()` para posicionamiento de mallas instanciadas en WebGL.
   - `"fake"`: 0 coincidencias en código fuente.
   - `"mock"`:
     - `src/components/Modals/UserManagementModal.tsx:386`: Etiqueta de botón de interfaz de usuarios predeterminados.
     - `src/services/api.ts:74`: Comentario sobre fallback offline.
     - `src/utils/i18n.ts:455`: Cadena de traducción que declara explícitamente la prohibición de datos mock.
     - `src/data/_archivado/aiEngineMockData.ts`: Archivo archivado con datos sintéticos obsoletos.
     - `tests/test_copilot_v1.py:7`: Uso estándar de `unittest.mock`.
   - `"demo"`:
     - `src/utils/i18n.ts:263, 612`: Cadenas de traducción de la opción de ingesta.
     - `src/data/_archivado/aiEngineMockData.ts:405`: Parámetro en archivo archivado.

---

### PASO 3. Variable Objetivo y Verificación contra ILOSTAT

#### A. Definición de Informalidad en Cada Encuesta

1. **India — PLFS 2024 (`cperv1.csv`):**
   - **Población objetivo:** Personas de 15+ años (`Age >= 15`) ocupadas en actividad principal (`Principal_Status_Code` en `{11, 12, 21, 31, 41, 51}`). Muestra ocupada: 163 973 personas.
   - **Condición de Informal:**
     - Ayudante familiar no remunerado en empresa del hogar: `Principal_Status_Code == 21`.
     - O bien, trabajador por cuenta propia o empleador (`Principal_Status_Code` en `{11, 12}`) en empresas propietarias, sociedades no constituidas o del hogar (`Principal_Enterprise_Type` en `{'01', '02', '03', '04', '12', '19'}` o enteros `{1, 2, 3, 4, 12, 19}`).
     - O bien, asalariado regular o jornalero ocasional (`Principal_Status_Code` en `{31, 41, 51}`) sin cobertura de beneficios de seguridad social (`Principal_Social_Security == 8`).
   - **Factor de ponderación (peso):**  
     `peso = Subsample_Multiplier / 100.0` si `Ns_Count_Sector_Stratum_Substratum_Subsample == Ns_Count_Sector_Stratum_Substratum`, caso contrario `Subsample_Multiplier / 200.0`.

2. **Nigeria — NLFS 2023 Q3 (`NLFS_2023Q3_INDIVIDUAL.sav`):**
   - **Población objetivo:** Personas de 15+ años (`dc5 >= 15`) con trabajo principal (`mjj4` no nulo). Muestra ocupada: 18 808 personas.
   - **Condición de Informal:**
     - Ayuda en negocio familiar o a miembro del hogar: `mjj4` en `{3.0, 5.0}`.
     - O bien, trabajo en negocio/granja propia (`mjj4 == 2.0`) y el negocio **no** está formalmente registrado (`mjj9c != 1.0`, es decir, no es "YES").
     - O bien, asalariado o aprendiz (`mjj4` en `{1.0, 4.0}`) y el empleador **no** aporta a pensión ni seguro de salud (`mjj8l_1 != 1.0` y `mjj8l_2 != 1.0`). Si no hubo respuesta o se desconoce la contribución (`mjj8l_1` y `mjj8l_2` en `{NaN, 97}`), se considera formal únicamente si cuenta simultáneamente con vacaciones anuales pagadas (`mjj8m == 1.0`) y licencia por enfermedad pagada (`mjj8n == 1.0`).
   - **Factor de ponderación (peso):**  
     Variable `weight_nlfs_q4` (peso crudo de hogar provisto por el NBS).

---

#### B. Comparación de Tasas Ponderadas Reconstruidas vs. ILOSTAT

Las tasas de referencia provienen de `data/ilostat_calibracion.csv` (descarga oficial de la API SDMX de ILOSTAT):

| País | Segmento | Tasa Ponderada Encuesta Reconstruida | Tasa Oficial ILOSTAT | Diferencia (p.p.) | Muestra Efectiva (filas) |
|---|---|:---:|:---:|:---:|:---:|
| **India (2024)** | **Total** | **87.96 %** | **88.13 %** | **-0.17 p.p.** | 163 973 |
| | Mujeres | 90.39 % | 91.56 % | -1.17 p.p. | 48 249 |
| | Hombres | 87.01 % | 86.58 % | +0.43 p.p. | 115 720 |
| **Nigeria (2023 Q3 / 2024)** | **Total** | **92.25 %** | **93.14 %** | **-0.89 p.p.** | 18 808 |
| | Mujeres | 95.97 % | 96.38 % | -0.41 p.p. | 9 250 |
| | Hombres | 88.61 % | 89.86 % | -1.25 p.p. | 9 558 |

*Observación metodológica:* Las diferencias son mínimas (< 1.3 p.p.) y se explican por el tratamiento de imputación de casos no declarados en el modelo de armonización de microdatos de ILOSTAT frente a la microencuesta trimestral cruda.

---

### PASO 4. Entrenamiento de Modelos y Auditoría de Fuga de Información

1. **Modelos implementados en el código:**
   - En `backend/ml_engine.py`:
     - Función `run_stratified_cv` (líneas 383-408): Admite `xgboost` (`XGBClassifier`), `random_forest` (`RandomForestClassifier`) y fallback a `HistGradientBoostingClassifier`.  
       *Faltan:* Regresión Logística (referencia), CatBoost y Redes Neuronales (MLP).
     - Función `run_cross_validation_models` (líneas 624-633): Instancia en diccionario `XGBClassifier`, `HistGradientBoostingClassifier`, `RandomForestClassifier`, `MLPClassifier` y `LogisticRegression`.  
       *Falta:* CatBoost.
   - **Incompatibilidad crítica:** La función `run_cross_validation_models` (línea 614) tiene codificada una lista fija de variables:
     `["edad", "anos_educacion", "anos_experiencia", "tamano_empresa", "capital_humano", "acceso_credito_pyme", "gasto_capacitacion_usd", "dias_tramite_registro"]`
     y la variable objetivo `"es_formal"`. Al pasarle la encuesta cruda PLFS (`cperv1.csv`), falla de inmediato con `KeyError: 'es_formal'`.

2. **Esquema de partición de datos:**
   - `backend/ml_engine.py:368`:
     ```python
     skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
     ```
     La partición es por filas aleatorias independientes a nivel persona. **NO** se agrupa por identificador de hogar (`Sample_Household_Number` / `FSU` en India, o `interview_key` en Nigeria).
     *Riesgo metodológico:* Personas del mismo hogar comparten características no observadas (entorno socioeconómico, choques del hogar), lo que introduce fuga por correlación intrahogar entre entrenamiento y prueba. Se requiere `GroupKFold` agrupado por hogar.
   - `backend/ml_engine.py:620-622`: En `run_cross_validation_models` la división es un corte secuencial simple 80/20 (`iloc[:split_idx]`), sin validación cruzada agrupada.

3. **Auditoría de fuga de información (variables predictoras vs. objetivo):**
   - En `data/microdatos_reales/india/plfs_2024/README.md` (líneas 43-45) y `data/microdatos_reales/nigeria/nlfs_2023q3/README.md` (líneas 42-45) se documenta claramente qué variables definen informalidad y **NO** deben usarse como predictoras:
     - India: `Principal_Enterprise_Type`, `Principal_Social_Security`, `Principal_Status_Code`, `Job_Contract_Type`, `Paid_Leave`.
     - Nigeria: `mjj4`, `mjj9c`, `mjj8l_1`, `mjj8l_2`, `mjj8m`, `mjj8n`, `mjj8c`, `mjj8k`, `mjj8a`.
   - **Problema encontrado en el Frontend:** En `src/components/Views/AIEngine/CrossValidationTab.tsx` (líneas 170-176), la tabla fija de importancia de características incluye:
     ```typescript
     { feature: 'Aporte a Seguridad Social', importance: 28.5 },
     ```
     Esta variable define directamente la variable objetivo en India.

4. **Uso de ponderadores muestrales (pesos de encuesta):**
   - En `backend/ml_engine.py:409` (`model.fit(X_train, y_train)`): **No** se suministra `sample_weight`.
   - En el cálculo de métricas (`accuracy_score`, `f1_score`, `roc_auc_score` en líneas 426-444 y 648-679): **No** se pondera por factor de expansión.

---

### PASO 5. Ejecución y Medición

1. **Estado de ejecución:**
   - No existe un script o comando CLI para ejecutar el entrenamiento del motor IA sobre las encuestas `cperv1.csv` o `NLFS_2023Q3_INDIVIDUAL.sav`.
   - La carpeta `models_store/` no contiene ningún archivo `.joblib` generado a partir de microdatos reales (únicamente la subcarpeta `_archivado/`).
   - Al invocar programáticamente las funciones de entrenamiento sobre las encuestas reales:
     - `load_real_country_microdata("india")` retorna `None`.
     - `run_cross_validation_models(df_plfs)` levanta `KeyError: 'es_formal'`.
     - `run_stratified_cv(df_plfs)` falla por falta de columna objetivo `ESTADO_LABORAL` y pretende codificar 139 columnas crudas sin armonizar.

2. **Tabla de Desempeño: Métricas Reales vs. Mock Fallback en Frontend:**

| País | Modelo | AUC-ROC | F1-Score | Accuracy | Brier Score | Desempeño Mujeres (F1 / AUC) | Desempeño Hombres (F1 / AUC) | Origen de la Cifra |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **India (PLFS 2024)** | Regresión Logística | *No entrenado* | *No entrenado* | *No entrenado* | *No entrenado* | *No calculado* | *No calculado* | Código no conectado a microdatos |
| | Random Forest | *No entrenado* | *No entrenado* | *No entrenado* | *No entrenado* | *No calculado* | *No calculado* | Código no conectado a microdatos |
| | XGBoost | *No entrenado* | *No entrenado* | *No entrenado* | *No entrenado* | *No calculado* | *No calculado* | Código no conectado a microdatos |
| | LightGBM | *No entrenado* | *No entrenado* | *No entrenado* | *No entrenado* | *No calculado* | *No calculado* | Código no conectado a microdatos |
| | CatBoost | *No existe* | *No existe* | *No existe* | *No existe* | *No existe* | *No existe* | Falta biblioteca y clase |
| | MLP Neural Net | *No entrenado* | *No entrenado* | *No entrenado* | *No entrenado* | *No calculado* | *No calculado* | Código no conectado a microdatos |
| **Nigeria (NLFS 2023)** | Todos los modelos | *No entrenado* | *No entrenado* | *No entrenado* | *No entrenado* | *No calculado* | *No calculado* | Cargador no soporta `.sav` ni subcarpetas |
| **Valores Mock (Fallback UI)** | XGBoost v3.4 | 0.948 | 0.912 | 0.926 | *No calculado* | *No calculado* | *No calculado* | `CrossValidationTab.tsx:134-143` (Mock) |
| | Random Forest | 0.932 | 0.895 | 0.908 | *No calculado* | *No calculado* | *No calculado* | `_archivado/aiEngineMockData.ts:182` (Mock) |
| | LightGBM | 0.941 | 0.908 | 0.919 | *No calculado* | *No calculado* | *No calculado* | `_archivado/aiEngineMockData.ts:181` (Mock) |
| | Regresión Logística | 0.884 | 0.841 | 0.862 | *No calculado* | *No calculado* | *No calculado* | `_archivado/aiEngineMockData.ts:184` (Mock) |

3. **Modelo Ganador Declarado:**
   - En el código frontend (`src/components/Views/AIEngine/CrossValidationTab.tsx:184-210`), aparece marcado como "Modelo Campeón en Producción" el `XGBoost v3.4 (SOTA)` con badge neón predeterminado.
   - **Veredicto sobre el modelo ganador:** No es un ganador científico ni empírico; es una asignación fija predeterminada en el código frontend, sin haber ejecutado entrenamiento competitivo sobre el conjunto de prueba de las encuestas reales.

4. **Tiempo de ejecución y reproducibilidad con semillas:**
   - No medible por ausencia de ejecución sobre datos reales.
   - Los parámetros de semilla en el código fuente están fijados a `random_state=42` (`backend/ml_engine.py:368, 504, 626`).

---

### PASO 6. Pruebas Unitarias y de Integración

1. **Resultado de `pytest`:**
   - Comando ejecutado: `.\.venv\Scripts\pytest.exe -v`
   - **Total de pruebas recolectadas:** 33 pruebas en `tests/`.
   - **Resultado:** **22 pasadas, 11 omitidas (skipped), 0 falladas** en 5.06 segundos.
   - Detalle de pruebas omitidas: 9 pruebas en `tests/test_copilot_v1.py` y 2 pruebas en `tests/test_postgres_langflow_integration.py` omitidas debido a que funciones asíncronas (`@pytest.mark.asyncio`) requieren el plugin activo en `pytest.ini`.
2. **Pruebas específicas del motor IA:**
   - **Ninguna.** No existe ningún archivo `test_ml_engine.py` ni pruebas en `tests/` que importen o verifiquen `backend.ml_engine`.
3. **Integridad de las tablas del artículo en `outputs/`:**
   - Comando ejecutado: `git diff entrada-libre-2026-10-22 -- outputs/`
   - **Resultado:** Vacío (código de salida 0). Las tablas macroeconómicas y resultados de calibración del artículo científico no han sido alterados en lo absoluto.

---

### PASO 7. Integración con el Sistema y Capturas

1. **Pestaña "Motor IA" en la Interfaz Streamlit:**
   - En `streamlit_app/views/ai_engine_view.py:68-89`:
     ```python
     df = load_real_country_microdata(country_code)
     if df is None or len(df) == 0:
         # Renderiza tarjeta informativa de bloqueo
         return
     ```
     Dado que `load_real_country_microdata` retorna `None`, la vista muestra una pantalla bloqueada con candado: *"Sin microdatos reales cargados"*, impidiendo cualquier visualización de datos falsos.
2. **Pestaña "Motor IA" en la Interfaz React / Vite:**
   - En `src/components/Views/AIEngineView.tsx:53-91`: Si `isDatasetLoaded` es falso, muestra una pantalla bloqueada semejante.
   - En `src/components/Views/AIEngine/CrossValidationTab.tsx:134-177`: Si se renderiza la pestaña de validación cruzada, los estados por defecto recurren a constantes fijas en caso de no recibir respuesta del backend (`summary`, `confusionMatrix`, `rocCurveData`, `featureImportance`).
   - En `src/components/Views/AIEngine/EDATab.tsx:84-92`: Si no hay respuesta de backend, recurre a `totalRows = 48500` (la cifra histórica del dataset sintético `SINTETICO_calibrado_PLFS_India.csv` documentado en `docs/INVENTARIO_DATOS_INVENTADOS.md`).
3. **Estado de las capturas en `outputs/capturas/`:**
   - El directorio `outputs/capturas/` contiene 6 capturas de alta resolución (4800 × 2700 px) correspondientes a:
     - `fig_dashboard_kenia_escenarioA.png`
     - `fig_dashboard_kenia_escenarioD.png`
     - `fig_gemelo3d_kenia_escenarioA.png`
     - `fig_gemelo3d_kenia_escenarioA_m60.png`
     - `fig_gemelo3d_kenia_escenarioB2.png`
     - `fig_gemelo3d_kenia_escenarioB2_m60.png`
   - **No existen capturas del Motor de IA**.

---

## 4. Problemas Encontrados (con Archivo y Línea)

| # | Archivo | Línea(s) | Severidad | Descripción del Problema |
|---|---|:---:|:---:|---|
| **1** | `backend/ml_engine.py` | 65–79 | **Crítica** | **Fallo de escaneo de microdatos reales:** `scan_real_microdatasets()` no realiza búsqueda recursiva en subcarpetas (`plfs_2024/`, `nlfs_2023q3/`) ni contempla la extensión `.sav`, provocando que retorne `[]` y el sistema quede en estado de "sin datos". |
| **2** | `backend/ml_engine.py` | 614–618 | **Crítica** | **Incompatibilidad de esquema / Excepción en runtime:** `run_cross_validation_models` busca características sintéticas en español (`"edad"`, `"anos_educacion"`, `"acceso_credito_pyme"`, `"es_formal"`) que no existen en las 140 variables en inglés de `cperv1.csv` ni en las 182 de `NLFS_..._INDIVIDUAL.sav`, provocando `KeyError: 'es_formal'`. |
| **3** | `backend/ml_engine.py` | 368 | **Alta** | **Fuga inter-hogar en partición:** `StratifiedKFold` particiona personas individuales al azar en lugar de agrupar por hogar (`GroupKFold` sobre `hhid` o `FSU`), permitiendo que miembros de la misma familia queden repartidos entre train y test. |
| **4** | `backend/ml_engine.py` | 409, 638 | **Media** | **Omisión de ponderadores de encuesta:** Los modelos y las métricas se ajustan y evalúan de forma no ponderada (`sample_weight=None`), ignorando los factores de expansión muestral. |
| **5** | `src/components/Views/AIEngine/CrossValidationTab.tsx` | 170–176 | **Alta** | **Fuga de información conceptual en UI:** Se lista "Aporte a Seguridad Social" como variable con 28.5 % de importancia en el clasificador, a pesar de ser la regla definitoria del objetivo informal en asalariados de PLFS. |
| **6** | `src/components/Views/AIEngine/CrossValidationTab.tsx` | 134–177 | **Media** | **Valores de prueba cableados (Mock Fallback):** Matriz de confusión fija (TP 48250, FP 4680, FN 3950, TN 48520) y métricas fijas (F1 91.2, AUC 94.8) que se muestran cuando el backend no responde. |
| **7** | `src/components/Views/AIEngine/EDATab.tsx` | 84–92 | **Media** | **Residuo de datos sintéticos en UI:** En ausencia de datos, el fallback define `totalRows: 48500`, que corresponde a la cantidad de filas de los antiguos archivos sintéticos archivados. |
| **8** | `backend/ml_engine.py` | 383–408 | **Media** | **Modelos incompletos en CV:** `run_stratified_cv` no incluye Regresión Logística (referencia basal), CatBoost ni Redes Neuronales (MLP). |
| **9** | `tests/` | Global | **Media** | **Ausencia total de pruebas del motor IA:** Hay 33 pruebas para econometría, copilot e ITDT, pero cero pruebas unitarias o de integración para `ml_engine.py`. |

---

## 5. Comandos Exactos para Reproducir Esta Auditoría

Todos los comandos se ejecutaron en PowerShell dentro de la raíz del proyecto `c:\Users\PC ASUS\Desktop\gemelo-digital-3d-del-mercado-laboral`:

### 1. Estado de Git y exclusión de microdatos
```powershell
git branch -a
git status
git log --oneline -15
git diff --stat entrada-libre-2026-10-22
git ls-files | findstr microdatos_reales
Select-String -Path .gitignore -Pattern "microdatos"
```

### 2. Conteo de filas de microdatos en disco
```powershell
# India (PLFS 2024 CSV)
.\.venv\Scripts\python.exe -c "
with open('data/microdatos_reales/india/plfs_2024/cperv1.csv', 'rb') as f:
    print('cperv1.csv personas:', sum(1 for _ in f) - 1)
with open('data/microdatos_reales/india/plfs_2024/chhv1.csv', 'rb') as f:
    print('chhv1.csv hogares:', sum(1 for _ in f) - 1)
"

# Nigeria (NLFS 2023 Q3 SAV con pyreadstat)
.\.venv\Scripts\python.exe -c "
import pyreadstat
_, mi = pyreadstat.read_sav('data/microdatos_reales/nigeria/nlfs_2023q3/NLFS_2023Q3_INDIVIDUAL.sav', metadataonly=True)
print('Nigeria personas:', mi.number_rows)
_, mh = pyreadstat.read_sav('data/microdatos_reales/nigeria/nlfs_2023q3/NLFS_2023Q3_HOUSEHOLD_IDENTIFICATION.sav', metadataonly=True)
print('Nigeria hogares:', mh.number_rows)
"
```

### 3. Verificación de lectura del motor actual
```powershell
.\.venv\Scripts\python.exe -c "
from backend.ml_engine import scan_real_microdatasets, load_real_country_microdata
print('scan_real_microdatasets():', scan_real_microdatasets())
print('load_real_country_microdata(india):', load_real_country_microdata('india'))
print('load_real_country_microdata(nigeria):', load_real_country_microdata('nigeria'))
"
```

### 4. Cálculo de informalidad ponderada en India PLFS 2024
```powershell
.\.venv\Scripts\python.exe -c "
import pandas as pd, numpy as np
cols = ['Sex', 'Age', 'Principal_Status_Code', 'Principal_Enterprise_Type', 'Principal_Social_Security',
        'Ns_Count_Sector_Stratum_Substratum_Subsample', 'Ns_Count_Sector_Stratum_Substratum', 'Subsample_Multiplier']
df = pd.read_csv('data/microdatos_reales/india/plfs_2024/cperv1.csv', usecols=cols)
same_ns = df['Ns_Count_Sector_Stratum_Substratum_Subsample'] == df['Ns_Count_Sector_Stratum_Substratum']
df['weight'] = np.where(same_ns, df['Subsample_Multiplier'] / 100.0, df['Subsample_Multiplier'] / 200.0)
df_emp = df[(df['Age'] >= 15) & (df['Principal_Status_Code'].isin([11, 12, 21, 31, 41, 51]))].copy()

is_helper = df_emp['Principal_Status_Code'] == 21
is_self = df_emp['Principal_Status_Code'].isin([11, 12])
is_inf_ent = df_emp['Principal_Enterprise_Type'].isin([1, 2, 3, 4, 12, 19, '01', '02', '03', '04', '12', '19'])
is_wage = df_emp['Principal_Status_Code'].isin([31, 41, 51])
no_soc = df_emp['Principal_Social_Security'].astype(str).str.strip().isin(['8', '8.0'])

df_emp['informal'] = (is_helper | (is_self & is_inf_ent) | (is_wage & no_soc)).astype(int)

w_tot = df_emp['weight'].sum()
w_inf = (df_emp['informal'] * df_emp['weight']).sum()
print(f'India PLFS Total: {w_inf / w_tot * 100:.2f}% (Muestra: {len(df_emp)})')
for s, n in [(1, 'Hombres'), (2, 'Mujeres')]:
    sub = df_emp[df_emp['Sex'] == s]
    print(f'India PLFS {n}: {(sub[\"informal\"] * sub[\"weight\"]).sum() / sub[\"weight\"].sum() * 100:.2f}%')
"
```

### 5. Cálculo de informalidad ponderada en Nigeria NLFS 2023 Q3
```powershell
.\.venv\Scripts\python.exe -c "
import pyreadstat, pandas as pd, numpy as np
df, _ = pyreadstat.read_sav('data/microdatos_reales/nigeria/nlfs_2023q3/NLFS_2023Q3_INDIVIDUAL.sav', encoding='latin1')
df15 = df[(df['dc5'] >= 15) & (df['mjj4'].notnull())].copy()

is_helper = df15['mjj4'].isin([3.0, 5.0])
is_own_inf = (df15['mjj4'] == 2.0) & (df15['mjj9c'] != 1.0)
is_emp = df15['mjj4'].isin([1.0, 4.0])

has_contrib = (df15['mjj8l_1'] == 1.0) | (df15['mjj8l_2'] == 1.0)
no_resp = (df15['mjj8l_1'].isna() | (df15['mjj8l_1'] == 97.0)) & (df15['mjj8l_2'].isna() | (df15['mjj8l_2'] == 97.0))
has_leave = (df15['mjj8m'] == 1.0) & (df15['mjj8n'] == 1.0)

is_formal_emp = is_emp & (has_contrib | (no_resp & has_leave))
df15['informal'] = (is_helper | is_own_inf | (is_emp & ~is_formal_emp)).astype(int)

w = df15['weight_nlfs_q4'].fillna(0)
print(f'Nigeria Total: {(df15[\"informal\"] * w).sum() / w.sum() * 100:.2f}% (Muestra: {len(df15)})')
for s, n in [(1.0, 'Hombres'), (2.0, 'Mujeres')]:
    sub = df15[df15['dc3'] == s]
    ws = sub['weight_nlfs_q4'].fillna(0)
    print(f'Nigeria {n}: {(sub[\"informal\"] * ws).sum() / ws.sum() * 100:.2f}%')
"
```

### 6. Ejecución de pruebas unitarias y verificación de outputs
```powershell
.\.venv\Scripts\pytest.exe -v
git diff entrada-libre-2026-10-22 -- outputs/
```
