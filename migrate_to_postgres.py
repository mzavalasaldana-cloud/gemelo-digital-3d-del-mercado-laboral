import os
import psycopg2
import sqlite3
import json
from dotenv import load_dotenv

load_dotenv("backend/.env")

PG_HOST = "localhost"
PG_PORT = 5432
PG_USER = "postgres"
PG_PASS = "1234"
PG_DBNAME = "labortwin_db"

print("--- 1. Conectando a PostgreSQL y verificando/creando base de datos ---")
conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    user=PG_USER,
    password=PG_PASS,
    dbname="postgres"
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PG_DBNAME,))
if not cur.fetchone():
    cur.execute(f'CREATE DATABASE "{PG_DBNAME}"')
    print(f"[OK] Base de datos '{PG_DBNAME}' creada exitosamente en PostgreSQL.")
else:
    print(f"[OK] Base de datos '{PG_DBNAME}' ya existe en PostgreSQL.")

cur.close()
conn.close()

print("\n--- 2. Creando tablas en labortwin_db ---")
conn_app = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    user=PG_USER,
    password=PG_PASS,
    dbname=PG_DBNAME
)
conn_app.autocommit = True
cur_app = conn_app.cursor()

cur_app.execute("""
CREATE TABLE IF NOT EXISTS datasets (
    id VARCHAR(50) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(500) NOT NULL,
    records_count INTEGER DEFAULT 0,
    features_list JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_datasets_is_active ON datasets (is_active);

CREATE TABLE IF NOT EXISTS simulation_runs (
    id VARCHAR(100) PRIMARY KEY,
    country VARCHAR(50) NOT NULL,
    scenario VARCHAR(100) NOT NULL,
    policy_params JSONB DEFAULT '{}'::jsonb,
    final_metrics JSONB DEFAULT '{}'::jsonb,
    duration_sec FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS copilot_chat_history (
    id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    scenario VARCHAR(100),
    month INTEGER DEFAULT 0,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    source VARCHAR(50) DEFAULT 'langflow',
    flow_id VARCHAR(100),
    verified_metrics JSONB DEFAULT '{}'::jsonb,
    policy_params JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_copilot_session_id ON copilot_chat_history (session_id);
CREATE INDEX IF NOT EXISTS ix_copilot_created_at ON copilot_chat_history (created_at DESC);
""")
print("[OK] Tablas 'datasets', 'simulation_runs' y 'copilot_chat_history' creadas e indexadas en PostgreSQL.")

print("\n--- 3. Migrando datos existentes desde SQLite local (labortwin_dev.db si existe) ---")
sqlite_path = "labortwin_dev.db"
if os.path.exists(sqlite_path):
    sconn = sqlite3.connect(sqlite_path)
    scur = sconn.cursor()
    
    # Migrar datasets
    try:
        scur.execute("SELECT id, filename, filepath, records_count, features_list, is_active, created_at FROM datasets")
        rows = scur.fetchall()
        for r in rows:
            feat_json = json.loads(r[4]) if isinstance(r[4], str) else r[4]
            cur_app.execute("""
                INSERT INTO datasets (id, filename, filepath, records_count, features_list, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    filename = EXCLUDED.filename,
                    filepath = EXCLUDED.filepath,
                    records_count = EXCLUDED.records_count,
                    features_list = EXCLUDED.features_list,
                    is_active = EXCLUDED.is_active;
            """, (r[0], r[1], r[2], r[3], json.dumps(feat_json), bool(r[5]), r[6]))
        print(f"[OK] {len(rows)} datasets transferidos desde SQLite a PostgreSQL.")
    except Exception as e:
        print(f"Nota datasets: {e}")

    # Migrar simulation_runs
    try:
        scur.execute("SELECT id, country, scenario, policy_params, final_metrics, duration_sec, created_at FROM simulation_runs")
        srows = scur.fetchall()
        for r in srows:
            p_json = json.loads(r[3]) if isinstance(r[3], str) else r[3]
            m_json = json.loads(r[4]) if isinstance(r[4], str) else r[4]
            cur_app.execute("""
                INSERT INTO simulation_runs (id, country, scenario, policy_params, final_metrics, duration_sec, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    country = EXCLUDED.country,
                    scenario = EXCLUDED.scenario,
                    policy_params = EXCLUDED.policy_params,
                    final_metrics = EXCLUDED.final_metrics,
                    duration_sec = EXCLUDED.duration_sec;
            """, (r[0], r[1], r[2], json.dumps(p_json), json.dumps(m_json), r[5], r[6]))
        print(f"[OK] {len(srows)} corridas de simulacion transferidas desde SQLite a PostgreSQL.")
    except Exception as e:
        print(f"Nota simulation_runs: {e}")
        
    sconn.close()
else:
    print("No se encontro SQLite previo, se iniciara con esquema limpio y datasets oficiales.")

# 4. Insertar datasets oficiales predeterminados si no existen
default_datasets = [
    ("ds-knbs-ken", "KNBS_Kenya_Informal_Sector_Survey_2024.csv", "./data_store/KNBS_Kenya_Informal_Sector_Survey_2024.csv", 38000, ["ESTADO_LABORAL", "INGRESO_NETO_DIA", "CAPITAL_HUMANO", "EDAD", "EDUCACION_ANIOS", "APORTE_SEG_SOC", "TAM_EMPRESA"], True),
    ("ds-plfs-ind", "PLFS_India_Periodic_Labour_Force_Survey_2023-24.csv", "./data_store/PLFS_India_Periodic_Labour_Force_Survey_2023-24.csv", 48500, ["ESTADO_LABORAL", "INGRESO_NETO_DIA", "CAPITAL_HUMANO", "EDAD", "EDUCACION_ANIOS", "APORTE_SEG_SOC", "TAM_EMPRESA"], False),
    ("ds-nlss-nga", "NBS_Nigeria_Living_Standards_Survey_2023.csv", "./data_store/NBS_Nigeria_Living_Standards_Survey_2023.csv", 32000, ["ESTADO_LABORAL", "INGRESO_NETO_DIA", "CAPITAL_HUMANO", "EDAD", "EDUCACION_ANIOS", "APORTE_SEG_SOC", "TAM_EMPRESA"], False),
    ("ds-qlfs-bgd", "BBS_Bangladesh_Quarterly_Labour_Force_Survey_2024.csv", "./data_store/BBS_Bangladesh_Quarterly_Labour_Force_Survey_2024.csv", 29500, ["ESTADO_LABORAL", "INGRESO_NETO_DIA", "CAPITAL_HUMANO", "EDAD", "EDUCACION_ANIOS", "APORTE_SEG_SOC", "TAM_EMPRESA"], False),
]

for did, fname, fpath, rcount, flist, isact in default_datasets:
    cur_app.execute("""
        INSERT INTO datasets (id, filename, filepath, records_count, features_list, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (did, fname, fpath, rcount, json.dumps(flist), isact))

print("[OK] Datasets nacionales oficiales inicializados en PostgreSQL.")

cur_app.close()
conn_app.close()
print("\n[EXITO] Transferencia y configuracion de PostgreSQL completada exitosamente!")
