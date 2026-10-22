#!/usr/bin/env python3
"""
scripts/generar_fuentes_calibracion.py

Extrae directamente de data/ilostat_s_F.csv y data/ilostat_series_historicas.csv
la fuente oficial exacta de calibración para cada uno de los 4 países.
Genera src/data/ilostat_calibracion_fuentes.json sin texto escrito a mano.
"""

import os
import csv
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_JSON = os.path.join(BASE_DIR, "src", "data", "ilostat_calibracion_fuentes.json")

PAIS_NOMBRES = {
    "KEN": "Kenia",
    "NGA": "Nigeria",
    "IND": "India",
    "BGD": "Bangladés",
    "KENYA": "Kenia",
    "NIGERIA": "Nigeria",
    "INDIA": "India",
    "BANGLADESH": "Bangladés",
}

def generar():
    s_F_path = os.path.join(DATA_DIR, "ilostat_s_F.csv")
    if not os.path.exists(s_F_path):
        raise FileNotFoundError(f"No existe {s_F_path}")

    fuentes = {}
    with open(s_F_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cc = row["country_code"].strip().upper()
            c_key = "KENYA" if cc == "KEN" else ("NIGERIA" if cc == "NGA" else ("INDIA" if cc == "IND" else "BANGLADESH"))
            src_raw = row["source"].strip()
            
            # El campo de fuente exacto de la encuesta ILOSTAT tras el identificador de la API
            parts = src_raw.split(";")
            survey_exact = parts[1].strip() if len(parts) > 1 else src_raw
            nombre_pais = PAIS_NOMBRES.get(cc, row["country"])
            
            fuentes[c_key] = {
                "country": nombre_pais,
                "country_code": cc,
                "year": int(row["year"]),
                "full_source": src_raw,
                "survey_exact": survey_exact,
                "label": f"{nombre_pais} ({survey_exact})",
            }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump(fuentes, out, indent=2, ensure_ascii=False)
    
    print(f"[+] Fuentes de calibración generadas exitosamente en: {OUTPUT_JSON}")
    for k, v in fuentes.items():
        print(f" -> {k}: {v['label']}")

if __name__ == "__main__":
    generar()
