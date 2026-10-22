#!/usr/bin/env python3
"""
scripts/fetch_ilostat_calibracion.py

Descarga datos oficiales de calibración de informalidad laboral por sexo
desde la API SDMX oficial de ILOSTAT para los 4 países del modelo ITDT:
  - Kenia (KEN): 2019
  - Nigeria (NGA): 2024
  - India (IND): 2024
  - Bangladés (BGD): 2023

Indicador:
  EMP_NIFL_SEX_RT: Informal employment rate by sex (%)
  Frecuencia anual (A), desglosado por:
    - SEX_T: Total
    - SEX_F: Mujeres
    - SEX_M: Hombres

Flujo:
  1. Consulta la API SDMX de ILOSTAT (https://sdmx.ilo.org/rest/data/ILO,DF_EMP_NIFL_SEX_RT/...).
  2. Guarda los JSON crudos en data/raw/ilostat_calibracion_{codigo}_raw.json.
  3. Extrae las tasas, la fuente exacta y el tipo de dato (encuesta vs estimación modelada).
  4. Genera data/ilostat_calibracion.csv con las columnas:
     pais, codigo, anio, sexo, tasa, fuente, tipo_dato, fecha_descarga, url
"""

import os
import json
import csv
import ssl
import urllib.request
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
OUTPUT_CSV = os.path.join(DATA_DIR, "ilostat_calibracion.csv")

os.makedirs(RAW_DIR, exist_ok=True)

TARGET_COUNTRIES = [
    {"pais": "Kenia", "codigo": "KEN", "anio": 2019},
    {"pais": "Nigeria", "codigo": "NGA", "anio": 2024},
    {"pais": "India", "codigo": "IND", "anio": 2024},
    {"pais": "Bangladés", "codigo": "BGD", "anio": 2023},
]

INDICATOR = "EMP_NIFL_SEX_RT"


def _build_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def fetch_country_sdmx(country_code: str, year: int) -> Tuple[Optional[dict], Optional[str]]:
    """Descarga de la API SDMX oficial de ILOSTAT para un país y año determinados."""
    url = (
        f"https://sdmx.ilo.org/rest/data/ILO,DF_{INDICATOR}/"
        f"{country_code}.A..SEX_T+SEX_F+SEX_M"
        f"?startPeriod={year}&endPeriod={year}"
    )
    headers = {
        "User-Agent": "LaborTwin-DigitalTwin/1.0 (+https://github.com/ILO/ITDT)",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url, headers=headers)
    ctx = _build_ssl_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            raw_bytes = resp.read()
            payload = json.loads(raw_bytes.decode("utf-8"))
            return payload, url
    except Exception as e:
        print(f"  [Error SDMX] {country_code} ({year}): {e}")
        return None, None


def parse_sdmx_calibration(payload: dict, target_year: int) -> List[Dict[str, Any]]:
    """Extrae las observaciones de informalidad total, masculina y femenina."""
    structure = payload.get("structure", {})
    series_dims = structure.get("dimensions", {}).get("series", [])
    obs_dims = structure.get("dimensions", {}).get("observation", [])
    time_values = [v.get("id") for v in obs_dims[0].get("values", [])] if obs_dims else []

    attributes_obs = structure.get("attributes", {}).get("observation", [])

    datasets = payload.get("dataSets", [])
    if not datasets:
        return []

    records = []
    series_data = datasets[0].get("series", {})

    for series_key, series_val in series_data.items():
        indices = [int(x) for x in series_key.split(":")]
        dim_map = {}
        for dim_idx, val_idx in enumerate(indices):
            if dim_idx < len(series_dims):
                dim_id = series_dims[dim_idx].get("id")
                dim_val = series_dims[dim_idx]["values"][val_idx].get("id")
                dim_map[dim_id] = dim_val

        sex_code = dim_map.get("SEX")
        observations = series_val.get("observations", {})

        for time_idx_str, obs_record in observations.items():
            time_idx = int(time_idx_str)
            obs_year = time_values[time_idx] if time_idx < len(time_values) else str(target_year)

            if str(target_year) == str(obs_year):
                val = float(obs_record[0]) if obs_record and obs_record[0] is not None else None
                if val is not None:
                    # Extraer atributos de observación (SOURCE, NOTE_SOURCE, OBS_STATUS, etc.)
                    o_attrs = obs_record[1:] if len(obs_record) > 1 else []
                    attr_dict = {}
                    for a_idx, a_val_idx in enumerate(o_attrs):
                        if a_idx < len(attributes_obs):
                            a_id = attributes_obs[a_idx].get("id")
                            avals = attributes_obs[a_idx].get("values", [])
                            if a_val_idx is not None and a_val_idx < len(avals):
                                val_str = avals[a_val_idx].get("name", avals[a_val_idx].get("id"))
                            elif len(avals) == 1:
                                val_str = avals[0].get("name", avals[0].get("id"))
                            else:
                                val_str = ""
                            attr_dict[a_id] = val_str

                    # Si SOURCE o NOTE_SOURCE no vinieron explícitos en o_attrs, tomarlos de la estructura si son univaluados
                    for a_struct in attributes_obs:
                        a_id = a_struct.get("id")
                        if a_id in ["SOURCE", "NOTE_SOURCE"] and not attr_dict.get(a_id):
                            avals = a_struct.get("values", [])
                            if len(avals) == 1:
                                attr_dict[a_id] = avals[0].get("name", avals[0].get("id"))

                    # Determinar fuente y tipo de dato
                    source_str = attr_dict.get("SOURCE", "")
                    note_source = attr_dict.get("NOTE_SOURCE", "")
                    full_source = f"{source_str} ({note_source})" if note_source and source_str else (source_str or note_source or "ILOSTAT Micro data processing")

                    # Clasificación: encuesta o estimación modelada
                    tipo_dato = "encuesta"
                    source_lower = full_source.lower()
                    if "modelled" in source_lower or "model" in source_lower or "estimación modelada" in source_lower:
                        tipo_dato = "estimación modelada"
                    elif "survey" in source_lower or "lfs" in source_lower or "household" in source_lower or "encuesta" in source_lower:
                        tipo_dato = "encuesta"

                    records.append({
                        "sex_code": sex_code,
                        "year": int(obs_year),
                        "tasa": round(val, 2),
                        "tasa_raw": val,
                        "fuente": full_source,
                        "tipo_dato": tipo_dato,
                    })

    return records


def main():
    print("=" * 75)
    print("ILOSTAT API Fetcher - Calibración Oficial ITDT (EMP_NIFL_SEX_RT)")
    print("=" * 75)

    download_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    all_rows = []

    sex_label_map = {
        "SEX_T": "Total",
        "SEX_F": "Mujeres",
        "SEX_M": "Hombres",
    }

    for target in TARGET_COUNTRIES:
        pais = target["pais"]
        code = target["codigo"]
        anio = target["anio"]

        print(f"\n[*] Descargando {pais} ({code}) año {anio} desde SDMX ILOSTAT...")
        payload, url = fetch_country_sdmx(code, anio)

        if not payload:
            print(f"  [!] ERROR: No se pudo obtener respuesta SDMX para {code} {anio}")
            continue

        # Guardar JSON crudo
        raw_path = os.path.join(RAW_DIR, f"ilostat_calibracion_{code}_raw.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"  [+] JSON crudo guardado en: {raw_path}")

        records = parse_sdmx_calibration(payload, anio)
        print(f"  [+] Observaciones encontradas: {len(records)}")

        for r in records:
            sex_label = sex_label_map.get(r["sex_code"], r["sex_code"])
            print(f"      - {sex_label} ({r['sex_code']}): {r['tasa']}% (raw: {r['tasa_raw']}) | Fuente: {r['fuente']} | Tipo: {r['tipo_dato']}")
            all_rows.append({
                "pais": pais,
                "codigo": code,
                "anio": anio,
                "sexo": sex_label,
                "tasa": r["tasa"],
                "fuente": r["fuente"],
                "tipo_dato": r["tipo_dato"],
                "fecha_descarga": download_date,
                "url": url,
            })

    # Ordenar por país, año, y orden de sexo (Total, Mujeres, Hombres)
    sex_order = {"Total": 0, "Mujeres": 1, "Hombres": 2}
    all_rows.sort(key=lambda x: (x["codigo"], x["anio"], sex_order.get(x["sexo"], 3)))

    # Guardar en data/ilostat_calibracion.csv
    fieldnames = [
        "pais", "codigo", "anio", "sexo", "tasa", "fuente", "tipo_dato", "fecha_descarga", "url"
    ]
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n[+] CSV de calibración guardado exitosamente en: {OUTPUT_CSV}")
    print(f"[+] Total registros generados: {len(all_rows)}")


if __name__ == "__main__":
    main()
