#!/usr/bin/env python3
"""
scripts/generar_fuentes_calibracion.py

Extrae directamente de data/ilostat_calibracion.csv la fuente oficial exacta
de calibración para cada uno de los 4 países.
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
    calib_path = os.path.join(DATA_DIR, "ilostat_calibracion.csv")
    if not os.path.exists(calib_path):
        raise FileNotFoundError(f"No existe {calib_path}")

    fuentes = {}
    with open(calib_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["sexo"].strip().lower() != "total":
                continue
            cc = row["codigo"].strip().upper()
            c_key = "KENYA" if cc == "KEN" else ("NIGERIA" if cc == "NGA" else ("INDIA" if cc == "IND" else "BANGLADESH"))
            src_raw = row["fuente"].strip()
            
            # Formato encuesta
            nombre_pais = PAIS_NOMBRES.get(cc, row["pais"])
            
            # Etiqueta limpia y concisa: País (Fuente corta año)
            fuentes[c_key] = {
                "country": nombre_pais,
                "country_code": cc,
                "year": int(row["anio"]),
                "full_source": src_raw,
                "tipo_dato": row.get("tipo_dato", "encuesta"),
                "label": f"{nombre_pais} ({src_raw.split('(')[0].strip()} {row['anio']})",
            }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as out:
        json.dump(fuentes, out, indent=2, ensure_ascii=False)
    
    print(f"[+] Fuentes de calibración generadas exitosamente en: {OUTPUT_JSON}")
    for k, v in fuentes.items():
        print(f"  * {k}: {v['label']} | {v['full_source']}")

if __name__ == "__main__":
    generar()
