"""
streamlit_app.data.mock_data: Registros base, perfiles empíricos de países y datos de demostración.
- COUNTRY_PROFILES se construye dinámicamente a partir de itdt.parameters.COUNTRY_DATABASE y data/ilostat_s_F.csv.
- Las corridas de simulación se consultan desde la base de datos (/api/v1/simulations/history).
- Los elementos sin fuente real (usuarios, empresas, datasets sintéticos) están identificados como datos de demostración (DEMO_).
"""

import json
import logging
from typing import Dict, Any, List
from itdt.parameters import COUNTRY_DATABASE

logger = logging.getLogger("labortwin.mock_data")

# ==============================================================================
# 1. PERFILES DE PAÍSES (Fuente Real: COUNTRY_DATABASE y data/ilostat_s_F.csv)
# ==============================================================================

_UI_COUNTRY_METADATA: Dict[str, Dict[str, Any]] = {
    "KENYA": {
        "flag": "🇰🇪",
        "currency": "KES",
        "population": "54.0M",
        "keyClusters": ["Nairobi Silicon Savannah", "Mombasa Port Hub", "Jua Kali Artisan Basins", "Eldoret Agri-Valley"],
        "contextDescription": "Alta prevalencia del sector informal 'Jua Kali', microfinanzas móviles M-Pesa y polo tecnológico en Nairobi.",
        "iloComplianceScore": 58,
    },
    "NIGERIA": {
        "flag": "🇳🇬",
        "currency": "NGN",
        "population": "223.8M",
        "keyClusters": ["Lagos Financial Island", "Kano Commercial Axis", "Onitsha Market Hub", "Niger Delta Energy"],
        "contextDescription": "Mercados urbanos densos, comercio informal masivo en Lagos y brechas significativas entre el sector formal corporativo y microtalleres.",
        "iloComplianceScore": 51,
    },
    "INDIA": {
        "flag": "🇮🇳",
        "currency": "INR",
        "population": "1.428B",
        "keyClusters": ["Bengaluru Tech Triangle", "Maharashtra Manufacturing", "Ganga Rural Basin", "Surat Textile Clusters"],
        "contextDescription": "Enorme sector 'unorganized', transición de manufactura semi-formal y rápido crecimiento de plataformas gig de servicios.",
        "iloComplianceScore": 62,
    },
    "BANGLADESH": {
        "flag": "🇧🇩",
        "currency": "BDT",
        "population": "171.2M",
        "keyClusters": ["Dhaka RMG Ready-Made Garments", "Chittagong Maritime Corridor", "Sylhet Plantation Lowlands", "Khulna Delta Crafts"],
        "contextDescription": "Exportación textil masiva con encadenamientos de talleres informales subcontratados y microcréditos rurales.",
        "iloComplianceScore": 55,
    },
}


def build_country_profiles() -> Dict[str, Dict[str, Any]]:
    """
    Construye los perfiles de países derivando todas las métricas empíricas de
    itdt.parameters.COUNTRY_DATABASE (calibrado con data/ilostat_s_F.csv e ILOSTAT oficial).
    """
    profiles: Dict[str, Dict[str, Any]] = {}
    for c_key, c_info in COUNTRY_DATABASE.items():
        ui = _UI_COUNTRY_METADATA.get(c_key, {})
        profiles[c_key] = {
            "code": c_key,
            "name": f"{c_info['name']} (ILOSTAT {c_info.get('year', 2024)})",
            "country_name": c_info["name"],
            "country_code": c_info["country_code"],
            "flag": ui.get("flag", "🌐"),
            "currency": ui.get("currency", "USD"),
            "population": ui.get("population", "N/A"),
            "year": c_info.get("year", 2024),
            "baseInformalityRate": c_info["T_obs"],
            "baseInformalityFemale": c_info["F_obs"],
            "baseInformalityMale": c_info["M_obs"],
            "genderGap": round(c_info["F_obs"] - c_info["M_obs"], 2),
            "s_F": c_info["s_F"],
            "keyClusters": ui.get("keyClusters", []),
            "contextDescription": ui.get("contextDescription", ""),
            "iloComplianceScore": ui.get("iloComplianceScore", 50),
        }
    return profiles


COUNTRY_PROFILES: Dict[str, Dict[str, Any]] = build_country_profiles()

INITIAL_POLICY_STATE: Dict[str, float] = {
    "registrationCostReduction": 30.0,
    "smeSubsidyUSDMonth": 50.0,
    "skillsTrainingCoverage": 25.0,
    "socialProtectionTax": 12.0,
    "smartInspectionCoverage": 20.0,
}


# ==============================================================================
# 2. HISTORIAL DE CORRIDAS DE SIMULACIÓN (Fuente Real: DB /api/v1/simulations/history)
# ==============================================================================

def get_simulation_runs() -> List[Dict[str, Any]]:
    """
    Carga el historial de corridas de simulación desde la base de datos a través
    del endpoint /api/v1/simulations/history o consulta directa a PostgreSQL / SQLite.
    """
    # 1. Consulta al backend FastAPI
    try:
        import urllib.request
        req = urllib.request.Request("http://127.0.0.1:8000/api/v1/simulations/history", headers={"User-Agent": "StreamlitTwin"})
        with urllib.request.urlopen(req, timeout=1.2) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                runs = data.get("runs", [])
                if runs:
                    return runs
    except Exception:
        pass

    # 2. Fallback: consulta directa a la base de datos
    try:
        from backend.database import DATABASE_URL
        from sqlalchemy import create_engine, text
        sync_url = DATABASE_URL.replace("+asyncpg", "").replace("+aiosqlite", "")
        sync_engine = create_engine(sync_url)
        with sync_engine.connect() as conn:
            res = conn.execute(text("SELECT id, country, scenario, policy_params, final_metrics, duration_sec, created_at FROM simulation_runs ORDER BY created_at DESC LIMIT 25"))
            rows = res.fetchall()
            if rows:
                return [
                    {
                        "id": row[0],
                        "country": row[1],
                        "scenario": row[2],
                        "policy_params": row[3],
                        "final_metrics": row[4],
                        "duration_sec": row[5],
                        "created_at": str(row[6]),
                    }
                    for row in rows
                ]
    except Exception:
        pass

    return []


MOCK_SIM_RUNS: List[Dict[str, Any]] = get_simulation_runs()


# ==============================================================================
# 3. EMPRESAS Y PARTICIONES ESPACIALES (Datos de Demostración 3D)
# ==============================================================================

DEMO_FIRMS: List[Dict[str, Any]] = [
    {
        "id": "firm-f-01",
        "name": "Apex Synth & Tech Corp",
        "type": "formal",
        "x": -8.0,
        "z": -6.0,
        "height": 6.5,
        "sizeEmployees": 1420,
        "sectorCategory": "Tecnología",
        "productivityScore": 92,
        "formalizationCostUSD": 2400,
        "taxComplianceRate": 98,
        "color": "#00f0ff",
        "isDemo": True,
    },
    {
        "id": "firm-f-02",
        "name": "Metropolis Port Logistics Ltd",
        "type": "formal",
        "x": 7.0,
        "z": -7.0,
        "height": 5.2,
        "sizeEmployees": 980,
        "sectorCategory": "Logística",
        "productivityScore": 84,
        "formalizationCostUSD": 1800,
        "taxComplianceRate": 95,
        "color": "#00f0ff",
        "isDemo": True,
    },
    {
        "id": "firm-f-03",
        "name": "Vanguard Industrial Textiles",
        "type": "formal",
        "x": 0.0,
        "z": -10.0,
        "height": 7.8,
        "sizeEmployees": 2150,
        "sectorCategory": "Manufactura",
        "productivityScore": 89,
        "formalizationCostUSD": 3200,
        "taxComplianceRate": 99,
        "color": "#00f0ff",
        "isDemo": True,
    },
    {
        "id": "firm-f-04",
        "name": "BioAgro Processing Hub",
        "type": "formal",
        "x": 10.0,
        "z": 6.0,
        "height": 4.8,
        "sizeEmployees": 640,
        "sectorCategory": "Agroindustria",
        "productivityScore": 78,
        "formalizationCostUSD": 1400,
        "taxComplianceRate": 91,
        "color": "#00f0ff",
        "isDemo": True,
    },
    {
        "id": "firm-f-05",
        "name": "Equator Solar & Tech Solutions",
        "type": "formal",
        "x": -11.0,
        "z": 7.0,
        "height": 5.5,
        "sizeEmployees": 820,
        "sectorCategory": "Tecnología",
        "productivityScore": 86,
        "formalizationCostUSD": 2100,
        "taxComplianceRate": 94,
        "color": "#00f0ff",
        "isDemo": True,
    },
    {
        "id": "firm-inf-01",
        "name": "Mercado Artesanal Jua Kali",
        "type": "informal_mycelium",
        "x": -3.0,
        "z": 12.0,
        "height": 1.8,
        "sizeEmployees": 450,
        "sectorCategory": "Servicios Personales",
        "productivityScore": 38,
        "formalizationCostUSD": 450,
        "taxComplianceRate": 12,
        "color": "#f59e0b",
        "isDemo": True,
    },
    {
        "id": "firm-inf-02",
        "name": "Red de Comercio Ambulante Central",
        "type": "informal_mycelium",
        "x": 6.0,
        "z": 14.0,
        "height": 1.5,
        "sizeEmployees": 720,
        "sectorCategory": "Comercio & Retail",
        "productivityScore": 32,
        "formalizationCostUSD": 300,
        "taxComplianceRate": 5,
        "color": "#f59e0b",
        "isDemo": True,
    },
]

# Alias de compatibilidad
MOCK_FIRMS = DEMO_FIRMS


# ==============================================================================
# 4. USUARIOS INSTITUCIONALES (Datos de Demostración RBAC)
# ==============================================================================

DEMO_USERS: List[Dict[str, Any]] = [
    {
        "id": "usr-001",
        "name": "Dra. Elena Rostova (Demostración)",
        "email": "elena.rostova@example.org",
        "role": "ADMIN",
        "department": "Dirección de Modelado Macroeconómico",
        "lastActive": "Activo ahora",
        "avatar": "👩‍💼",
        "permissions": {
            "editPolicies": True,
            "retrainAI": True,
            "manageDatasets": True,
            "manageUsers": True,
            "exportReports": True,
        },
        "isDemo": True,
    },
    {
        "id": "usr-002",
        "name": "Carlos Mendoza (Demostración)",
        "email": "carlos.mendoza@example.org",
        "role": "POLICY_ANALYST",
        "department": "Análisis de Políticas de Empleo",
        "lastActive": "Hace 15 min",
        "avatar": "👨‍💼",
        "permissions": {
            "editPolicies": True,
            "retrainAI": False,
            "manageDatasets": True,
            "manageUsers": False,
            "exportReports": True,
        },
        "isDemo": True,
    },
    {
        "id": "usr-003",
        "name": "Dr. Kwame Achebe (Demostración)",
        "email": "kwame.achebe@example.org",
        "role": "RESEARCHER",
        "department": "Investigación Laboral (Demostración)",
        "lastActive": "Hace 2 horas",
        "avatar": "🧑‍🔬",
        "permissions": {
            "editPolicies": False,
            "retrainAI": True,
            "manageDatasets": True,
            "manageUsers": False,
            "exportReports": True,
        },
        "isDemo": True,
    },
    {
        "id": "usr-004",
        "name": "Sofia Lindqvist (Demostración)",
        "email": "sofia.lindqvist@example.org",
        "role": "AUDITOR",
        "department": "Auditoría de Modelado (Demostración)",
        "lastActive": "Ayer",
        "avatar": "🕵️‍♀️",
        "permissions": {
            "editPolicies": False,
            "retrainAI": False,
            "manageDatasets": False,
            "manageUsers": False,
            "exportReports": True,
        },
        "isDemo": True,
    },
]

# Alias de compatibilidad
MOCK_USERS = DEMO_USERS


# ==============================================================================
# 5. DATASETS SINTÉTICOS DE PRECARGA (Datos de Demostración)
# ==============================================================================

DEMO_DATASETS: List[Dict[str, Any]] = [
    {
        "id": "ds-plfs-india",
        "name": "SINTETICO_calibrado_PLFS_India.csv",
        "country": "INDIA",
        "records": 48500,
        "variables": 14,
        "sampleType": "Datos sintéticos de demostración; no son microdatos oficiales",
        "institution": "Generador sintético calibrado (Demostración)",
        "fileFormat": "CSV / Sintético Demostración",
        "isVerified": False,
        "isDemo": True,
    },
    {
        "id": "ds-knbs-kenya",
        "name": "SINTETICO_calibrado_KNBS_Kenya.csv",
        "country": "KENYA",
        "records": 38000,
        "variables": 14,
        "sampleType": "Datos sintéticos de demostración; no son microdatos oficiales",
        "institution": "Generador sintético calibrado (Demostración)",
        "fileFormat": "CSV / Sintético Demostración",
        "isVerified": False,
        "isDemo": True,
    },
    {
        "id": "ds-nbs-nigeria",
        "name": "SINTETICO_calibrado_NBS_Nigeria.csv",
        "country": "NIGERIA",
        "records": 42000,
        "variables": 14,
        "sampleType": "Datos sintéticos de demostración; no son microdatos oficiales",
        "institution": "Generador sintético calibrado (Demostración)",
        "fileFormat": "CSV / Sintético Demostración",
        "isVerified": False,
        "isDemo": True,
    },
    {
        "id": "ds-bbs-bangladesh",
        "name": "SINTETICO_calibrado_BBS_Bangladesh.csv",
        "country": "BANGLADESH",
        "records": 36000,
        "variables": 14,
        "sampleType": "Datos sintéticos de demostración; no son microdatos oficiales",
        "institution": "Generador sintético calibrado (Demostración)",
        "fileFormat": "CSV / Sintético Demostración",
        "isVerified": False,
        "isDemo": True,
    },
]

# Alias de compatibilidad
PRELOADED_DATASETS = DEMO_DATASETS


# ==============================================================================
# 6. INDICADORES DE TRABAJO DECENTE DE LA OIT (Metas ODS 8)
# ==============================================================================

ILO_DECENT_WORK_INDICATORS: List[Dict[str, Any]] = [
    {
        "id": "ilo-01",
        "code": "DW-INF",
        "name": "Tasa de Empleo Informal",
        "category": "Oportunidades de Empleo",
        "target2030": 45.0,
        "unit": "%",
        "higherIsBetter": False,
        "description": "Porcentaje de trabajadores en empleos sin cobertura de seguridad social ni registro legal.",
    },
    {
        "id": "ilo-02",
        "code": "DW-LOWPAY",
        "name": "Tasa de Salarios Bajos (<2/3 Mediana)",
        "category": "Ingresos Adecuados",
        "target2030": 12.0,
        "unit": "%",
        "higherIsBetter": False,
        "description": "Trabajadores asalariados que ganan menos de dos tercios del salario por hora mediano.",
    },
    {
        "id": "ilo-03",
        "code": "DW-HOURS",
        "name": "Jornadas Excesivas (>48h/semana)",
        "category": "Tiempo de Trabajo Decente",
        "target2030": 15.0,
        "unit": "%",
        "higherIsBetter": False,
        "description": "Porcentaje de personas ocupadas que laboran habitualmente más de 48 horas semanales.",
    },
    {
        "id": "ilo-04",
        "code": "DW-SOCPROT",
        "name": "Cobertura Efectiva de Seguridad Social",
        "category": "Protección Social",
        "target2030": 70.0,
        "unit": "%",
        "higherIsBetter": True,
        "description": "Proporción de la población económicamente activa cubierta por al menos un esquema de protección social.",
    },
    {
        "id": "ilo-05",
        "code": "DW-GENDERGAP",
        "name": "Brecha Salarial de Género no Ajustada",
        "category": "Igualdad de Oportunidades",
        "target2030": 8.0,
        "unit": "%",
        "higherIsBetter": False,
        "description": "Diferencia porcentual entre los ingresos medianos de hombres y mujeres.",
    },
    {
        "id": "ilo-06",
        "code": "DW-UNION",
        "name": "Densidad Sindical y Negociación Colectiva",
        "category": "Diálogo Social",
        "target2030": 35.0,
        "unit": "%",
        "higherIsBetter": True,
        "description": "Porcentaje de trabajadores afiliados a sindicatos u organizaciones representativas.",
    },
    {
        "id": "ilo-07",
        "code": "DW-YOUTHNEET",
        "name": "Jóvenes sin Empleo, Educación ni Capacitación (NINI)",
        "category": "Estabilidad y Juventud",
        "target2030": 10.0,
        "unit": "%",
        "higherIsBetter": False,
        "description": "Proporción de jóvenes de 15 a 24 años desvinculados del sistema formativo y laboral.",
    },
    {
        "id": "ilo-08",
        "code": "DW-SAFETY",
        "name": "Tasa de Lesiones Ocupacionales Fatales",
        "category": "Medio Ambiente de Trabajo Seguro",
        "target2030": 1.5,
        "unit": "por 100k",
        "higherIsBetter": False,
        "description": "Lesiones de trabajo mortales por cada 100.000 trabajadores en el sector formal e informal.",
    },
]
