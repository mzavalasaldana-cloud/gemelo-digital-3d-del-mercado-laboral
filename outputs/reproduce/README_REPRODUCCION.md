# Paquete Oficial de Reproducción del Artículo Científico ITDT

Este directorio contiene las figuras y tablas generadas automáticamente por el Gemelo Digital ITDT,
calibrado por SMM con microdatos de ILOSTAT para Kenia, Nigeria, India y Bangladés.

## Archivos Generados:
- `figura5_intensidad_sanciones.png` / `.pdf`: Barrido de multiplicador de sanciones de 1.0 a 4.0 bajo B1 con bandas de ±1 DE y cierres anuales.
- `figura6_informalidad_sexo.png` / `.pdf`: Informalidad por escenario y sexo en meses 109–120 con barras de error ±1 DE y etiquetas de brecha F − M.
- `Resultados_Articulo_ITDT.xlsx`: Libro Excel maestro multi-pestaña con formato institucional y bloques de interpretabilidad.
- `tabla4_calibracion_smm.xlsx` / `.md`: Momentos observados, simulados y estimaciones φ0 y γ0 (10 recalibraciones).
- `tabla5_validacion_loco.xlsx` / `.md`: Validación Leave-One-Country-Out (MAE = 3.68 p.p.) frente a baselines.
- `tabla6_niveles_y_cambios_bootstrap.xlsx` / `.md`: Niveles y contrastes pareados frente a A con IC 95% Bootstrap B = 4000.
- `tabla7_ablacion_mecanismo_b2.xlsx` / `.md`: Descomposición causal de B2 con variantes recalibradas (R = 20).
- `tabla8_robustez_reglas_entrada.xlsx` / `.md`: Robustez a reglas de entrada (forzada vs libre) y normalización Ȳ.
- `Paquete_Replicacion_ITDT.zip`: Archivo comprimido con todos los artefactos.

## Comando para regenerar todo desde la consola:
```bash
python scripts/reproduce_paper.py
```
O mediante el Makefile:
```bash
make reproduce
```
