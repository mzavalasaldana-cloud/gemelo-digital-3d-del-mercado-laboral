#!/usr/bin/env python3
"""
scripts/fetch_ilostat_series_historicas.py

Descarga series históricas reales de informalidad laboral por sexo desde la API de ILOSTAT
(Organización Internacional del Trabajo) para los 4 países del gemelo digital ITDT:
  - Kenia (KEN)
  - Nigeria (NGA)
  - India (IND)
  - Bangladés (BGD)

Indicador:
  EMP_NIFL_SEX_RT: Informal employment rate by sex (%)

Reglas estrictas:
  - NO imputar, NO interpolar, NO rellenar años vacíos.
  - Guardar respuestas crudas completas en data/raw/.
  - Guardar CSV consolidado en data/ilostat_series_historicas.csv.
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
OUTPUT_CSV = os.path.join(DATA_DIR, "ilostat_series_historicas.csv")

os.makedirs(RAW_DIR, exist_ok=True)

TARGET_COUNTRIES = [
    {"name": "Kenia", "code": "KEN"},
    {"name": "Nigeria", "code": "NGA"},
    {"name": "India", "code": "IND"},
    {"name": "Bangladés", "code": "BGD"},
]

INDICATOR = "EMP_NIFL_SEX_RT"

def _build_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def fetch_dbnomics_series(country_code: str) -> Tuple[Optional[dict], Optional[str]]:
    """Consulta la API de DBnomics para el indicador oficial de ILOSTAT."""
    url = (
        f"https://api.db.nomics.world/v22/series/ILO/{INDICATOR}"
        f"?dimensions=%7B%22ref_area%22%3A%5B%22{country_code}%22%5D%7D"
        f"&observations=1&limit=200"
    )
    headers = {"User-Agent": "LaborTwin-Research/1.0"}
    req = urllib.request.Request(url, headers=headers)
    ctx = _build_ssl_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data, url
    except Exception as e:
        print(f"  [Error DBnomics] {country_code}: {e}")
        return None, None

def main():
    print(f"=== Descargando series históricas reales de ILOSTAT ({INDICATOR}) ===")
    records = []
    download_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for c in TARGET_COUNTRIES:
        code = c["code"]
        name = c["name"]
        print(f"\nConsultando {name} ({code})...")

        raw_data, source_url = fetch_dbnomics_series(code)
        if raw_data is None:
            print(f"  [AVISO] No se pudo obtener respuesta de la API para {code}.")
            continue

        # Guardar respuesta cruda
        raw_filename = f"ilostat_series_historicas_{code}_raw.json"
        raw_filepath = os.path.join(RAW_DIR, raw_filename)
        with open(raw_filepath, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False)
        print(f"  Respuesta cruda guardada en {raw_filepath}")

        # Parsear series anuales por sexo (SEX_T, SEX_F, SEX_M)
        docs = raw_data.get("series", {}).get("docs", [])
        for doc in docs:
            dims = doc.get("dimensions", {})
            sex = dims.get("sex")
            freq = dims.get("frequency", "A")

            # Solo nos interesan las series anuales de Total, Mujeres y Hombres
            if freq == "A" and sex in ["SEX_T", "SEX_F", "SEX_M"]:
                sex_label = "Total" if sex == "SEX_T" else ("Mujeres" if sex == "SEX_F" else "Hombres")
                periods = doc.get("period", [])
                values = doc.get("value", [])

                for p, v in zip(periods, values):
                    # Solo años de 4 dígitos
                    if len(p) == 4 and p.isdigit() and v not in (None, "NA", ""):
                        try:
                            val_float = round(float(v), 2)
                            records.append({
                                "pais": name,
                                "codigo_pais": code,
                                "indicador": INDICATOR,
                                "sexo": sex_label,
                                "sexo_codigo": sex,
                                "anio": int(p),
                                "tasa_informalidad": val_float,
                                "fuente": f"ILOSTAT SDMX / DBnomics ({source_url})",
                                "fecha_descarga": download_date,
                            })
                            print(f"    - {name} ({p}) {sex_label}: {val_float}%")
                        except ValueError:
                            pass

    # Ordenar por país, año y sexo
    records.sort(key=lambda r: (r["codigo_pais"], r["anio"], r["sexo"]))

    # Guardar en CSV
    fieldnames = [
        "pais", "codigo_pais", "indicador", "sexo", "sexo_codigo",
        "anio", "tasa_informalidad", "fuente", "fecha_descarga"
    ]
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"\n[OK] CSV limpio guardado en: {OUTPUT_CSV}")
    print(f"Total registros históricos reales: {len(records)}")

if __name__ == "__main__":
    main()
