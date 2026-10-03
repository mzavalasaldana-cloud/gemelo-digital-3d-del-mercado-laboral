# Tabla 10: Costo computacional por réplica (216 meses: 96 de calentamiento + 120 de escenario)

| NW (trabajadores)          | NF (empresas)   | Tiempo por réplica (s), media (DE)   |   Memoria máxima del proceso (MB) |
|:---------------------------|:----------------|:-------------------------------------|----------------------------------:|
| 3 000                      | 300             | 0.227 (0.100)                        |                             171.3 |
| 6 000 (configuración base) | 600             | 0.237 (0.055)                        |                             171.3 |
| 12 000                     | 1 200           | 0.400 (0.064)                        |                             173.1 |
| 24 000                     | 2 400           | 0.698 (0.059)                        |                             175   |

*Nota.* 3 repeticiones por tamaño. El tiempo crece de forma aproximadamente lineal con NW. Memoria real del proceso medida con psutil/resource (RSS).
