# Documentación de Insumos para la Validación Fuera de Muestra (LOCO)

**Fecha de generación:** Octubre 2026  
**Referencia:** Sección 3.6 del artículo *ITDT: Un gemelo digital para la evaluación ex ante de políticas de formalización laboral*.

---

## 1. Principio Fundamental de Blindaje de Insumos

En la validación cruzada dejando un país fuera (*Leave-One-Country-Out*, LOCO), el objetivo científico es predecir la tasa de informalidad femenina ($F_c$) de un país excluido $c$ a partir de la información macroeconómica de los otros tres países de entrenamiento ($\mathcal{C}_{-c}$).

> [!IMPORTANT]
> **Aislamiento Estricto del País Excluido:**
> Ningún modelo tiene acceso, directa ni indirectamente, a:
> 1. La tasa de informalidad femenina observada del país excluido ($F_{obs,c}$).
> 2. La tasa de informalidad total observada del país excluido ($T_{obs,c}$), dado que $T = s_F F + (1 - s_F) M$ permitiría derivar $F$ algebraicamente.

---

## 2. Matriz de Insumos Utilizados por Cada Modelo en LOCO

| Modelo | Insumos del País Excluido ($c$) | Insumos de los Países de Entrenamiento ($\mathcal{C}_{-c}$) | Parámetros Estimados / Transferidos | ¿Usa $F_c$ o $T_c$? |
| :--- | :--- | :--- | :--- | :---: |
| **ITDT ($\gamma_0$ común)** | • Tasa masculina observada $M_{obs,c}$<br>• Proporción de empleo femenino $s_{F,c}$ (de `data/ilostat_s_F.csv`) | • Tasas completas: $M_{obs,k}$, $F_{obs,k}$, $s_{F,k}$ ($k \in \mathcal{C}_{-c}$) | • $\gamma_0^*$: estimado por búsqueda en rejilla $[0.0, 1.2]$ sobre $\mathcal{C}_{-c}$.<br>• $\phi_{0,c}$: calibrado en $c$ para igualar **únicamente** $M_{obs,c}$ dado $\gamma_0^*$. | ❌ **NO** |
| **Brecha Media** | • Tasa masculina observada $M_{obs,c}$ | • Brechas observadas: $(F_{obs,k} - M_{obs,k})$ para $k \in \mathcal{C}_{-c}$ | • Brecha promedio transferida: $\bar{\Delta}_{-c} = \frac{1}{3}\sum (F_k - M_k)$<br>• Predicción: $\hat{F}_c = M_c + \bar{\Delta}_{-c}$. | ❌ **NO** |
| **Razón Media** | • Tasa masculina observada $M_{obs,c}$ | • Razones observadas: $(F_{obs,k} / M_{obs,k})$ para $k \in \mathcal{C}_{-c}$ | • Razón promedio transferida: $\bar{R}_{-c} = \frac{1}{3}\sum (F_k / M_k)$<br>• Predicción: $\hat{F}_c = \min(100, M_c \cdot \bar{R}_{-c})$. | ❌ **NO** |
| **Regresión Lineal sobre $s_F$** | • Tasa masculina observada $M_{obs,c}$<br>• Proporción de empleo femenino $s_{F,c}$ | • Brechas observadas $(F_k - M_k)$ y $s_{F,k}$ para $k \in \mathcal{C}_{-c}$ | • Coeficientes OLS: $\Delta_k = \beta_0 + \beta_1 s_{F,k}$ entrenados con los 3 países.<br>• Predicción: $\hat{F}_c = M_c + (\hat{\beta}_0 + \hat{\beta}_1 s_{F,c})$. | ❌ **NO** |
| **ITDT sin cuidado (E3)** | • Tasa masculina observada $M_{obs,c}$<br>• Proporción de empleo femenino $s_{F,c}$ | • Ninguno requerido (modelo sin término de cuidado, $\gamma_0 = 0$) | • $\phi_{0,c}$: calibrado en $c$ para igualar $M_{obs,c}$ fijando $\gamma_0 = 0$.<br>• Predicción: $\hat{F}_c = F_{sim}(\phi_{0,c}, \gamma_0=0)$. | ❌ **NO** |

---

## 3. Justificación y Observaciones Metodológicas

1. **Independencia de $s_F$:**  
   La proporción de mujeres en el empleo ($s_F$) se carga directamente del indicador oficial de empleo por sexo publicado por ILOSTAT (almacenado en `data/ilostat_s_F.csv` con metadatos de consulta). No se deduce algebraicamente de la relación contable de tasas de informalidad, garantizando que no filtre información de $F_c$.
2. **Identificación de $\phi_0$ en el Excluido:**  
   Dado que el empleo masculino no sufre penalización por cuidado ($\gamma_0 \cdot H_{care} / 48 \approx 0$), la tasa masculina $M_{obs,c}$ permite calibrar el costo fijo de cumplimiento $\phi_0$ del país excluido de forma limpia y ortogonal a la brecha de género.
3. **Poder predictivo de ITDT:**  
   El modelo ITDT es el único modelo estructural capaz de predecir la brecha de género fuera de muestra transfiriendo un único parámetro conductual común ($\gamma_0$) entre economías del Sur Global.
