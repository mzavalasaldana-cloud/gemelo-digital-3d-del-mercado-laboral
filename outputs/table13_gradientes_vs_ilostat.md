# Tabla 13: Validación de gradientes no calibrados frente a microdatos agregados de ILOSTAT (Escenario A)

| País      | Dimensión   | Categoría        |   Año Obs. |   Tasa Obs. ILOSTAT (%) |   Tasa Sim. ITDT (%) |   Error Abs. (pp) |
|:----------|:------------|:-----------------|-----------:|------------------------:|---------------------:|------------------:|
| Kenia     | Educación   | Básica (e = 0)   |       2019 |                   88.77 |                94.77 |              6    |
| Kenia     | Educación   | Media (e = 1)    |       2019 |                   80.84 |                83.87 |              3.03 |
| Kenia     | Educación   | Superior (e = 2) |       2019 |                   31.71 |                66.05 |             34.34 |
| Kenia     | Zona        | Rural            |       2019 |                   93.08 |                89.48 |              3.6  |
| Kenia     | Zona        | Urbana           |       2019 |                   73.82 |                81.09 |              7.27 |
| Nigeria   | Educación   | Básica (e = 0)   |       2022 |                   98.05 |                98.75 |              0.7  |
| Nigeria   | Educación   | Media (e = 1)    |       2022 |                   93.74 |                94.58 |              0.84 |
| Nigeria   | Educación   | Superior (e = 2) |       2022 |                   73.38 |                84.52 |             11.14 |
| Nigeria   | Zona        | Rural            |       2022 |                   97.94 |                96.47 |              1.47 |
| Nigeria   | Zona        | Urbana           |       2022 |                   90.35 |                92.68 |              2.33 |
| India     | Educación   | Básica (e = 0)   |       2012 |                   90.61 |                96.93 |              6.32 |
| India     | Educación   | Media (e = 1)    |       2012 |                   73.4  |                88.59 |             15.19 |
| India     | Educación   | Superior (e = 2) |       2012 |                   49.03 |                71.55 |             22.52 |
| India     | Zona        | Rural            |       2012 |                   92.74 |                92.47 |              0.27 |
| India     | Zona        | Urbana           |       2012 |                   72.51 |                85.82 |             13.31 |
| Bangladés | Educación   | Básica (e = 0)   |       2022 |                   85.87 |                92.6  |              6.73 |
| Bangladés | Educación   | Media (e = 1)    |       2022 |                   71.85 |                80.98 |              9.14 |
| Bangladés | Educación   | Superior (e = 2) |       2022 |                   53.45 |                66.4  |             12.95 |
| Bangladés | Zona        | Rural            |       2017 |                   96.6  |                87.63 |              8.97 |
| Bangladés | Zona        | Urbana           |       2017 |                   89.79 |                78.65 |             11.14 |

### Error Medio Absoluto (MAE) por país

| País | MAE Gradientes (pp) |
|:---|:---:|
| Kenia | 10.85 |
| Nigeria | 3.30 |
| India | 11.52 |
| Bangladés | 9.78 |
| **Promedio 4 países** | **8.86** |

---
### Notas metodológicas y emparejamiento de categorías

1. **Emparejamiento de educación:**
   - **Básica ($e = 0$):** Emparejada con `EDU_AGGREGATE_BAS` de ILOSTAT (*Basic education*: primaria completa o secundaria baja / ISCED 1-2).
   - **Media ($e = 1$):** Emparejada con `EDU_AGGREGATE_INT` de ILOSTAT (*Intermediate education*: secundaria alta o post-secundaria no terciaria / ISCED 3-4).
   - **Superior ($e = 2$):** Emparejada con `EDU_AGGREGATE_ADV` de ILOSTAT (*Advanced education*: educación terciaria y universitaria / ISCED 5-8).

2. **Emparejamiento geográfico:**
   - **Rural:** Emparejada con `GEO_COV_RUR` de ILOSTAT (*Rural area coverage*).
   - **Urbana:** Emparejada con `GEO_COV_URB` de ILOSTAT (*Urban area coverage*).

3. **Años observados y disponibilidad empírica:**
   - **Kenia (KEN):** 2019 (coincide exactamente con el año de calibración).
   - **Nigeria (NGA):** 2022 (año empírico más cercano disponible con desagregación completa en ILOSTAT; 2024 sólo posee series nacionales modeladas).
   - **India (IND):** 2012 (año más reciente con microdatos armonizados completos de ambas dimensiones en la serie anual de ILOSTAT).
   - **Bangladés (BGD):** 2022 para educación (`EMP_NIFL_SEX_EDU_RT`) y 2017 para zona geográfica (`EMP_NIFL_SEX_GEO_RT`), correspondientes a las rondas oficiales de la Labour Force Survey disponibles.

4. **Principio de no imputación:** Ningún dato ausente ha sido estimado ni rellenado; todas las cifras observadas provienen directamente del repositorio oficial de ILOSTAT.
