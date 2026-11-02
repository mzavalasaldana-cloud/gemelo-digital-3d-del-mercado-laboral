# Tabla 5: Validación Fuera de Muestra Dejando un País Fuera (LOCO CV)

| País excluido   | F observada   | ITDT (gamma_0 común)   |   Brecha media |   Razón media |   Regresión lineal |   ITDT sin cuidado |
|:----------------|:--------------|:-----------------------|---------------:|--------------:|-------------------:|-------------------:|
| Kenia           | 90.19         | 93.67 (gamma_0=0.6)    |          92.85 |         93.01 |              91.39 |              82.91 |
| Nigeria         | 96.38         | 94.78 (gamma_0=0.5)    |          99.77 |        100    |              98.11 |              90.11 |
| India           | 91.56         | 94.62 (gamma_0=0.6)    |          97.01 |         97.67 |             106.69 |              86.3  |
| Bangladés       | 95.72         | 89.14 (gamma_0=0.5)    |          84.22 |         83.63 |              83.4  |              78.19 |
| MAE (p.p.)      | —             | 3.68                   |           5.75 |          6.16 |               7.59 |               9.08 |

---

### Explicabilidad Metodológica

> **Descripción y Fuentes:**
> Prueba de transferibilidad estructural Leave-One-Country-Out (LOCO) en 4 pliegues. En cada pliegue se excluye un país, se estima el parámetro común γ0 sobre los otros tres, y se pronostica la tasa de informalidad femenina del país excluido usando exclusivamente su tasa masculina observada e insumos empíricos independientes. Modelos de contraste: Heurística de Brecha Media, Razón Media empírica, Regresión Lineal OLS e ITDT sin restricción de cuidado.

> **Interpretación de Resultados:**
> 1. Superioridad predictiva de ITDT: Alcanza el menor error absoluto medio (MAE = 3.68 p.p.), superando con holgura a la Brecha Media (5.75 p.p.), Razón Media (6.16 p.p.), Regresión Lineal (7.59 p.p.) y al modelo sin cuidados (9.08 p.p.). 2. Validación del microfundamento de cuidados: Al desactivar el módulo de cuidado no remunerado, el error se dispara a 9.08 p.p., demostrando que el canal γ0 no es redundante sino esencial para predecir la brecha de género entre economías en desarrollo.
