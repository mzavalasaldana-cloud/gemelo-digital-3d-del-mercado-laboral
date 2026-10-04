# Tabla 10: Costo computacional por réplica (216 meses: 96 de calentamiento + 120 de escenario)

| NW (trabajadores)          | NF (empresas)   | Tiempo por réplica (s), media (DE)   |   Memoria máxima del proceso (MB) |
|:---------------------------|:----------------|:-------------------------------------|----------------------------------:|
| 3 000                      | 300             | 0.222 (0.077)                        |                             202.9 |
| 6 000 (configuración base) | 600             | 0.274 (0.040)                        |                             203.9 |
| 12 000                     | 1 200           | 0.456 (0.027)                        |                             205.8 |
| 24 000                     | 2 400           | 0.682 (0.087)                        |                             208.6 |

*Nota.* 3 repeticiones por tamaño. El tiempo crece de forma aproximadamente lineal con NW. Memoria real del proceso medida con psutil/resource (RSS).
