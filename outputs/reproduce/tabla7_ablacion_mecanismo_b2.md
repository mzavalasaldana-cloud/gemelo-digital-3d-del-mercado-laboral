# Tabla 7: Descomposición y Ablación Causal del Efecto de B2 frente a A

| Variante del modelo        |   Δ mujeres (p.p.) |   Δ hombres (p.p.) |   Δ brecha (p.p.) |   Δ cierres (p.p./año) | Δ empresas formales: dueña / dueño (p.p.)   |
|:---------------------------|-------------------:|-------------------:|------------------:|-----------------------:|:--------------------------------------------|
| Completo                   |             -17.57 |             -47.25 |             29.69 |                  24.4  | +35.9 / +40.4                               |
| Sin restricción de cuidado |             -49.49 |             -49.35 |             -0.14 |                  18.51 | +36.4 / +36.7                               |
| Sin DCC regresivo          |             -17.67 |             -47.55 |             29.88 |                  24.24 | +36.4 / +40.7                               |
| Sin ambos                  |             -50.14 |             -49.94 |             -0.2  |                  18.5  | +37.1 / +36.4                               |

---

### Explicabilidad Metodológica

> **Descripción y Fuentes:**
> Experimento de ablación estructural con R = 20 réplicas pareadas por país. Cada variante del modelo fue recalibrada a los momentos oficiales de ILOSTAT antes de ejecutar los contrastes para aislar mecanismos puros: Variantes: Modelo Completo, Sin restricción de cuidado (H_care = 0), Sin componente digital regresivo (DCC plano), Sin ambos.

> **Interpretación de Resultados:**
> 1. Causa raíz de la brecha de género: Al remover la restricción de cuidados, la ampliación de la brecha de género inducida por B2 colapsa de +29.69 p.p. a −0.14 p.p., demostrando formalmente que el cuidado no remunerado es el único canal causante del ensanchamiento de la brecha. 2. Efecto del DCC regresivo: Eliminar el costo digital regresivo modera marginalmente los cierres de empresas (de 24.4% a 24.2%), pero mantiene inalterada la brecha (+29.88 p.p.), confirmando que el DCC afecta la rentabilidad de las MiPyMEs pero no la asimetría de género en el mercado laboral.
