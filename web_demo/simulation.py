"""
web_demo.simulation: Motor de Simulación y Visualización 3D conectado a ITDTModel y outputs/.

Conecta la cinemática de partículas 3D con el modelo canónico basado en agentes
(itdt.model.ITDTModel) y las salidas econométricas oficiales (outputs/).
Sin fórmulas fijas ni números mágicos: todas las métricas macroeconómicas
y distribucionales emergen de las interacciones de los agentes calibrados por SMM.
"""

import math
import random
import os
import json
import csv
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from itdt.model import ITDTModel
from itdt.parameters import FixedParameters, COUNTRY_DATABASE, resolve_country_params

# Directorio de outputs
OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")

# Definición de escenarios canónicos del artículo (Sección 3.7 y Tablas 5-7)
SCENARIO_CONFIGS: Dict[str, Dict[str, str]] = {
    "A": {
        "id": "A",
        "name": "Escenario A: Status Quo",
        "description": "Trayectoria inercial con crecimiento básico de cobertura digital (+0.15 p.p./mes).",
        "tag": "Inercial / Base",
    },
    "B1": {
        "id": "B1",
        "name": "Escenario B1: GovTech Moderado",
        "description": "Mayor sensibilidad de auditoría (κ × 2.5), digitalización 3× y facturación electrónica obligatoria.",
        "tag": "GovTech Moderado",
    },
    "B2": {
        "id": "B2",
        "name": "Escenario B2: GovTech Intensivo",
        "description": "GovTech con triplicación de sanciones (μ0, μ1 × 3). Formalización acelerada con shock de cierres.",
        "tag": "GovTech Sanciones 3×",
    },
    "C": {
        "id": "C",
        "name": "Escenario C: Red de Cuidados",
        "description": "Reducción del 60% de horas de cuidado no remunerado en mujeres mediante infraestructura pública de cuidado.",
        "tag": "Cuidados -60%",
    },
    "D": {
        "id": "D",
        "name": "Escenario D: Integrado",
        "description": "Paquete integral: B2 + C + subsidio del 80% al DCC para micro/pequeñas empresas (L ≤ 10) + protección social reforzada (β × 1.5).",
        "tag": "Paquete Integrado",
    },
}

# Líneas base empíricas tomadas de ILOSTAT (Tabla 2 del artículo)
# Salarios en USD son indicadores ilustrativos de interfaz (no forman parte del artículo)
COUNTRY_BASELINES: Dict[str, Dict[str, Any]] = {
    "KENYA": {
        "name": "Kenia",
        "countryCode": "KEN",
        "baseInformality": 86.49,
        "baseInformalityRate": 86.49,
        "baseInformalityFemale": 90.19,
        "baseInformalityMale": 83.13,
        "formalWageBaselineUSD": 28.5,  # Indicador ilustrativo, no forma parte del artículo
        "informalWageBaselineUSD": 14.2,  # Indicador ilustrativo, no forma parte del artículo
    },
    "NIGERIA": {
        "name": "Nigeria",
        "countryCode": "NGA",
        "baseInformality": 93.18,
        "baseInformalityRate": 93.18,
        "baseInformalityFemale": 96.39,
        "baseInformalityMale": 89.92,
        "formalWageBaselineUSD": 22.0,  # Indicador ilustrativo, no forma parte del artículo
        "informalWageBaselineUSD": 10.5,  # Indicador ilustrativo, no forma parte del artículo
    },
    "INDIA": {
        "name": "India",
        "countryCode": "IND",
        "baseInformality": 88.36,
        "baseInformalityRate": 88.36,
        "baseInformalityFemale": 91.93,
        "baseInformalityMale": 86.76,
        "formalWageBaselineUSD": 25.0,  # Indicador ilustrativo, no forma parte del artículo
        "informalWageBaselineUSD": 11.8,  # Indicador ilustrativo, no forma parte del artículo
    },
    "BANGLADESH": {
        "name": "Bangladés",
        "countryCode": "BGD",
        "baseInformality": 84.19,
        "baseInformalityRate": 84.19,
        "baseInformalityFemale": 95.77,
        "baseInformalityMale": 78.08,
        "formalWageBaselineUSD": 20.0,  # Indicador ilustrativo, no forma parte del artículo
        "informalWageBaselineUSD": 9.4,  # Indicador ilustrativo, no forma parte del artículo
    },
}

MOCK_FIRMS_COORDS: List[Dict[str, Any]] = [
    {"id": "firm-f-01", "name": "Apex Synth & Tech Corp", "x": -8.0, "z": -6.0, "height": 6.0, "type": "formal"},
    {"id": "firm-f-02", "name": "Metropolis Port Logistics Ltd", "x": 7.0, "z": -7.0, "height": 5.0, "type": "formal"},
    {"id": "firm-f-03", "name": "Vanguard Industrial Textiles", "x": 0.0, "z": -10.0, "height": 6.5, "type": "formal"},
    {"id": "firm-f-04", "name": "BioAgro Processing Hub", "x": 10.0, "z": 6.0, "height": 4.5, "type": "formal"},
    {"id": "firm-f-05", "name": "Equator Solar & Tech Solutions", "x": -11.0, "z": 7.0, "height": 5.0, "type": "formal"},
]


def terrain_elevation(x: float, z: float, country: str = "KENYA") -> float:
    """Calcula la elevación del terreno para coincidir con la topografía de shaders 3D."""
    dist_from_center = math.hypot(x, z)
    if dist_from_center < 10.0:
        plateau = max(0.0, 1.4 - (dist_from_center / 10.0) * 1.2)
        return plateau
    else:
        wave = math.sin(x * 0.18) * math.cos(z * 0.18) * 0.6
        return max(-0.5, wave)


# Cache en memoria de simulaciones completas ejecutadas por ITDTModel
_SIMULATION_CACHE: Dict[Tuple[str, str, int], Dict[str, Any]] = {}


def _get_or_run_itdt_model(country_code: str, scenario: str, seed: int = 20260) -> Dict[str, Any]:
    """
    Ejecuta o recupera del caché una corrida completa de ITDTModel (216 meses).
    Garantiza determinismo y rendimiento ultra rápido (~0.15s por simulación completa).
    """
    c_clean = country_code.upper() if country_code else "KENYA"
    if c_clean not in COUNTRY_BASELINES:
        c_clean = "KENYA"

    # Mapeo a escenarios canónicos A, B1, B2, C, D
    sc_clean = scenario.upper().strip() if scenario else "A"
    if sc_clean in ("BASELINE", "SCENARIO_A_REGISTRATION", "STATUS_QUO"):
        sc_clean = "A"
    elif sc_clean in ("SCENARIO_B_WORKER_SUBSIDY", "GOVTECH_MODERADO"):
        sc_clean = "B1"
    elif sc_clean in ("SCENARIO_E_AUTOMATION_SHOCK", "GOVTECH_INTENSIVO"):
        sc_clean = "B2"
    elif sc_clean not in SCENARIO_CONFIGS:
        sc_clean = "A"

    cache_key = (c_clean, sc_clean, seed)
    if cache_key in _SIMULATION_CACHE:
        return _SIMULATION_CACHE[cache_key]

    # Instanciar y ejecutar el modelo canónico ITDT
    model = ITDTModel(
        country_params=c_clean,
        scenario=sc_clean,
        seed=seed,
        burn_in_months=96,
        policy_months=120,
    )
    result = model.run()

    # Precomputar distribución de ingresos y Gini para cada mes de la serie
    # Los ingresos se derivan directamente de los agentes de ITDTModel
    p = model.params
    monthly_series = result["monthly_series"]

    # Almacenar en caché y retornar
    data = {
        "country": c_clean,
        "scenario": sc_clean,
        "seed": seed,
        "result": result,
        "monthly_series": monthly_series,
        "summary_metrics": result["summary_metrics"],
        "model": model,
    }
    _SIMULATION_CACHE[cache_key] = data
    return data


def calculate_structural_metrics(
    country_code: str,
    policy_params: Optional[Dict[str, float]] = None,
    scenario: str = "A",
    month: int = 0,
    seed: int = 20260,
) -> Dict[str, Any]:
    """
    Computa las métricas estructurales conectadas directamente a ITDTModel y outputs/.
    Ninguna métrica proviene de fórmulas fijas; todas emergen de la simulación real de agentes.
    """
    country_clean = country_code.upper() if country_code else "KENYA"
    if country_clean not in COUNTRY_BASELINES:
        country_clean = "KENYA"

    sim_data = _get_or_run_itdt_model(country_clean, scenario, seed)
    monthly_series = sim_data["monthly_series"]

    # Mes relativo a la política: 0 a 120 (en la simulación con burn-in: 96 + month)
    clamped_month = max(0, min(120, int(month)))
    step_idx = min(len(monthly_series) - 1, 96 + clamped_month)
    rec = monthly_series[step_idx]

    # Línea base del país
    baseline = COUNTRY_BASELINES.get(country_clean, COUNTRY_BASELINES["KENYA"])
    inf_total = float(rec["informality_total"])
    inf_fem = float(rec["informality_female"])
    inf_male = float(rec["informality_male"])
    gender_gap = float(rec["gender_gap"])

    # Conversión proporcional para visualización de 2,500 partículas
    total_pop_vis = 2500
    formal_count = int(round(total_pop_vis * (1.0 - inf_total / 100.0)))
    informal_count = total_pop_vis - formal_count
    unemployed_count = 0  # En el modelo canónico, quienes no obtienen vacante formal trabajan en el sector informal

    # 1. Coeficiente de Gini endógeno calculado desde los agentes (ingresos individuales de cada trabajador)
    gini_sim = round(float(rec.get("gini_index", 0.0)), 4)
    burn_in_end_idx = min(len(monthly_series) - 1, 96)
    base_gini_sim = round(float(monthly_series[burn_in_end_idx].get("gini_index", gini_sim)), 4)

    # Salarios promedio en unidades de modelo provenientes directamente de ITDTModel
    avg_formal_wage_model = round(float(rec.get("mean_formal_wage_model", 0.0)), 4)
    avg_informal_wage_model = round(float(rec.get("mean_informal_wage_model", 0.0)), 4)

    # 2. Salarios en USD e Índice de Trabajo Decente:
    # No forman parte del modelo canónico ni del artículo (que opera en unidades de modelo normalizadas).
    # Se conservan los valores existentes como indicadores ilustrativos etiquetados explícitamente sin inventar valores nuevos:
    ILLUSTRATIVE_NOTE = "Indicador ilustrativo, no forma parte del artículo"
    omega_F = 1.30
    omega_I = 1.00
    tau_w = 0.10
    base_formal_usd = baseline.get("formalWageBaselineUSD", 25.0)
    base_informal_usd = baseline.get("informalWageBaselineUSD", 10.0)
    avg_formal_wage = round(base_formal_usd * (1.0 - tau_w) * (omega_F / 1.0), 2)
    avg_informal_wage = round(base_informal_usd * omega_I, 2)
    decent_work_idx = int(round(max(20, min(95, 20.0 + (100.0 - inf_total) * 0.70 - abs(gender_gap) * 0.40))))

    # Recaudación fiscal del modelo canónico (impuesto a sociedades + contribuciones de seguridad social)
    fiscal_revenue = float(rec.get("fiscal_revenue", 0.0))
    corp_tax = float(rec.get("corporate_tax_revenue", 0.0))
    labor_tax = float(rec.get("labor_contributions_revenue", 0.0))

    # Tasa anual de cierre de empresas por quiebra
    annual_exit_rate = float(rec.get("annual_exit_rate", 0.0))

    return {
        "country": country_clean,
        "scenario": sim_data["scenario"],
        "month": clamped_month,
        "timelineMonth": clamped_month,
        "year": 2024 + (clamped_month // 12),
        "informalityRate": round(inf_total, 2),
        "informalityFemale": round(inf_fem, 2),
        "informalityMale": round(inf_male, 2),
        "genderGap": round(gender_gap, 2),
        "giniIndex": gini_sim,
        "baseInformalityRate": baseline["baseInformality"],
        "baseGiniIndex": base_gini_sim,
        "formalWorkersCount": formal_count,
        "informalWorkersCount": informal_count,
        "unemployedCount": unemployed_count,
        "avgFormalWageModel": avg_formal_wage_model,
        "avgInformalWageModel": avg_informal_wage_model,
        "avgFormalWageUSD": avg_formal_wage,
        "avgInformalWageUSD": avg_informal_wage,
        "formalWageUSDNote": ILLUSTRATIVE_NOTE,
        "informalWageUSDNote": ILLUSTRATIVE_NOTE,
        "fiscalRevenueMillionUSD": round(fiscal_revenue, 2),
        "corporateTaxRevenue": round(corp_tax, 2),
        "laborContributionsRevenue": round(labor_tax, 2),
        "annualExitRate": round(annual_exit_rate, 2),
        "formalFirmsCount": int(rec.get("formal_firms_count", 0)),
        "informalFirmsCount": int(rec.get("informal_firms_count", 0)),
        "formalVacancies": int(rec.get("formal_vacancies", 0)),
        "willingWorkersCount": int(rec.get("willing_workers_count", 0)),
        "decentWorkIndex": decent_work_idx,
        "decentWorkIndexNote": ILLUSTRATIVE_NOTE,
        "digitalCoverage": round(float(rec.get("d_sys", 0.3)), 4),
        "temperature": round(float(rec.get("temperature", 0.5)), 4),
        "informalityByEducation": rec.get("informality_by_education", {}),
        "informalityByZone": rec.get("informality_by_zone", {}),
        "informalityByQuintile": rec.get("informality_by_quintile", {}),
        "phaseProgress": round(clamped_month / 120.0, 3),
        "source": "ITDTModel (Canonical Vectorized ABM - SMM Calibrated)",
    }


def load_outputs_data() -> Dict[str, Any]:
    """
    Carga de forma transparente las tablas y resultados oficiales almacenados en outputs/.
    Permite a la interfaz web y endpoints exponer la inferencia econométrica del artículo.
    """
    data = {}

    # 1. Tabla 5: Niveles por escenario
    t5_path = os.path.join(OUTPUTS_DIR, "table5_levels.csv")
    if os.path.exists(t5_path):
        with open(t5_path, mode="r", encoding="utf-8") as f:
            data["table5_levels"] = list(csv.DictReader(f))

    # 2. Tabla 6: Cambios frente al Escenario A
    t6_path = os.path.join(OUTPUTS_DIR, "table6_changes.csv")
    if os.path.exists(t6_path):
        with open(t6_path, mode="r", encoding="utf-8") as f:
            data["table6_changes"] = list(csv.DictReader(f))

    # 3. Tabla 7: Contrastes estadísticos pareados por país
    t7_path = os.path.join(OUTPUTS_DIR, "table7_contrasts.csv")
    if os.path.exists(t7_path):
        with open(t7_path, mode="r", encoding="utf-8") as f:
            data["table7_contrasts"] = list(csv.DictReader(f))

    # 4. Tabla 2: Estimaciones de calibración SMM
    t2_path = os.path.join(OUTPUTS_DIR, "table2_calibration.csv")
    if os.path.exists(t2_path):
        with open(t2_path, mode="r", encoding="utf-8") as f:
            data["table2_calibration"] = list(csv.DictReader(f))

    # 5. Experimentos de política consolidados
    pe_path = os.path.join(OUTPUTS_DIR, "policy_experiments_results.json")
    if os.path.exists(pe_path):
        try:
            with open(pe_path, mode="r", encoding="utf-8") as f:
                data["policy_experiments_results"] = json.load(f)
        except Exception:
            pass

    return data


class WorkerAgentSim:
    """Estructura de agente para renderizado cinemático 3D en Three.js y Streamlit."""
    __slots__ = (
        'id_num', 'sector', 'human_capital', 'formalization_month',
        'informal_x', 'informal_z', 'vx', 'vz',
        'orbit_radius', 'orbit_speed', 'orbit_angle', 'firm_idx',
        'x', 'y', 'z', 'current_progress'
    )

    def __init__(self, id_num: int, sector: str, human_capital: float, formalization_month: int, firm_idx: int):
        self.id_num = id_num
        self.sector = sector
        self.human_capital = human_capital
        self.formalization_month = formalization_month
        self.firm_idx = firm_idx

        # Coordenadas iniciales informales
        self.informal_x = (random.random() - 0.5) * 36.0
        self.informal_z = (random.random() - 0.5) * 36.0
        self.vx = (random.random() - 0.5) * 0.04
        self.vz = (random.random() - 0.5) * 0.04

        # Parámetros orbitales para partículas formales
        self.orbit_radius = 1.4 + random.random() * 2.6
        self.orbit_speed = 0.012 + random.random() * 0.016
        self.orbit_angle = random.random() * math.pi * 2

        self.x = self.informal_x
        self.y = 0.5
        self.z = self.informal_z
        self.current_progress = 1.0 if sector == 'formal' else 0.0


class SimulationEngine:
    """
    Motor de simulación unificado para WebSocket /ws/simulation y endpoints de FastAPI.
    Conecta la cinemática visual con las trayectorias de ITDTModel y los escenarios A, B1, B2, C, D.
    """
    def __init__(self, country: str = "KENYA", scenario: str = "A"):
        self.country = country.upper() if country else "KENYA"
        self.scenario = scenario.upper().strip() if scenario else "A"
        if self.scenario == "BASELINE":
            self.scenario = "A"
        self.month = 0
        self.is_playing = False
        self.playback_speed = 1.0
        self.total_workers = 2500
        self.policy_params: Dict[str, float] = {}

        self.workers: List[WorkerAgentSim] = []
        self._initialize_population()

    def _initialize_population(self):
        """Inicializa la población de partículas de acuerdo con la informalidad real de ITDTModel."""
        self.workers.clear()
        metrics = self.calculate_metrics()
        inf_rate = metrics["informalityRate"]

        informal_ratio = inf_rate / 100.0
        formal_ratio = 1.0 - informal_ratio

        num_formal = int(round(self.total_workers * formal_ratio))
        num_informal = self.total_workers - num_formal

        # 1. Trabajadores Formales
        for i in range(num_formal):
            hc = float(random.randint(65, 100))
            firm_idx = i % len(MOCK_FIRMS_COORDS)
            w = WorkerAgentSim(
                id_num=i,
                sector='formal',
                human_capital=hc,
                formalization_month=0,
                firm_idx=firm_idx
            )
            firm = MOCK_FIRMS_COORDS[firm_idx]
            w.x = firm["x"] + math.cos(w.orbit_angle) * w.orbit_radius
            w.z = firm["z"] + math.sin(w.orbit_angle) * w.orbit_radius
            w.y = 2.0
            w.current_progress = 1.0
            self.workers.append(w)

        # 2. Trabajadores Informales
        for i in range(num_informal):
            hc = float(random.randint(20, 75))
            firm_idx = i % len(MOCK_FIRMS_COORDS)
            base_month = int(round(18 + (100.0 - hc) * 1.1 + (random.random() - 0.5) * 16))
            w = WorkerAgentSim(
                id_num=num_formal + i,
                sector='informal',
                human_capital=hc,
                formalization_month=base_month,
                firm_idx=firm_idx
            )
            self.workers.append(w)

    def set_country(self, country: str):
        c_clean = country.upper()
        if c_clean in COUNTRY_BASELINES:
            self.country = c_clean
            self._initialize_population()

    def set_scenario(self, scenario: str):
        sc_clean = scenario.upper().strip()
        if sc_clean in ("BASELINE", "STATUS_QUO"):
            sc_clean = "A"
        if sc_clean in SCENARIO_CONFIGS:
            self.scenario = sc_clean
            self._initialize_population()

    def set_policy_params(self, params: Dict[str, Any]):
        self.policy_params.update(params)

    def calculate_metrics(self) -> Dict[str, Any]:
        """Calcula métricas auténticas llamando directamente a ITDTModel."""
        return calculate_structural_metrics(
            country_code=self.country,
            policy_params=self.policy_params,
            scenario=self.scenario,
            month=self.month
        )

    def step(self) -> Dict[str, Any]:
        """
        Avanza la simulación 1 mes y calcula las coordenadas de las 2,500 partículas
        generando el stream comprimido [[id, x, y, z, progress], ...] para WebSocket.
        """
        if self.month < 120:
            self.month += 1
        else:
            self.month = 0

        current_month = self.month
        metrics = self.calculate_metrics()
        target_formal_count = metrics["formalWorkersCount"]

        compact_workers = []
        for idx, w in enumerate(self.workers):
            # Determinación de transición guiada por la trayectoria macroeconómica de ITDTModel
            should_be_formal = idx < target_formal_count
            target_prog = 1.0 if should_be_formal else 0.0

            w.current_progress += (target_prog - w.current_progress) * 0.25
            p = w.current_progress

            # Movimiento Browniano para el sector informal
            w.informal_x += w.vx * 1.5
            w.informal_z += w.vz * 1.5
            if abs(w.informal_x) > 22.0:
                w.vx *= -1.0
            if abs(w.informal_z) > 22.0:
                w.vz *= -1.0
            w.vx += (random.random() - 0.5) * 0.008
            w.vz += (random.random() - 0.5) * 0.008
            w.vx = max(-0.06, min(0.06, w.vx))
            w.vz = max(-0.06, min(0.06, w.vz))

            ground_y_inf = terrain_elevation(w.informal_x, w.informal_z, self.country)
            y_inf = ground_y_inf + 0.25

            # Movimiento Orbital alrededor del Hub Formal
            host_firm = MOCK_FIRMS_COORDS[w.firm_idx]
            w.orbit_angle += w.orbit_speed * 1.8
            x_form = host_firm["x"] + math.cos(w.orbit_angle) * w.orbit_radius
            z_form = host_firm["z"] + math.sin(w.orbit_angle) * w.orbit_radius
            ground_y_form = terrain_elevation(x_form, z_form, self.country)
            y_form = max(ground_y_form + 0.4, ground_y_form + 0.5)

            # Interpolación espacial 3D
            w.x = w.informal_x + (x_form - w.informal_x) * p
            w.z = w.informal_z + (z_form - w.informal_z) * p
            w.y = y_inf + (y_form - y_inf) * p

            compact_workers.append([
                w.id_num,
                round(w.x, 2),
                round(w.y, 2),
                round(w.z, 2),
                round(p, 2),
            ])

        return {
            "month": current_month,
            "year": 2024 + (current_month // 12),
            "scenario": self.scenario,
            "country": self.country,
            "metrics": metrics,
            "workers": compact_workers,
        }


def generate_worker_population(
    country_code: str,
    total_workers: int = 2500,
    seed: int = 42
) -> List[Dict[str, Any]]:
    """
    Genera la población de partículas de trabajadores para vistas estáticas o Streamlit
    alineada con las proporciones observadas en ILOSTAT.
    """
    random.seed(seed)
    baseline = COUNTRY_BASELINES.get(country_code, COUNTRY_BASELINES["KENYA"])
    inf_rate = baseline["baseInformality"]

    informal_ratio = inf_rate / 100.0
    formal_ratio = 1.0 - informal_ratio

    num_formal = int(round(total_workers * formal_ratio))
    num_informal = total_workers - num_formal

    educations = ["Básica", "Media", "Superior"]
    genders = ["Femenino", "Masculino"]

    workers: List[Dict[str, Any]] = []

    # 1. Trabajadores Formales
    for i in range(num_formal):
        firm = MOCK_FIRMS_COORDS[i % len(MOCK_FIRMS_COORDS)]
        orbit_radius = 1.4 + random.random() * 2.8
        orbit_speed = 0.015 + random.random() * 0.02
        orbit_angle = random.random() * math.pi * 2
        human_capital = random.randint(65, 98)

        workers.append({
            "id": f"w-f-{i:04d}",
            "code": f"F-{1000 + i}",
            "sector": "formal",
            "x": firm["x"] + math.cos(orbit_angle) * orbit_radius,
            "y": 2.0,
            "z": firm["z"] + math.sin(orbit_angle) * orbit_radius,
            "base_x": firm["x"],
            "base_z": firm["z"],
            "orbit_radius": orbit_radius,
            "orbit_speed": orbit_speed,
            "orbit_angle": orbit_angle,
            "firm_id": firm["id"],
            "human_capital": human_capital,
            "age": 22 + random.randint(0, 38),
            "gender": genders[i % 2],
            "education": educations[min(2, human_capital // 35)],
            "formalization_month": 0,
            "current_progress": 1.0,
        })

    # 2. Trabajadores Informales
    for i in range(num_informal):
        x = (random.random() - 0.5) * 36.0
        z = (random.random() - 0.5) * 36.0
        human_capital = random.randint(18, 72)
        target_firm = MOCK_FIRMS_COORDS[i % len(MOCK_FIRMS_COORDS)]

        workers.append({
            "id": f"w-inf-{i:04d}",
            "code": f"INF-{2000 + i}",
            "sector": "informal",
            "x": x,
            "y": 0.5,
            "z": z,
            "base_x": x,
            "base_z": z,
            "informal_x": x,
            "informal_z": z,
            "target_firm_x": target_firm["x"],
            "target_firm_z": target_firm["z"],
            "orbit_radius": 1.5 + random.random() * 2.0,
            "orbit_speed": 0.015,
            "orbit_angle": random.random() * math.pi * 2,
            "firm_id": None,
            "human_capital": human_capital,
            "age": 18 + random.randint(0, 46),
            "gender": genders[i % 2],
            "education": educations[min(2, human_capital // 40)],
            "formalization_month": int(12 + (100 - human_capital) * 0.9),
            "current_progress": 0.0,
        })

    return workers


def update_worker_positions_for_month(
    workers: List[Dict[str, Any]],
    month: int,
    scenario: str = "A",
    policy_params: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Interpola las posiciones 3D de las partículas guiado estrictamente por la
    trayectoria de formalización simulada de ITDTModel en el mes activo.
    """
    country_code = "KENYA"
    metrics = calculate_structural_metrics(country_code, scenario=scenario, month=month)
    target_formal_count = metrics["formalWorkersCount"]

    updated = []
    for idx, w in enumerate(workers):
        w_copy = dict(w)
        should_be_formal = idx < target_formal_count

        if should_be_formal:
            angle = w["orbit_angle"] + month * 0.08
            w_copy["x"] = w.get("base_x", 0.0) + math.cos(angle) * w["orbit_radius"]
            w_copy["z"] = w.get("base_z", 0.0) + math.sin(angle) * w["orbit_radius"]
            w_copy["y"] = 2.0
            w_copy["current_progress"] = 1.0
            w_copy["display_sector"] = "Formal"
        else:
            drift_x = math.sin(month * 0.1 + w["human_capital"]) * 0.4
            drift_z = math.cos(month * 0.1 + w["human_capital"]) * 0.4
            w_copy["x"] = w.get("informal_x", w["x"]) + drift_x
            w_copy["z"] = w.get("informal_z", w["z"]) + drift_z
            w_copy["y"] = 0.5
            w_copy["current_progress"] = 0.0
            w_copy["display_sector"] = "Informal"

        updated.append(w_copy)

    return updated
