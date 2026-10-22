# Tabla 13: Validación de gradientes no calibrados frente a microdatos agregados de ILOSTAT (Escenario A)

| País      | Dimensión   | Categoría        |   Año Obs. |   Tasa Obs. ILOSTAT (%) |   Tasa Sim. ITDT (%) |   Error Abs. (pp) |
|:----------|:------------|:-----------------|-----------:|------------------------:|---------------------:|------------------:|
| Kenia     | Educación   | Básica (e = 0)   |       2019 |                   88.77 |                95.3  |              6.53 |
| Kenia     | Educación   | Media (e = 1)    |       2019 |                   80.84 |                85.03 |              4.19 |
| Kenia     | Educación   | Superior (e = 2) |       2019 |                   31.71 |                67.39 |             35.68 |
| Kenia     | Zona        | Rural            |       2019 |                   93.08 |                90.24 |              2.84 |
| Kenia     | Zona        | Urbana           |       2019 |                   73.82 |                82.21 |              8.39 |
| Nigeria   | Educación   | Básica (e = 0)   |       2022 |                   98.05 |                98.53 |              0.48 |
| Nigeria   | Educación   | Media (e = 1)    |       2022 |                   93.74 |                93.94 |              0.2  |
| Nigeria   | Educación   | Superior (e = 2) |       2022 |                   73.38 |                83.34 |              9.96 |
| Nigeria   | Zona        | Rural            |       2022 |                   97.94 |                96.07 |              1.87 |
| Nigeria   | Zona        | Urbana           |       2022 |                   90.35 |                91.95 |              1.6  |
| India     | Educación   | Básica (e = 0)   |       2012 |                   90.61 |                96.36 |              5.75 |
| India     | Educación   | Media (e = 1)    |       2012 |                   73.4  |                87.11 |             13.71 |
| India     | Educación   | Superior (e = 2) |       2012 |                   49.03 |                69.05 |             20.02 |
| India     | Zona        | Rural            |       2012 |                   92.74 |                91.45 |              1.29 |
| India     | Zona        | Urbana           |       2012 |                   72.51 |                84.28 |             11.77 |
| Bangladés | Educación   | Básica (e = 0)   |       2022 |                   85.87 |                91.86 |              5.99 |
| Bangladés | Educación   | Media (e = 1)    |       2022 |                   71.85 |                80.01 |              8.16 |
| Bangladés | Educación   | Superior (e = 2) |       2022 |                   53.45 |                65.52 |             12.07 |
| Bangladés | Zona        | Rural            |       2017 |                   96.6  |                86.91 |              9.69 |
| Bangladés | Zona        | Urbana           |       2017 |                   89.79 |                77.6  |             12.19 |

### Error Medio Absoluto (MAE) por país

| País | MAE Gradientes (pp) |
|:---|:---:|
| Kenia | 11.53 |
| Nigeria | 2.82 |
| India | 10.51 |
| Bangladés | 9.62 |
| **Promedio 4 países** | **8.62** |

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
