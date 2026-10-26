#!/usr/bin/env python3
"""
scripts/fetch_ilostat_gradientes.py

Descarga datos reales de informalidad desagregada por:
  1. Sexo y Educación (EMP_NIFL_SEX_EDU_RT)
  2. Sexo y Zona Geográfica Rural/Urbana (EMP_NIFL_SEX_GEO_RT)
desde las fuentes oficiales de ILOSTAT (API SDMX y API DBnomics de la OIT)
para los 4 países del gemelo digital ITDT:
  - Kenia (KEN): 2019
  - Nigeria (NGA): 2024 (o más cercano disponible: 2022)
  - India (IND): 2024 (o más cercano disponible: 2022)
  - Bangladés (BGD): 2023 (o más cercano disponible: 2022 / 2017)

Guarda las respuestas crudas en data/raw/ y el CSV consolidado en data/ilostat_gradientes.csv.
Reporta de forma rigurosa las combinaciones que no existen sin imputar ni rellenar.
"""

import os
import json
import csv
import ssl
import urllib.request
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional, Any

# Rutas del repositorio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
OUTPUT_CSV = os.path.join(DATA_DIR, "ilostat_gradientes.csv")

TARGET_COUNTRIES = [
    {"name": "Kenya", "code": "KEN", "target_year": 2019},
    {"name": "Nigeria", "code": "NGA", "target_year": 2024},
    {"name": "India", "code": "IND", "target_year": 2024},
    {"name": "Bangladesh", "code": "BGD", "target_year": 2023},
]

INDICATORS = [
    {
        "indicator": "EMP_NIFL_SEX_EDU_RT",
        "description": "Informality rate by sex and education (aggregated levels)",
        "target_classifs": [
            "EDU_AGGREGATE_BAS",
            "EDU_AGGREGATE_INT",
            "EDU_AGGREGATE_ADV",
            "EDU_AGGREGATE_LTB",
            "EDU_AGGREGATE_TOTAL",
        ],
    },
    {
        "indicator": "EMP_NIFL_SEX_GEO_RT",
        "description": "Informality rate by sex and geographic area (urban/rural)",
        "target_classifs": [
            "GEO_COV_RUR",
            "GEO_COV_URB",
            "GEO_COV_NAT",
        ],
    },
]


def _build_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_sdmx_data(indicator: str, country_code: str) -> Tuple[Optional[dict], Optional[str]]:
    """Consulta la API SDMX REST de ILOSTAT."""
    url = f"https://sdmx.ilo.org/rest/data/ILO,DF_{indicator}/{country_code}.../?lastNObservations=10"
    headers = {
        "User-Agent": "LaborTwin-DigitalTwin/1.0 (+https://github.com/ILO/ITDT)",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers)
    ctx = _build_ssl_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data, url
    except Exception:
        return None, None


def fetch_dbnomics_data(indicator: str, country_code: str) -> Tuple[Optional[dict], Optional[str]]:
    """Consulta el endpoint oficial de ILOSTAT en DBnomics con todas las observaciones."""
    url = (
        f"https://api.db.nomics.world/v22/series/ILO/{indicator}"
        f"?dimensions=%7B%22ref_area%22%3A%5B%22{country_code}%22%5D%7D"
        f"&observations=1&limit=200"
    )
    headers = {"User-Agent": "LaborTwin-DigitalTwin/1.0"}
    req = urllib.request.Request(url, headers=headers)
    ctx = _build_ssl_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data, url
    except Exception as e:
        print(f"  [Error DBnomics] {country_code} / {indicator}: {e}")
        return None, None


def parse_dbnomics_series(
    data: dict,
    target_classifs: List[str],
    target_year: int,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Extrae observaciones para las categorías objetivo.
    Prioriza el año objetivo exacto (anual 'A'); si no existe, toma el año anual más cercano disponible.
    """
    docs = data.get("series", {}).get("docs", [])
    extracted_rows: List[Dict[str, Any]] = []
    available_years_by_classif: Dict[str, List[str]] = {}

    # Agrupar series por (sex, classif1, freq)
    series_candidates: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for doc in docs:
        dims = doc.get("dimensions", {})
        sex = dims.get("sex")
        classif = dims.get("classif1")
        freq = dims.get("frequency", "A")

        if classif in target_classifs and sex in ["SEX_T", "SEX_F", "SEX_M"]:
            periods = doc.get("period", [])
            values = doc.get("value", [])
            series_candidates[(sex, classif, freq)] = {
                "doc": doc,
                "periods": periods,
                "values": values,
            }
            if classif not in available_years_by_classif:
                available_years_by_classif[classif] = []
            available_years_by_classif[classif].extend(periods)

    # Para cada par (sex, classif), seleccionar la mejor observación
    unique_pairs = {(sex, classif) for (sex, classif, freq) in series_candidates.keys()}

    for sex, classif in sorted(unique_pairs):
        # 1. Preferir serie anual (freq == 'A')
        candidate_entry = series_candidates.get((sex, classif, "A"))
        if not candidate_entry:
            # Buscar trimestral si no hay anual
            candidate_entry = series_candidates.get((sex, classif, "Q"))

        if not candidate_entry:
            continue

        periods = candidate_entry["periods"]
        values = candidate_entry["values"]

        # Filtrar valores no nulos
        valid_points = []
        for p, v in zip(periods, values):
            if v is not None and v != "NA":
                try:
                    val_float = float(v)
                    # Extraer año numérico (e.g. '2019' o '2019-Q1' -> 2019)
                    year_num = int(p.split("-")[0])
                    valid_points.append((year_num, p, val_float))
                except (ValueError, TypeError):
                    pass

        if not valid_points:
            continue

        # Ordenar por proximidad al año objetivo, prefiriendo período anual exacto
        def sort_key(pt):
            y_num, p_str, _ = pt
            dist = abs(y_num - target_year)
            is_annual = 0 if len(p_str) == 4 else 1
            is_exact = 0 if y_num == target_year else 1
            return (dist, is_exact, is_annual, -y_num)

        valid_points.sort(key=sort_key)
        best_point = valid_points[0]

        extracted_rows.append({
            "sexo": sex,
            "categoria": classif,
            "anio": best_point[1],  # período seleccionado
            "valor": round(best_point[2], 2),
            "series_code": candidate_entry["doc"].get("series_code", ""),
        })

    return extracted_rows, available_years_by_classif


def main():
    print("=" * 70)
    print("ILOSTAT API Fetcher - Gradientes de Informalidad (Educación y Zona)")
    print("=" * 70)

    os.makedirs(RAW_DIR, exist_ok=True)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    csv_rows = []
    manifest: Dict[str, Any] = {
        "metadata": {
            "title": "ILOSTAT Gradients by Education and Geographic Area",
            "query_date": today_str,
            "indicators": [ind["indicator"] for ind in INDICATORS],
            "countries": [c["code"] for c in TARGET_COUNTRIES],
        },
        "raw_files": [],
        "missing_combinations": [],
    }

    for ind_info in INDICATORS:
        ind_code = str(ind_info["indicator"])
        raw_classifs = ind_info["target_classifs"]
        target_classifs: List[str] = list(raw_classifs) if isinstance(raw_classifs, list) else [raw_classifs]
        print(f"\n>>> Indicador: {ind_code} ({ind_info['description']})")

        for country in TARGET_COUNTRIES:
            c_name = str(country["name"])
            c_code = str(country["code"])
            c_target_year = int(country["target_year"])

            print(f"\n  [+] Consultando {c_name} ({c_code}), objetivo año {c_target_year}...")

            # 1. Intentar consulta SDMX
            payload_sdmx, url_sdmx = fetch_sdmx_data(ind_code, c_code)
            data_source_used = "SDMX"
            payload = payload_sdmx
            api_url = url_sdmx

            # 2. Si no o si SDMX viene vacío, usar DBnomics
            if not payload:
                payload_dbn, url_dbn = fetch_dbnomics_data(ind_code, c_code)
                if payload_dbn:
                    payload = payload_dbn
                    api_url = url_dbn
                    data_source_used = "DBnomics"

            if not payload:
                print(f"      [AVISO] No se obtuvo respuesta para {c_code} en {ind_code}.")
                manifest["missing_combinations"].append({
                    "country": c_code,
                    "indicator": ind_code,
                    "reason": "API endpoint returned no data",
                })
                continue

            # Guardar archivo raw original
            raw_filename = f"ilostat_{ind_code}_{c_code}_raw.json"
            raw_path = os.path.join(RAW_DIR, raw_filename)
            with open(raw_path, "w", encoding="utf-8") as f_raw:
                json.dump(
                    {
                        "indicator": ind_code,
                        "country_code": c_code,
                        "country_name": c_name,
                        "target_year": c_target_year,
                        "source_type": data_source_used,
                        "api_url": api_url,
                        "fetched_at": today_str,
                        "payload": payload,
                    },
                    f_raw,
                    indent=2,
                    ensure_ascii=False,
                )
            manifest["raw_files"].append(raw_filename)
            print(f"      -> Crudo guardado en: data/raw/{raw_filename}")

            # Procesar series
            parsed_rows, available_years = parse_dbnomics_series(payload, target_classifs, c_target_year)

            # Verificar si faltaron categorías esperadas
            found_classifs = {r["categoria"] for r in parsed_rows}
            for expected_cl in target_classifs:
                if expected_cl not in found_classifs:
                    manifest["missing_combinations"].append({
                        "country": c_code,
                        "indicator": ind_code,
                        "missing_classif": expected_cl,
                        "reason": f"No observada en datos ILOSTAT para {c_code}",
                    })
                    print(f"      [FALTANTE] Categoría {expected_cl} no disponible en ILOSTAT para {c_code}.")

            for r in parsed_rows:
                csv_rows.append({
                    "pais": c_name,
                    "pais_codigo": c_code,
                    "indicador": ind_code,
                    "sexo": r["sexo"],
                    "categoria": r["categoria"],
                    "anio": r["anio"],
                    "valor": r["valor"],
                    "fuente_url": api_url,
                    "fecha_descarga": today_str,
                })
                print(f"      - {r['categoria']} | {r['sexo']} ({r['anio']}): {r['valor']:.2f}%")

    # Guardar manifiesto de raw
    manifest_path = os.path.join(RAW_DIR, "ilostat_gradientes_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f_m:
        json.dump(manifest, f_m, indent=2, ensure_ascii=False)

    # Guardar CSV consolidado limpio
    fieldnames = [
        "pais",
        "pais_codigo",
        "indicador",
        "sexo",
        "categoria",
        "anio",
        "valor",
        "fuente_url",
        "fecha_descarga",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print("\n" + "=" * 70)
    print(f"[OK] data/ilostat_gradientes.csv generado con {len(csv_rows)} observaciones oficiales.")
    print(f"[OK] Manifiesto y crudos registrados en data/raw/")
    print("=" * 70)

    # Imprimir resumen de faltantes reportados
    if manifest["missing_combinations"]:
        print("\n--- COMBINACIONES FALTANTES REPORTADAS RIGUROSAMENTE (SIN IMPUTAR) ---")
        for m in manifest["missing_combinations"]:
            print(f"  * {m}")
        print("----------------------------------------------------------------------")


if __name__ == "__main__":
    main()
