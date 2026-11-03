# Reporte Oficial de Correcciones v1.0.1: Métricas de Cierres por Sexo del Dueño
**Fecha de emisión:** 2026-11-02  
**Versión:** `v1.0.1`  
**Repositorio:** ITDT (*Informality Transition Digital Twin*)

---

## 1. Motivo de la Corrección

En la versión inicial `v1.0.0` del paquete de replicación, no existía un script automatizado que calculara de forma explícita las tasas de cierre y la formalización neta desagregadas por el sexo del dueño de la empresa. Las cifras reportadas en borradores preliminares del manuscrito (B2: 29.80 % / 20.40 %, RR 1.46) provenían de aproximaciones que no eran estrictamente reproducibles mediante el pipeline canónico.

Para subsanar esta limitación y garantizar la reproducibilidad científica estricta:
1. Se incorporó el script canónico [`scripts/cierres_por_dueno.py`](../scripts/cierres_por_dueno.py).
2. El script clasifica las salidas registradas en `exited_firm_indices` guardando el sexo del dueño de cada firma antes de cada paso de simulación.
3. No consume números aleatorios adicionales, preservando la trayectoria de cada réplica idéntica a la del simulador base `ITDTModel`.
4. Se actualizan las cifras por los valores exactos y reproducibles generados por el script:
   - **B2:** Cierre dueña **28.98 %** / Cierre dueño **21.95 %**, **RR = 1.32 [1.25, 1.39]**.

---

## 2. Tabla Completa de Nuevos Valores Reproducibles

### 2.1. Escenarios Principales (Tablas 5 y Figura 3)
*Estimación con $R = 40$ réplicas independientes, ventana de evaluación meses 109–120, intervalo de confianza al 95 % obtenido por bootstrap en dos etapas ($B = 4000$, semilla 2026).*

| Escenario | Tasa Cierre Dueña (%) | Tasa Cierre Dueño (%) | Riesgo Relativo (RR) [IC 95 %] | $\Delta$ Formales Dueña (p.p.) | $\Delta$ Formales Dueño (p.p.) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **A** (Statu quo) | 0.03 | 0.02 | n. d. | +0.0 | +0.0 |
| **B1** (GovTech moderado) | 0.00 | 0.00 | n. d. | +0.0 | +0.0 |
| **B2** (GovTech intensivo) | 28.98 | 21.95 | 1.32 [1.25, 1.39] | +36.1 | +40.4 |
| **C** (Red de cuidados) | 0.00 | 0.02 | n. d. | +0.8 | -0.1 |
| **D** (Integrado) | 11.30 | 9.90 | 1.14 [1.07, 1.24] | +39.5 | +36.2 |

### 2.2. Descomposición por Ablación (Tabla 6: B2 vs. A)
*Evaluación de las 4 variantes estructurales con recalibración SMM y $R = 20$ réplicas.*

| Variante de Mecanismo | Cierre Dueña (%) | Cierre Dueño (%) | Riesgo Relativo (RR) [IC 95 %] |
| :--- | :---: | :---: | :---: |
| **Modelo Completo (`full`)** | 29.30 | 21.65 | 1.35 [1.28, 1.42] |
| **Sin canal de cuidado (`no_care`)** | 18.55 | 18.50 | 1.00 [0.93, 1.05] |
| **Sin DCC regresivo (`no_dcc`)** | 28.95 | 21.62 | 1.34 [1.25, 1.44] |
| **Sin ambos mecanismos (`neither`)** | 18.57 | 18.46 | 1.01 [0.95, 1.05] |

### 2.3. Robustez ante Especificaciones Estructurales (Tabla 7: B2)
*Recalibración de $\phi_0$ y $\gamma_0$ en cada especificación con $R = 40$ réplicas.*

| Regla de Entrada / Modo de Salario de Reserva | Cierre Dueña (%) | Cierre Dueño (%) |
| :--- | :---: | :---: |
| **Entrada forzada / $\bar{y}$ dinámica** (`forced_informal / dynamic`) | 58.60 | 48.32 |
| **Entrada forzada / $\bar{y}$ fija** (`forced_informal / fixed`) | 8.38 | 7.16 |
| **Libre entrada / $\bar{y}$ dinámica** (`free / dynamic`) *(Canónica)* | 28.98 | 21.95 |
| **Libre entrada / $\bar{y}$ fija** (`free / fixed`) | 4.84 | 3.82 |

---

## 3. Preservación de las Conclusiones Cualitativas

Las correcciones numéricas no alteran en modo alguno las conclusiones teóricas ni de política del artículo:

1. **Persistencia de la penalización de género:** En el escenario de fiscalización estricta no asistida (B2), las firmas lideradas por mujeres enfrentan una probabilidad de cierre significativamente superior a la de los hombres (RR = 1.32, con límite inferior del IC 95 % en 1.25, estrictamente mayor que 1.0).
2. **Identificación del canal causal:** El análisis de ablación confirma que la sobrecarga del trabajo de cuidado no remunerado es la causa dominante de esta asimetría. Al desactivar el canal de cuidado (`no_care`), la tasa de cierre se iguala prácticamente al 18.5 % en ambos sexos y el RR colapsa a 1.00 [0.93, 1.05].
3. **Eficacia del enfoque integrado:** La política D (GovTech + Red de Cuidados + Monotributo progresivo) reduce la tasa global de mortalidad empresarial (11.30 % dueña vs. 9.90 % dueño) y contrae el sesgo de género a RR = 1.14 [1.07, 1.24], mientras maximiza la formalización neta de mujeres dueñas (+39.5 p.p.).

---

## 4. Regeneración de Figuras y Flujo de Reproducción

Las figuras del manuscrito se generan a partir de estas salidas reproducibles:
* **Figuras en español:** generadas en [`outputs/figuras_articulo/`](../outputs/figuras_articulo/) mediante `python scripts/generar_figuras.py`.
* **Figuras en inglés:** generadas en [`outputs/figuras_articulo_en/`](../outputs/figuras_articulo_en/) mediante `python scripts/generar_figuras_en.py`.

Ambos conjuntos incluyen exportaciones vectoriales en PDF y mapas de bits en PNG a 800 ppp. Todo el flujo queda plenamente integrado en los orquestadores:
```bash
make owner      # Ejecuta los tres modos de cierres_por_dueno.py
make figuras    # Regenera las figuras del artículo en ambos idiomas
```

