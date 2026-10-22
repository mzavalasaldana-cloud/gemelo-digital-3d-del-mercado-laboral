#!/usr/bin/env python3
"""
Validación de gradientes no calibrados vs datos reales de ILOSTAT (Tabla 13).
Compara la informalidad simulada en el Escenario A (itdt) con los datos
oficiales de ILOSTAT almacenados en data/ilostat_gradientes.csv.

No modifica ninguna lógica del modelo.
"""

import json
import os
import sys
import numpy as np
import pandas as pd

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    results_path = os.path.join(repo_root, "outputs", "policy_experiments_results.json")
    ilostat_path = os.path.join(repo_root, "data", "ilostat_gradientes.csv")
    out_dir = os.path.join(repo_root, "outputs")
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(results_path):
        print(f"ERROR: No se encontró {results_path}. Ejecuta make all primero.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(ilostat_path):
        print(f"ERROR: No se encontró {ilostat_path}. Ejecuta scripts/fetch_ilostat_gradientes.py primero.", file=sys.stderr)
        sys.exit(1)

    with open(results_path, "r", encoding="utf-8") as f:
        sim_data = json.load(f)

    ilo_df = pd.read_csv(ilostat_path)

    # Definición de países y mapeos
    country_specs = [
        {"key": "KENYA", "name": "Kenia", "code": "KEN"},
        {"key": "NIGERIA", "name": "Nigeria", "code": "NGA"},
        {"key": "INDIA", "name": "India", "code": "IND"},
        {"key": "BANGLADESH", "name": "Bangladés", "code": "BGD"},
    ]

    dimension_specs = [
        {
            "dim": "Educación",
            "cat_label": "Básica (e = 0)",
            "model_field": ("education", "basic_e0"),
            "ilo_ind": "EMP_NIFL_SEX_EDU_RT",
            "ilo_cat": "EDU_AGGREGATE_BAS",
        },
        {
            "dim": "Educación",
            "cat_label": "Media (e = 1)",
            "model_field": ("education", "middle_e1"),
            "ilo_ind": "EMP_NIFL_SEX_EDU_RT",
            "ilo_cat": "EDU_AGGREGATE_INT",
        },
        {
            "dim": "Educación",
            "cat_label": "Superior (e = 2)",
            "model_field": ("education", "advanced_e2"),
            "ilo_ind": "EMP_NIFL_SEX_EDU_RT",
            "ilo_cat": "EDU_AGGREGATE_ADV",
        },
        {
            "dim": "Zona",
            "cat_label": "Rural",
            "model_field": ("zone", "rural"),
            "ilo_ind": "EMP_NIFL_SEX_GEO_RT",
            "ilo_cat": "GEO_COV_RUR",
        },
        {
            "dim": "Zona",
            "cat_label": "Urbana",
            "model_field": ("zone", "urban"),
            "ilo_ind": "EMP_NIFL_SEX_GEO_RT",
            "ilo_cat": "GEO_COV_URB",
        },
    ]

    rows = []
    country_mae = {}

    for c in country_specs:
        c_key = c["key"]
        c_name = c["name"]
        c_code = c["code"]

        if c_key not in sim_data or "A" not in sim_data[c_key]:
            print(f"ADVERTENCIA: No hay datos simulados para {c_key} en escenario A", file=sys.stderr)
            continue

        runs_A = sim_data[c_key]["A"]
        c_errors = []

        for dim in dimension_specs:
            field_group, field_name = dim["model_field"]
            sim_vals = [r["gradients"][field_group][field_name] for r in runs_A]
            sim_mean = float(np.mean(sim_vals))

            # Buscar dato real ILOSTAT
            sub = ilo_df[
                (ilo_df["pais_codigo"] == c_code)
                & (ilo_df["indicador"] == dim["ilo_ind"])
                & (ilo_df["categoria"] == dim["ilo_cat"])
                & (ilo_df["sexo"] == "SEX_T")
            ]

            if not sub.empty:
                obs_val = float(sub["valor"].values[0])
                obs_year = int(sub["anio"].values[0])
                abs_err = abs(sim_mean - obs_val)
                c_errors.append(abs_err)
                obs_str = f"{obs_val:.2f}"
                abs_err_str = f"{abs_err:.2f}"
            else:
                obs_val = np.nan
                obs_year = "Sin dato"
                abs_err = np.nan
                obs_str = "Sin datos reales disponibles"
                abs_err_str = "N/A"

            rows.append({
                "pais": c_name,
                "pais_codigo": c_code,
                "dimension": dim["dim"],
                "categoria": dim["cat_label"],
                "indicador_ilostat": dim["ilo_ind"],
                "codigo_ilostat": dim["ilo_cat"],
                "anio_observado": obs_year,
                "tasa_observada_ilostat": obs_val,
                "tasa_simulada_itdt": round(sim_mean, 2),
                "error_absoluto_pp": round(abs_err, 2) if not np.isnan(abs_err) else np.nan
            })

        if c_errors:
            country_mae[c_name] = float(np.mean(c_errors))
        else:
            country_mae[c_name] = np.nan

    df_table13 = pd.DataFrame(rows)

    # Guardar CSV
    csv_path = os.path.join(out_dir, "table13_gradientes_vs_ilostat.csv")
    df_table13.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"Guardado CSV en: {csv_path}")

    # Generar Markdown
    md_path = os.path.join(out_dir, "table13_gradientes_vs_ilostat.md")
    
    # Preparar tabla formateada para Markdown
    md_display_rows = []
    for r in rows:
        md_display_rows.append({
            "País": r["pais"],
            "Dimensión": r["dimension"],
            "Categoría": r["categoria"],
            "Año Obs.": r["anio_observado"],
            "Tasa Obs. ILOSTAT (%)": f"{r['tasa_observada_ilostat']:.2f}" if not pd.isna(r['tasa_observada_ilostat']) else "Sin datos",
            "Tasa Sim. ITDT (%)": f"{r['tasa_simulada_itdt']:.2f}",
            "Error Abs. (pp)": f"{r['error_absoluto_pp']:.2f}" if not pd.isna(r['error_absoluto_pp']) else "N/A",
        })
    df_display = pd.DataFrame(md_display_rows)

    total_errors = df_table13["error_absoluto_pp"].dropna().tolist()
    overall_mae = float(np.mean(total_errors)) if total_errors else 0.0

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Tabla 13: Validación de gradientes no calibrados frente a microdatos agregados de ILOSTAT (Escenario A)\n\n")
        f.write(df_display.to_markdown(index=False))
        f.write("\n\n### Error Medio Absoluto (MAE) por país\n\n")
        f.write("| País | MAE Gradientes (pp) |\n")
        f.write("|:---|:---:|\n")
        for c_name, mae_val in country_mae.items():
            f.write(f"| {c_name} | {mae_val:.2f} |\n")
        f.write(f"| **Promedio 4 países** | **{overall_mae:.2f}** |\n\n")
        f.write("---\n")
        f.write("### Notas metodológicas y emparejamiento de categorías\n\n")
        f.write("1. **Emparejamiento de educación:**\n")
        f.write("   - **Básica ($e = 0$):** Emparejada con `EDU_AGGREGATE_BAS` de ILOSTAT (*Basic education*: primaria completa o secundaria baja / ISCED 1-2).\n")
        f.write("   - **Media ($e = 1$):** Emparejada con `EDU_AGGREGATE_INT` de ILOSTAT (*Intermediate education*: secundaria alta o post-secundaria no terciaria / ISCED 3-4).\n")
        f.write("   - **Superior ($e = 2$):** Emparejada con `EDU_AGGREGATE_ADV` de ILOSTAT (*Advanced education*: educación terciaria y universitaria / ISCED 5-8).\n\n")
        f.write("2. **Emparejamiento geográfico:**\n")
        f.write("   - **Rural:** Emparejada con `GEO_COV_RUR` de ILOSTAT (*Rural area coverage*).\n")
        f.write("   - **Urbana:** Emparejada con `GEO_COV_URB` de ILOSTAT (*Urban area coverage*).\n\n")
        f.write("3. **Años observados y disponibilidad empírica:**\n")
        f.write("   - **Kenia (KEN):** 2019 (coincide exactamente con el año de calibración).\n")
        f.write("   - **Nigeria (NGA):** 2022 (año empírico más cercano disponible con desagregación completa en ILOSTAT; 2024 sólo posee series nacionales modeladas).\n")
        f.write("   - **India (IND):** 2012 (año más reciente con microdatos armonizados completos de ambas dimensiones en la serie anual de ILOSTAT).\n")
        f.write("   - **Bangladés (BGD):** 2022 para educación (`EMP_NIFL_SEX_EDU_RT`) y 2017 para zona geográfica (`EMP_NIFL_SEX_GEO_RT`), correspondientes a las rondas oficiales de la Labour Force Survey disponibles.\n\n")
        f.write("4. **Principio de no imputación:** Ningún dato ausente ha sido estimado ni rellenado; todas las cifras observadas provienen directamente del repositorio oficial de ILOSTAT.\n")

    print(f"Guardado Markdown en: {md_path}")
    print("\nResumen MAE por país:")
    for c_name, mae_val in country_mae.items():
        print(f"  {c_name}: {mae_val:.2f} pp")
    print(f"  Promedio total: {overall_mae:.2f} pp")

if __name__ == "__main__":
    main()
