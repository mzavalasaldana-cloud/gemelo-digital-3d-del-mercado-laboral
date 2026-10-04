# Tabla 10: Costo computacional por réplica (216 meses: 96 de calentamiento + 120 de escenario)

| NW (trabajadores)          | NF (empresas)   | Tiempo por réplica (s), media (DE)   |   Memoria máxima del proceso (MB) |
|:---------------------------|:----------------|:-------------------------------------|----------------------------------:|
| 3 000                      | 300             | 0.149 (0.000)                        |                             218.4 |
| 6 000 (configuración base) | 600             | 0.232 (0.005)                        |                             218.4 |
| 12 000                     | 1 200           | 0.360 (0.006)                        |                             218.6 |
| 24 000                     | 2 400           | 0.655 (0.020)                        |                             219.3 |

*Nota.* 3 repeticiones por tamaño. El tiempo crece de forma aproximadamente lineal con NW. Memoria real del proceso medida con psutil/resource (RSS).
