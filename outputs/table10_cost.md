# Tabla 10: Costo computacional por réplica (216 meses: 96 de calentamiento + 120 de escenario)

| NW (trabajadores)          | NF (empresas)   | Tiempo por réplica (s), media (DE)   |   Memoria máxima del proceso (MB) |
|:---------------------------|:----------------|:-------------------------------------|----------------------------------:|
| 3 000                      | 300             | 0.159 (0.002)                        |                             195.3 |
| 6 000 (configuración base) | 600             | 0.232 (0.011)                        |                             194.3 |
| 12 000                     | 1 200           | 0.365 (0.007)                        |                             195.7 |
| 24 000                     | 2 400           | 0.646 (0.004)                        |                             197.7 |

*Nota.* 3 repeticiones por tamaño. El tiempo crece de forma aproximadamente lineal con NW. Memoria real del proceso medida con psutil/resource (RSS).
