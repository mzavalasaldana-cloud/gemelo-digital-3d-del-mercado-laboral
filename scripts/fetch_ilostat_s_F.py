#!/usr/bin/env python3
"""
scripts/fetch_ilostat_s_F.py

Descarga datos de empleo por sexo y edad desde la API oficial de ILOSTAT
(Organización Internacional del Trabajo / International Labour Organization)
para los 4 países del gemelo digital ITDT:
  - Kenia (KEN): 2019
  - Nigeria (NGA): 2024
  - India (IND): 2024
  - Bangladés (BGD): 2023

Indicador:
  DF_EMP_TEMP_SEX_AGE_NB: Employment by sex and age (thousands)
  Población en edad de trabajar: AGE_YTHADULT_YGE15 (15 años o más)

Flujo:
  1. Consulta la API REST/SDMX de ILOSTAT (https://sdmx.ilo.org/rest/data/...)
     con fallback secundario a la API de series ILO en DBnomics.
  2. Guarda la respuesta original completa de la API en data/raw/.
  3. Extrae las observaciones de empleo femenino (SEX_F), masculino (SEX_M) y total (SEX_T).
  4. Calcula la proporción s_F = empleo_femenino / empleo_total.
  5. Regenera el archivo data/ilostat_s_F.csv con los momentos empíricos oficiales.
"""

import os
import sys
import json
import csv
import ssl
import urllib.request
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional

# Directorios de destino
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
OUTPUT_CSV = os.path.join(DATA_DIR, "ilostat_s_F.csv")

# Países y años objetivo para la calibración del gemelo digital ITDT
TARGET_COUNTRIES = [
    {
        "country": "Kenya",
        "country_code": "KEN",
        "year": 2019,
        "source_label": "ILOSTAT SDMX API (DF_EMP_TEMP_SEX_AGE_NB); KNBS KPHC / ILO Microdata",
    },
    {
        "country": "Nigeria",
        "country_code": "NGA",
        "year": 2024,
        "source_label": "ILOSTAT SDMX API (DF_EMP_TEMP_SEX_AGE_NB); NBS NLFS / ILO Modelled Estimates 2024",
    },
    {
        "country": "India",
        "country_code": "IND",
        "year": 2024,
        "source_label": "ILOSTAT SDMX API (DF_EMP_TEMP_SEX_AGE_NB); MoSPI PLFS / ILO Microdata 2024",
    },
    {
        "country": "Bangladesh",
        "country_code": "BGD",
        "year": 2023,
        "source_label": "ILOSTAT SDMX API (DF_EMP_TEMP_SEX_AGE_NB); BBS QLFS / ILO Microdata 2023",
    },
]

INDICATOR = "EMP_TEMP_SEX_AGE_NB"


def _build_ssl_context() -> ssl.SSLContext:
    """Crea un contexto SSL permisivo para evitar fallos de certificados en proxies locales."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_country_sdmx(country_code: str, year: int) -> Tuple[Optional[dict], Optional[str]]:
    """
    Descarga desde la API SDMX oficial de ILOSTAT:
    https://sdmx.ilo.org/rest/data/ILO,DF_EMP_TEMP_SEX_AGE_NB/...
    """
    # Key SDMX: [REF_AREA].[FREQ].[MEASURE].[SEX].[AGE]
    url = (
        f"https://sdmx.ilo.org/rest/data/ILO,DF_{INDICATOR}/"
        f"{country_code}.A..SEX_F+SEX_M+SEX_T.AGE_YTHADULT_YGE15"
        f"?startPeriod={year}&endPeriod={year}"
    )
    headers = {
        "User-Agent": "LaborTwin-DigitalTwin/1.0 (+https://github.com/ILO/ITDT)",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers)
    ctx = _build_ssl_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            raw_bytes = resp.read()
            payload = json.loads(raw_bytes.decode("utf-8"))
            return payload, url
    except Exception as e:
        print(f"  [Aviso] Fallo consulta SDMX para {country_code} ({e}). Intentando fallback...")
        return None, None


def fetch_country_dbnomics_fallback(country_code: str, year: int) -> Tuple[Optional[dict], Optional[str]]:
    """
    Fallback secundario a la API de DBnomics (proveedor oficial ILO):
    https://api.db.nomics.world/v22/series/ILO/EMP_TEMP_SEX_AGE_NB
    """
    url = (
        f"https://api.db.nomics.world/v22/series/ILO/{INDICATOR}"
        f"?dimensions=%7B%22ref_area%22%3A%5B%22{country_code}%22%5D%2C%22classif1%22%3A%5B%22AGE_AGGREGATE_TOTAL%22%2C%22AGE_YTHADULT_YGE15%22%5D%7D"
        f"&observations=1&limit=50"
    )
    headers = {"User-Agent": "LaborTwin-DigitalTwin/1.0"}
    req = urllib.request.Request(url, headers=headers)
    ctx = _build_ssl_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            raw_bytes = resp.read()
            payload = json.loads(raw_bytes.decode("utf-8"))
            return payload, url
    except Exception as e:
        print(f"  [Aviso] Fallo fallback DBnomics para {country_code} ({e}).")
        return None, None


def parse_sdmx_response(payload: dict, target_year: int) -> Dict[str, float]:
    """Extrae SEX_F, SEX_M, SEX_T para el año objetivo a partir del JSON de SDMX ILOSTAT."""
    structure = payload.get("structure", {})
    series_dims = structure.get("dimensions", {}).get("series", [])
    obs_dims = structure.get("dimensions", {}).get("observation", [])
    
    time_values = []
    if obs_dims:
        time_values = [v.get("id") for v in obs_dims[0].get("values", [])]

    results: Dict[str, float] = {}
    datasets = payload.get("dataSets", [])
    if not datasets:
        return results

    series_data = datasets[0].get("series", {})
    for series_key, series_val in series_data.items():
        indices = [int(x) for x in series_key.split(":")]
        dim_map = {}
        for dim_idx, val_idx in enumerate(indices):
            if dim_idx < len(series_dims):
                dim_id = series_dims[dim_idx].get("id")
                dim_val = series_dims[dim_idx]["values"][val_idx].get("id")
                dim_map[dim_id] = dim_val

        sex = dim_map.get("SEX")
        observations = series_val.get("observations", {})
        for time_idx_str, obs_record in observations.items():
            time_idx = int(time_idx_str)
            obs_year = time_values[time_idx] if time_idx < len(time_values) else str(target_year)
            if str(target_year) in str(obs_year):
                if obs_record and obs_record[0] is not None:
                    val = float(obs_record[0])
                    if sex in ["SEX_F", "SEX_M", "SEX_T"]:
                        results[sex] = val

    return results


def parse_dbnomics_response(payload: dict, target_year: int) -> Dict[str, float]:
    """Extrae SEX_F, SEX_M, SEX_T a partir del JSON de DBnomics."""
    results: Dict[str, float] = {}
    docs = payload.get("series", {}).get("docs", [])
    year_str = str(target_year)

    for doc in docs:
        dims = doc.get("dimensions", {})
        sex = dims.get("sex")
        periods = doc.get("period", [])
        values = doc.get("value", [])

        if year_str in periods:
            idx = periods.index(year_str)
            val = values[idx]
            if val is not None and val != "NA":
                results[sex] = float(val)

    return results


def main():
    print("=" * 70)
    print("ILOSTAT API Fetcher - Calibración s_F para el Gemelo Digital ITDT")
    print("=" * 70)

    # 1. Asegurar existencia de data/raw/
    os.makedirs(RAW_DIR, exist_ok=True)
    print(f"Directorio raw listo: {RAW_DIR}")

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    all_raw_manifest = {
        "metadata": {
            "title": "ILOSTAT Raw Response Collection - Employment by Sex and Age",
            "indicator": INDICATOR,
            "fetched_at": today_str,
            "countries": [c["country_code"] for c in TARGET_COUNTRIES],
        },
        "responses": {},
    }

    csv_rows = []

    for item in TARGET_COUNTRIES:
        c_name = item["country"]
        c_code = item["country_code"]
        c_year = item["year"]
        c_source = item["source_label"]

        print(f"\n[+] Descargando datos para {c_name} ({c_code}, año {c_year})...")

        # Intentar SDMX primario
        payload, api_url = fetch_country_sdmx(c_code, c_year)
        parsed_vals = {}
        api_type = "SDMX"

        if payload:
            parsed_vals = parse_sdmx_response(payload, c_year)
        else:
            # Fallback DBnomics
            payload, api_url = fetch_country_dbnomics_fallback(c_code, c_year)
            api_type = "DBnomics"
            if payload:
                parsed_vals = parse_dbnomics_response(payload, c_year)

        if not payload:
            raise RuntimeError(f"Error crítico: no se pudo obtener respuesta de la API para {c_code}")

        # Guardar respuesta cruda original individual en data/raw/
        raw_filename = f"ilostat_{INDICATOR}_{c_code}_{c_year}_raw.json"
        raw_filepath = os.path.join(RAW_DIR, raw_filename)
        with open(raw_filepath, "w", encoding="utf-8") as f_raw:
            json.dump(
                {
                    "country": c_name,
                    "country_code": c_code,
                    "target_year": c_year,
                    "api_source": api_type,
                    "request_url": api_url,
                    "download_timestamp": datetime.now(timezone.utc).isoformat(),
                    "response": payload,
                },
                f_raw,
                indent=2,
                ensure_ascii=False,
            )
        print(f"  -> Respuesta cruda guardada en: data/raw/{raw_filename}")

        all_raw_manifest["responses"][c_code] = {
            "country": c_name,
            "year": c_year,
            "raw_file": raw_filename,
            "api_url": api_url,
            "parsed_metrics": parsed_vals,
        }

        # Extraer métricas de empleo en miles
        f_emp = parsed_vals.get("SEX_F")
        m_emp = parsed_vals.get("SEX_M")
        t_emp = parsed_vals.get("SEX_T")

        if f_emp is None or m_emp is None:
            raise ValueError(f"No se encontraron observaciones de empleo para SEX_F/SEX_M en {c_code} ({c_year})")

        if t_emp is None or t_emp <= 0:
            t_emp = round(f_emp + m_emp, 3)

        # Proporción oficial de empleo femenino s_F
        s_F = round(f_emp / t_emp, 6)

        csv_rows.append({
            "country": c_name,
            "country_code": c_code,
            "year": c_year,
            "indicator": INDICATOR,
            "employment_female_thousands": round(f_emp, 1),
            "employment_male_thousands": round(m_emp, 1),
            "employment_total_thousands": round(t_emp, 1),
            "s_F": f"{s_F:.6f}",
            "source": c_source,
            "query_date": today_str,
        })

        print(f"  -> {c_name} ({c_year}): F={f_emp:.1f}k, M={m_emp:.1f}k, Total={t_emp:.1f}k => s_F = {s_F:.6f}")

    # Guardar manifiesto combinado en data/raw/
    manifest_filepath = os.path.join(RAW_DIR, f"ilostat_{INDICATOR}_all_raw.json")
    with open(manifest_filepath, "w", encoding="utf-8") as f_man:
        json.dump(all_raw_manifest, f_man, indent=2, ensure_ascii=False)
    print(f"\n[+] Manifiesto completo guardado en: data/raw/ilostat_{INDICATOR}_all_raw.json")

    # 4. Regenerar data/ilostat_s_F.csv
    fieldnames = [
        "country",
        "country_code",
        "year",
        "indicator",
        "employment_female_thousands",
        "employment_male_thousands",
        "employment_total_thousands",
        "s_F",
        "source",
        "query_date",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"\n[OK] data/ilostat_s_F.csv regenerado exitosamente.")
    print("-" * 70)
    with open(OUTPUT_CSV, "r", encoding="utf-8") as f_check:
        print(f_check.read())
    print("-" * 70)


if __name__ == "__main__":
    main()
