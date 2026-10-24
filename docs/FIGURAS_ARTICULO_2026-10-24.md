# Regeneración de Figuras del Artículo para Publicación Impresa (CRORR)
**Fecha:** 24 de octubre de 2026  
**Proyecto:** Gemelo Digital 3D del Mercado Laboral (ITDT)  
**Rama:** `figuras-articulo-2026-10-24`  
**Destino editorial:** *Croatian Operational Research Review* (CRORR)  

---

## 1. Resumen Ejecutivo y Diagnóstico

### El Problema Editorial
Al insertar figuras en una columna estándar de publicación de **145 mm** (o **120 mm** para diagramas de arquitectura), las figuras generadas a resolución de pantalla convencional sufren una reducción geométrica que encoge la tipografía a tamaños ilegibles de 2 a 4 puntos tipográficos ($2\text{--}4\text{ pt}$). Como establece la directriz editorial, tener alta cantidad de píxeles no basta si la letra en la página impresa queda por debajo del umbral mínimo de lectura del ojo humano.

### Criterios y Restricciones Obligatorias Aplicadas
1. **Conservación Numérica Estricta:** No se modificó ningún parámetro econométrico ni se volvió a correr el modelo (`make all` no ejecutado). Todos los gráficos se trazaron a partir de los datos consolidados en `outputs/` (`sanctions_sweep_data.csv`, `table5_levels.csv`, `trayectorias_mensuales.json`).
2. **Dimensiones Físicas y Resolución:**
   - Ancho final: exactamente **145 mm** (3425 px a 600 dpi) para Figuras 3, 4, 5 y 6.
   - Ancho final: exactamente **120 mm** (2835 px a 600 dpi) para Figura 2.
   - Exportación dual: **PNG a 600 dpi** y **PDF vectorial** para cada figura.
3. **Tipografía Legible en Impresión:**
   - Tamaño mínimo absoluto de letra en papel: **$\ge 8.0\text{ pt}$** ($66.7\text{ px}$ a 600 dpi) para leyendas, anotaciones y etiquetas de ejes.
   - Títulos de ejes y cartelas de estado: **$\ge 9.0\text{ pt}$** ($75.0\text{ px}$ a 600 dpi).
   - Tipografía sans institucional consistente: **DejaVu Sans / Arial**.
4. **Normas de Publicación y Estilo:**
   - Sin títulos dentro del lienzo del gráfico (los títulos pertenecen al pie de figura del artículo).
   - Idioma 100% en español.
   - Terminología estricta: *"statu quo"* (sin 's' final) y *"Brecha (M − H)"* ($mujeres - hombres$).
   - Diferenciación en escala de grises / blanco y negro mediante marcadores contrastantes, estilos de trazo (líneas continuas, discontinuas, punteadas) y tramas achuradas (*hatching*).

---

## 2. Inventario de Figuras Generadas

Todos los archivos generados residen en `outputs/figuras_articulo/` sin haber alterado ni eliminado las figuras previas.

| Figura | Archivo PNG (600 dpi) | Archivo PDF Vectorial | Ancho (mm) | Alto (mm) | Dimensiones (px) | Letra mín. (pt) | Letra título/eje |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Fig. 2** | `fig2_arquitectura.png` | `fig2_arquitectura.pdf` | 120.0 mm | 92.0 mm | $2834 \times 2173$ | 9.0 pt | 10.0 pt negrita |
| **Fig. 3** | `fig3_panel_kenia_D.png` | `fig3_panel_kenia_D.pdf` | 145.0 mm | 148.2 mm | $3425 \times 3501$ | 8.0 pt | 9.0 pt |
| *Fig. 3a* | `fig3a_tarjetas_indicadores.png` | — | 143.9 mm | 48.4 mm | $3400 \times 1144$ | 8.6 pt | 15.5 pt |
| *Fig. 3b* | `fig3b_grafico_trayectorias.png` | — | 143.9 mm | 89.1 mm | $3400 \times 2104$ | 8.6 pt | 9.1 pt |
| **Fig. 4** | `fig4_gemelo3d_kenia.png` | `fig4_gemelo3d_kenia.pdf` | 145.0 mm | 53.6 mm | $3425 \times 1267$ | 8.16 pt | 9.0 pt |
| *Fig. 4a* | `fig4a_gemelo3d_kenia_A.png` | — | 71.5 mm | 53.6 mm | $1690 \times 1267$ | 8.16 pt | 9.0 pt |
| *Fig. 4b* | `fig4b_gemelo3d_kenia_B2.png` | — | 71.5 mm | 53.6 mm | $1690 \times 1267$ | 8.16 pt | 9.0 pt |
| **Fig. 5** | `fig5_barrido_sanciones.png` | `fig5_barrido_sanciones.pdf` | 145.0 mm | 80.0 mm | $3425 \times 1889$ | 8.5 pt | 9.5 pt |
| **Fig. 6** | `fig6_niveles_escenarios.png` | `fig6_niveles_escenarios.pdf` | 145.0 mm | 75.0 mm | $3425 \times 1771$ | 8.5 pt | 9.5 pt |

---

## 3. Especificación Técnica por Figura

### Fig. 2. Arquitectura de ITDT (Diagrama Estructural)
- **Archivos:** `fig2_arquitectura.png` y `fig2_arquitectura.pdf`
- **Ancho final:** 120.0 mm ($2834\text{ px}$ a 600 dpi).
- **Tipografía:**
  - Títulos de bloques en negrita: **10.0 pt** (DejaVu Sans Bold).
  - Texto descriptivo y fórmulas internas: **9.0 pt** (DejaVu Sans Regular).
  - Flechas de flujo e interacciones: **8.5 pt** (DejaVu Sans Regular).
- **Contenido rigurosamente modelado:**
  - **Estado / Gobierno:** Parámetros fiscales ($\tau$, $\mu_0, \mu_1, \xi$, auditoría $P_{aud}$); subsidio al cumplimiento digital DCC y red pública de cuidados.
  - **Trabajadores:** Estado formal/informal, comparación de utilidades $U_{i,F}$ vs. $U_{i,I}$, carga de cuidado no remunerado $H_{care,i}$, capital humano $h_i$, alfabetización digital $K_{dig,i}$.
  - **Empresas:** Estado formal/informal, comparación de beneficios esperados $\Pi_{j,F}$ vs. $\Pi_{j,I}$, riesgo de auditoría $P_{aud,j}$, costo de cumplimiento $DCC_j$, mecanismo estocástico de Metropolis-Hastings.
  - **Interacción de Mercado:** Flecha explícita *"Vacantes formales asignadas por ranking de productividad"*.
- **Diseño Gráfico:** Bloques vectoriales con bordes redondeados y fondos diferenciados de alto contraste con jerarquía visual estructurada.

### Fig. 3. Panel Principal del Sistema (Kenia, Escenario D, Mes 120)
- **Archivos:** `fig3_panel_kenia_D.png`, `fig3_panel_kenia_D.pdf`, `fig3a_tarjetas_indicadores.png`, `fig3b_grafico_trayectorias.png`.
- **Ancho final:** 145.0 mm ($3425\text{ px}$ a 600 dpi).
- **Fuente de datos:** Simulación real del modelo (Kenia, Escenario D integrado, mes 120).
- **Captura con Playwright:**
  - Dispositivo calibrado con `device_scale_factor = 4`.
  - Captura aislada por selector DOM (`locator.screenshot`):
    - `(a)` Tarjetas de indicadores (`#dashboard-kpi-cards`): informalidad, brecha de género, recaudación fiscal y coeficiente Gini.
    - `(b)` Gráfico interactivo Recharts (`#dashboard-sim-chart`): *"Simulación ITDT (meses 1–120 de la política)"*.
  - Ocultación total de barras de navegación, botones y menús mediante inyección CSS editorial.
  - Tipografía inyectada: etiquetas numéricas principales a $34\text{ px}$ (15.5 pt en papel), títulos de tarjeta a $20\text{ px}$ (9.5 pt en papel), ejes y leyendas a $18\text{ px}$ (8.6 pt en papel).
- **Verificación de Cifras:**
  - Tasa de informalidad simulada: **51.8 %** (coincide exactamente con el valor del modelo).
  - Brecha de género: **+1.29 p.p.**

### Fig. 4. Vista 3D del Gemelo Digital (Kenia, Mes 120: Escenarios A y B2)
- **Archivos:** `fig4_gemelo3d_kenia.png`, `fig4_gemelo3d_kenia.pdf`, `fig4a_gemelo3d_kenia_A.png`, `fig4b_gemelo3d_kenia_B2.png`.
- **Ancho final:** 145.0 mm compuesto ($3425\text{ px}$ a 600 dpi; dos paneles de 71.5 mm / 1690 px cada uno con canal de separación de 45 px).
- **Parámetros de Cámara:** Distancia fija documentada $46.0$, $\phi = 0.65\text{ rad}$, $\theta = \pi/4$, objetivo focal en $(0, 1.0, 0)$.
- **Valores Leídos Directamente del Modelo:**
  - Escenario A: **87.1 %** de informalidad.
  - Escenario B2: **49.2 %** de informalidad.
- **Tipografía y Leyenda:**
  - Renderizada directamente sobre los paneles al tamaño final para evitar compresión tipográfica:
    - Cartela superior: `"(a) Escenario A – mes 120 – informalidad 87.1 %"` a **9.0 pt** (75 px a 600 dpi).
    - Leyenda inferior: *"Trabajador formal"* (círculo cian), *"Trabajador informal"* (círculo ámbar), *"Empresa formal"* (cuadrado esmeralda) a **8.16 pt** (68 px a 600 dpi).
- **Composición:** Recorte de márgenes periféricos vacíos para que el terreno ocupe el área activa del panel.

### Fig. 5. Barrido de la Intensidad de Sanción
- **Archivos:** `fig5_barrido_sanciones.png` y `fig5_barrido_sanciones.pdf`
- **Ancho final:** 145.0 mm; **Alto:** 80.0 mm ($3425 \times 1889\text{ px}$ a 600 dpi).
- **Fuente de datos:** `outputs/sanctions_sweep_data.csv`
- **Ejes y Variables:**
  - Eje X: Multiplicador de sanción de $1.0$ a $4.0$.
  - Eje Y Izquierdo (p.p.):
    - $\Delta$ Total (línea azul marino continua, marcador circular).
    - $\Delta$ Mujeres (línea fucsia discontinua `[6, 3]`, marcador cuadrado).
    - $\Delta$ Hombres (línea azul cielo discontinua fina `[4, 2]`, marcador triangular).
    - $\Delta$ Brecha (línea ámbar punteada `[2, 2]`, marcador romboidal).
    - Bandas de dispersión de $\pm 1$ desviación estándar para cada métrica.
  - Eje Y Derecho (%): Cierre anual de empresas (gráfico de barras achurado en gris pizarra con trama diagonal `//` para garantizar legibilidad en B&W).
- **Tipografía:**
  - Títulos de ejes: **9.5 pt**.
  - Marcas de ejes (*ticks*): **8.5 pt**.
  - Leyenda inferior (2 filas fuera del área de datos): **8.5 pt**.
- **Coincidencia Exacta de Puntos de Datos:**
  - Multiplicador 1.0: $\Delta\text{ Total} = +0.13\text{ p.p.}$, $\text{Cierre} = 0.00\%$.
  - Multiplicador 2.5: $\Delta\text{ Total} = -35.48\text{ p.p.}$, $\text{Cierre} = 27.14\%$.
  - Multiplicador 4.0: $\Delta\text{ Total} = -36.40\text{ p.p.}$, $\text{Cierre} = 15.61\%$.

### Fig. 6. Informalidad por Escenario y Sexo (Meses 109–120)
- **Archivos:** `fig6_niveles_escenarios.png` y `fig6_niveles_escenarios.pdf`
- **Ancho final:** 145.0 mm; **Alto:** 75.0 mm ($3425 \times 1771\text{ px}$ a 600 dpi).
- **Fuente de datos:** `outputs/table5_levels.csv`
- **Estructura Gráfica:**
  - Barras agrupadas por escenario: Mujeres, Hombres y Total con barras de error ($\pm 1\text{ SD}$).
  - Tramas diferenciadas para impresión en escala de grises:
    - Mujeres: trama densa cruzada (`xx`).
    - Hombres: trama diagonal continua (`//`).
    - Total: fondo sólido con borde reforzado.
  - Anotación superior en cada grupo: *"Brecha (M − H): +X.XX p.p."*.
  - Etiquetas del eje X: *"A: statu quo"*, *"B1: GovTech moderado"*, *"B2: GovTech intensivo"*, *"C: red de cuidados"*, *"D: integrado"*.
- **Tipografía:**
  - Título del eje Y: **9.5 pt**.
  - Etiquetas de escenarios en eje X: **8.5 pt** en negrita.
  - Marcas numéricas y leyendas: **8.5 pt**.
  - Anotaciones de brecha sobre las barras: **8.0 pt**.
- **Coincidencia con Tabla 5:**
  - Escenario A: Total $88.31\%$, M $93.75\%$, H $84.90\%$, Brecha $+8.85\text{ p.p.}$
  - Escenario B1: Total $88.42\%$, M $93.79\%$, H $85.05\%$, Brecha $+8.74\text{ p.p.}$
  - Escenario B2: Total $52.88\%$, M $75.99\%$, H $36.94\%$, Brecha $+39.04\text{ p.p.}$
  - Escenario C: Total $87.48\%$, M $87.91\%$, H $87.21\%$, Brecha $+0.70\text{ p.p.}$
  - Escenario D: Total $51.70\%$, M $52.80\%$, H $50.93\%$, Brecha $+1.87\text{ p.p.}$

---

## 4. Metodología de Verificación Automatizada

Se implementó el script de control de calidad [`scripts/verificar_figuras_articulo.py`](file:///c:/Users/PC%20ASUS/Desktop/gemelo-digital-3d-del-mercado-laboral/scripts/verificar_figuras_articulo.py), el cual realiza 3 baterías de pruebas independientes:

```bash
.\.venv\Scripts\python.exe scripts/verificar_figuras_articulo.py
```

### Resultados de la Batería de Pruebas:
1. **Prueba 1: Dimensiones y Metadatos de Resolución (PASS)**
   - Comprueba que cada PNG posea exactamente los píxeles requeridos para 600 dpi.
   - Comprueba la existencia sincronizada del archivo vectorial `.pdf`.
2. **Prueba 2: Simulación de Impresión a 300 dpi y Medición Tipográfica (PASS)**
   - Se reduce cada figura al ancho de columna correspondiente a 300 dpi ($1713\text{ px}$ para 145 mm).
   - Se calcula la altura en puntos de la letra más pequeña según la relación física:
     $$\text{Puntos (pt)} = \frac{\text{Altura en Píxeles}}{\text{DPI} / 72}$$
   - **Resultado:** Ningún texto en ninguna figura queda por debajo de **$8.0\text{ pt}$**.
3. **Prueba 3: Integridad de Datos Numéricos (PASS)**
   - Coincidencia bit a bit entre los datos graficados en las Figuras 5 y 6 y los archivos de referencia `sanctions_sweep_data.csv` y `table5_levels.csv`.
   - Coincidencia estricta de las Figuras 3 y 4 con las trayectorias de `outputs/trayectorias_mensuales.json`.

---

## 5. Control de Integridad de la Base de Código

Se confirmó mediante Git que ningún archivo de resultados original previo fue modificado:

```bash
git diff 4773d96 -- outputs/table*.md outputs/table*.csv outputs/figure*.png outputs/*.json
# Salida limpia (sin cambios en archivos preexistentes)
```

Todos los archivos generados fueron colocados exclusivamente en `outputs/figuras_articulo/`, preservando la totalidad del historial econométrico previo.
