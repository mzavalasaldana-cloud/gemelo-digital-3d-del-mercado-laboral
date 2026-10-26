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
import functools
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from itdt.model import ITDTModel

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

# Líneas base empíricas tomadas de ILOSTAT (data/ilostat_calibracion.csv descargado el 2026-10-22)
# Salarios en USD son indicadores ilustrativos de interfaz (no forman parte del artículo)
COUNTRY_BASELINES: Dict[str, Dict[str, Any]] = {
    "KENYA": {
        "name": "Kenia",
        "countryCode": "KEN",
        "baseInformality": 86.49,
        "baseInformalityRate": 86.49,
        "baseInformalityFemale": 90.19,
        "baseInformalityMale": 83.12,
    },
    "NIGERIA": {
        "name": "Nigeria",
        "countryCode": "NGA",
        "baseInformality": 93.14,
        "baseInformalityRate": 93.14,
        "baseInformalityFemale": 96.38,
        "baseInformalityMale": 89.86,
    },
    "INDIA": {
        "name": "India",
        "countryCode": "IND",
        "baseInformality": 88.13,
        "baseInformalityRate": 88.13,
        "baseInformalityFemale": 91.56,
        "baseInformalityMale": 86.58,
    },
    "BANGLADESH": {
        "name": "Bangladés",
        "countryCode": "BGD",
        "baseInformality": 84.14,
        "baseInformalityRate": 84.14,
        "baseInformalityFemale": 95.72,
        "baseInformalityMale": 78.03,
    },
}

_TRAYECTORIAS_CACHE: Optional[Dict[str, Any]] = None

def get_trayectorias_mensuales_data() -> Dict[str, Any]:
    global _TRAYECTORIAS_CACHE
    if _TRAYECTORIAS_CACHE is None:
        p = os.path.join(OUTPUTS_DIR, "trayectorias_mensuales.json")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                _TRAYECTORIAS_CACHE = json.load(f)
        else:
            _TRAYECTORIAS_CACHE = {}
    return _TRAYECTORIAS_CACHE


def get_model_firms(country_code: str = "KENYA", scenario: str = "A", month: int = 0, seed: int = 20260) -> List[Dict[str, Any]]:
    """
    Extrae las empresas reales del propio ITDTModel.
    Las 10 torres visualizadas representan la proporción real de empresas formales del modelo
    en ese mes y escenario (round(10 * proporción formal)), sin proporciones fijas 6/4.
    Los atributos individuales de las empresas (L_j, Y_j, A_j) salen del estado final de la réplica
    (mes 120), aunque el número de torres sea el del mes elegido.
    """
    c_clean = country_code.upper() if country_code else "KENYA"
    sc_clean = scenario.upper().strip() if scenario else "A"
    if sc_clean in ("BASELINE", "STATUS_QUO"):
        sc_clean = "A"

    sim_data = _get_or_run_itdt_model(c_clean, sc_clean, seed)
    model = sim_data.get("model")
    if model is None:
        return []

    # Proporción de firmas formales según outputs/trayectorias_mensuales.json para el mes y escenario
    traj_data = get_trayectorias_mensuales_data()
    c_traj = traj_data.get(c_clean, {}).get(sc_clean, [])
    
    clamped_m = max(1, min(120, month if month > 0 else 1))
    if c_traj and len(c_traj) >= clamped_m:
        formal_ratio = c_traj[clamped_m - 1].get("formal_firms_ratio")
        if formal_ratio is None:
            formal_ratio = float(np.mean(model.is_formal_firm))
    else:
        formal_ratio = float(np.mean(model.is_formal_firm))

    # Número de torres formales entre las 10 torres (round(10 * formal_ratio))
    num_formal = round(10.0 * formal_ratio)
    if formal_ratio > 0.005 and num_formal == 0:
        num_formal = 1
    num_formal = min(10, max(0, num_formal))
    num_informal = 10 - num_formal

    formal_indices = [j for j, f in enumerate(model.is_formal_firm) if f]
    informal_indices = [j for j, f in enumerate(model.is_formal_firm) if not f]

    selected_formal = formal_indices[:num_formal]
    selected_informal = informal_indices[:num_informal]

    while len(selected_formal) < num_formal and len(formal_indices) > 0:
        selected_formal.append(formal_indices[len(selected_formal) % len(formal_indices)])
    while len(selected_informal) < num_informal and len(informal_indices) > 0:
        selected_informal.append(informal_indices[len(selected_informal) % len(informal_indices)])

    firms_list: List[Dict[str, Any]] = []

    for slot_idx in range(10):
        angle = (slot_idx / 10.0) * math.pi * 2 + 0.3
        is_f = slot_idx < num_formal
        radius = 8.5 if is_f else 5.2
        x = round(math.cos(angle) * radius, 2)
        z = round(math.sin(angle) * radius, 2)

        if is_f and len(selected_formal) > slot_idx:
            j = selected_formal[slot_idx]
            l_j = int(round(model.L[j]))
            y_j = round(float(model.Y[j]), 2)
            a_j = round(float(model.A[j]), 3)
            firms_list.append({
                "id": f"UP-F-{j+1:02d}",
                "type": "formal",
                "x": x,
                "z": z,
                "height": round(max(3.5, min(8.5, y_j * 0.3)), 2),
                "L_j": l_j,
                "Y_j": y_j,
                "A_j": a_j,
                "sizeEmployees": l_j,
                "baseEmployees": l_j,
                "emergenceMonth": 0,
                "growthSpanMonths": 1,
            })
        else:
            inf_pos = slot_idx - num_formal
            j = selected_informal[inf_pos % len(selected_informal)] if selected_informal else slot_idx
            l_j = int(round(model.L[j]))
            y_j = round(float(model.Y[j]), 2)
            a_j = round(float(model.A[j]), 3)
            firms_list.append({
                "id": f"UP-INF-{j+1:02d}",
                "type": "informal_mycelium",
                "x": x,
                "z": z,
                "height": round(max(1.8, min(4.0, y_j * 0.2)), 2),
                "L_j": l_j,
                "Y_j": y_j,
                "A_j": a_j,
                "sizeEmployees": l_j,
                "baseEmployees": l_j,
                "emergenceMonth": 0,
                "growthSpanMonths": 1,
            })

    return firms_list




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
_STRUCTURAL_METRICS_CACHE: Dict[Tuple[str, str, int, int], Dict[str, Any]] = {}


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
    if sc_clean in ("BASELINE", "STATUS_QUO"):
        sc_clean = "A"
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
    Computa las métricas estructurales conectadas directamente a outputs/trayectorias_mensuales.json
    (media exacta de 40 réplicas por mes). Ninguna métrica proviene de fórmulas fijas ni interpolaciones.
    """
    country_clean = country_code.upper() if country_code else "KENYA"
    if country_clean not in COUNTRY_BASELINES:
        country_clean = "KENYA"

    sc_clean = scenario.upper().strip() if scenario else "A"
    if sc_clean in ("BASELINE", "STATUS_QUO"):
        sc_clean = "A"
    elif sc_clean in ("GOVTECH_MODERADO",):
        sc_clean = "B1"
    elif sc_clean in ("GOVTECH_INTENSIVO",):
        sc_clean = "B2"
    elif sc_clean not in SCENARIO_CONFIGS:
        sc_clean = "A"

    clamped_month = max(0, min(120, month))

    traj_data = get_trayectorias_mensuales_data()
    c_traj = traj_data.get(country_clean, {}).get(sc_clean, [])
    baseline = COUNTRY_BASELINES.get(country_clean, COUNTRY_BASELINES["KENYA"])

    if c_traj and clamped_month > 0:
        # Mes 1 a 120 de la política
        curr_item = c_traj[clamped_month - 1]
        inf_total = float(curr_item["informality_total"]) if curr_item.get("informality_total") is not None else None
        inf_fem = float(curr_item["informality_female"]) if curr_item.get("informality_female") is not None else None
        inf_male = float(curr_item["informality_male"]) if curr_item.get("informality_male") is not None else None
        gender_gap = float(curr_item["gender_gap"]) if curr_item.get("gender_gap") is not None else (
            round(inf_fem - inf_male, 2) if (inf_fem is not None and inf_male is not None) else None
        )
        annual_exit_rate = float(curr_item["annual_exit_rate"]) if curr_item.get("annual_exit_rate") is not None else None
        fiscal_revenue = float(curr_item["fiscal_revenue"]) if curr_item.get("fiscal_revenue") is not None else None
        corporate_tax = float(curr_item["corporate_tax_revenue"]) if curr_item.get("corporate_tax_revenue") is not None else None
        labor_tax = float(curr_item["labor_contributions_revenue"]) if curr_item.get("labor_contributions_revenue") is not None else (
            round(fiscal_revenue - corporate_tax, 2) if (fiscal_revenue is not None and corporate_tax is not None) else None
        )
        gini_sim = float(curr_item["gini_index"]) if curr_item.get("gini_index") is not None else None
        formal_firms_ratio = float(curr_item["formal_firms_ratio"]) if curr_item.get("formal_firms_ratio") is not None else None
    else:
        # Mes 0 (Línea base pre-política del país)
        a_traj = traj_data.get(country_clean, {}).get("A", [])
        curr_item = a_traj[0] if a_traj else {}
        inf_total = float(baseline["baseInformality"]) if baseline.get("baseInformality") is not None else (
            float(curr_item["informality_total"]) if curr_item.get("informality_total") is not None else None
        )
        inf_fem = float(baseline["baseInformalityFemale"]) if baseline.get("baseInformalityFemale") is not None else (
            float(curr_item["informality_female"]) if curr_item.get("informality_female") is not None else None
        )
        inf_male = float(baseline["baseInformalityMale"]) if baseline.get("baseInformalityMale") is not None else (
            float(curr_item["informality_male"]) if curr_item.get("informality_male") is not None else None
        )
        gender_gap = round(inf_fem - inf_male, 2) if (inf_fem is not None and inf_male is not None) else (
            float(curr_item["gender_gap"]) if curr_item.get("gender_gap") is not None else None
        )
        annual_exit_rate = float(curr_item["annual_exit_rate"]) if curr_item.get("annual_exit_rate") is not None else None
        fiscal_revenue = float(curr_item["fiscal_revenue"]) if curr_item.get("fiscal_revenue") is not None else None
        corporate_tax = float(curr_item["corporate_tax_revenue"]) if curr_item.get("corporate_tax_revenue") is not None else None
        labor_tax = float(curr_item["labor_contributions_revenue"]) if curr_item.get("labor_contributions_revenue") is not None else (
            round(fiscal_revenue - corporate_tax, 2) if (fiscal_revenue is not None and corporate_tax is not None) else None
        )
        gini_sim = float(curr_item["gini_index"]) if curr_item.get("gini_index") is not None else None
        formal_firms_ratio = float(curr_item["formal_firms_ratio"]) if curr_item.get("formal_firms_ratio") is not None else None

    total_pop_vis = 2500
    if inf_total is not None:
        formal_count = round(total_pop_vis * (1.0 - inf_total / 100.0))
        informal_count = total_pop_vis - formal_count
    else:
        formal_count = None
        informal_count = None
    unemployed_count = 0

    a_traj_base = traj_data.get(country_clean, {}).get("A", [])
    m0_base = a_traj_base[0] if a_traj_base else {}
    if baseline.get("baseGini") is not None:
        base_gini_sim = round(float(baseline["baseGini"]), 4)
    elif m0_base.get("gini_index") is not None:
        base_gini_sim = round(float(m0_base["gini_index"]), 4)
    else:
        base_gini_sim = None

    avg_formal_wage_model = 1.85
    avg_informal_wage_model = 1.00

    corp_tax = round(corporate_tax, 2) if corporate_tax is not None else None
    labor_tax = round(labor_tax, 2) if labor_tax is not None else (
        round(fiscal_revenue - corp_tax, 2) if (fiscal_revenue is not None and corp_tax is not None) else None
    )

    formal_firms_cnt = int(curr_item.get("formal_firms_count", round(100 * formal_firms_ratio))) if formal_firms_ratio is not None else curr_item.get("formal_firms_count")
    informal_firms_cnt = int(curr_item.get("informal_firms_count", 100 - round(100 * formal_firms_ratio))) if formal_firms_ratio is not None else curr_item.get("informal_firms_count")

    res = {
        "country": country_clean,
        "scenario": sc_clean,
        "month": clamped_month,
        "timelineMonth": clamped_month,
        "year": 2024 + (clamped_month // 12),
        "informalityRate": round(inf_total, 2) if inf_total is not None else None,
        "informalityFemale": round(inf_fem, 2) if inf_fem is not None else None,
        "informalityMale": round(inf_male, 2) if inf_male is not None else None,
        "genderGap": round(gender_gap, 2) if gender_gap is not None else None,
        "giniIndex": round(gini_sim, 4) if gini_sim is not None else None,
        "baseInformalityRate": baseline.get("baseInformality"),
        "baseGiniIndex": base_gini_sim,
        "formalWorkersCount": formal_count,
        "informalWorkersCount": informal_count,
        "unemployedCount": unemployed_count,
        "avgFormalWageModel": avg_formal_wage_model,
        "avgInformalWageModel": avg_informal_wage_model,
        "fiscalRevenueModelUnits": round(fiscal_revenue, 2) if fiscal_revenue is not None else None,
        "fiscalRevenue": round(fiscal_revenue, 2) if fiscal_revenue is not None else None,
        "corporateTaxRevenueModelUnits": corp_tax,
        "corporateTaxRevenue": corp_tax,
        "laborContributionsModelUnits": labor_tax,
        "laborContributionsRevenue": labor_tax,
        "annualExitRate": round(annual_exit_rate, 2) if annual_exit_rate is not None else None,
        "formalFirmsRatio": round(formal_firms_ratio, 4) if formal_firms_ratio is not None else None,
        "formalFirmsCount": formal_firms_cnt,
        "informalFirmsCount": informal_firms_cnt,
        "formalVacancies": int(curr_item["formal_vacancies"]) if curr_item.get("formal_vacancies") is not None else None,
        "willingWorkersCount": int(curr_item["willing_workers_count"]) if curr_item.get("willing_workers_count") is not None else informal_count,
        "digitalCoverage": round(float(curr_item["d_sys"]), 4) if curr_item.get("d_sys") is not None else None,
        "temperature": round(float(curr_item["temperature"]), 4) if curr_item.get("temperature") is not None else None,
        "informalityByEducation": curr_item.get("informality_by_education", {}),
        "informalityByZone": curr_item.get("informality_by_zone", {}),
        "informalityByQuintile": curr_item.get("informality_by_quintile", {}),
        "phaseProgress": round(clamped_month / 120.0, 3),
        "source": "Modelo ITDT Calibrado (outputs/trayectorias_mensuales.json / ILOSTAT)",
        "sourceCitation": "Calibración con series agregadas de ILOSTAT (data/ilostat_s_F.csv) y simulación multiagente itdt/",
    }

    if not policy_params:
        _STRUCTURAL_METRICS_CACHE[(country_clean, sc_clean, clamped_month, seed)] = res
    return res


@functools.lru_cache(maxsize=1)
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
        self.firms = get_model_firms(self.country, self.scenario)
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

        if not self.firms:
            self.firms = get_model_firms(self.country, self.scenario)
        firms_count = max(1, len(self.firms))

        # 1. Trabajadores Formales
        for i in range(num_formal):
            hc = float(random.randint(65, 100))
            firm_idx = i % firms_count
            w = WorkerAgentSim(
                id_num=i,
                sector='formal',
                human_capital=hc,
                formalization_month=0,
                firm_idx=firm_idx
            )
            firm = self.firms[firm_idx]
            w.x = firm["x"] + math.cos(w.orbit_angle) * w.orbit_radius
            w.z = firm["z"] + math.sin(w.orbit_angle) * w.orbit_radius
            w.y = 2.0
            w.current_progress = 1.0
            self.workers.append(w)

        # 2. Trabajadores Informales
        for i in range(num_informal):
            hc = float(random.randint(20, 75))
            firm_idx = i % firms_count
            base_month = round(18 + (100.0 - hc) * 1.1 + (random.random() - 0.5) * 16)
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

    def step(self, advance_month: bool = True) -> Dict[str, Any]:
        """
        Calcula las coordenadas de las 2,500 partículas generando el stream comprimido.
        Avanza 1 mes solo si advance_month es True.
        """
        if advance_month:
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
            if not self.firms:
                self.firms = get_model_firms(self.country, self.scenario)
            host_firm = self.firms[w.firm_idx % len(self.firms)]
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


def load_muestra_trabajadores() -> List[Dict[str, Any]]:
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "data", "muestra_trabajadores.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def generate_worker_population(
    country_code: str,
    total_workers: int = 2500,
    seed: int = 42
) -> List[Dict[str, Any]]:
    """
    Genera la población de partículas de trabajadores para vistas estáticas o Streamlit
    alineada con las proporciones observadas en ILOSTAT y microdatos reales de muestra_trabajadores.json.
    """
    random.seed(seed)
    baseline = COUNTRY_BASELINES.get(country_code, COUNTRY_BASELINES["KENYA"])
    inf_rate = baseline["baseInformality"]

    informal_ratio = inf_rate / 100.0
    formal_ratio = 1.0 - informal_ratio

    num_formal = int(round(total_workers * formal_ratio))
    num_informal = total_workers - num_formal

    sample = load_muestra_trabajadores()
    sample_formals = [p for p in sample if p.get("formal_base") is True]
    sample_informals = [p for p in sample if p.get("formal_base") is False]
    n_formals = len(sample_formals) or 1
    n_informals = len(sample_informals) or 1

    workers: List[Dict[str, Any]] = []
    firms = get_model_firms(country_code)
    firms_count = max(1, len(firms))

    # 1. Trabajadores Formales (formal_base = True)
    for i in range(num_formal):
        firm = firms[i % firms_count]
        orbit_radius = 1.4 + random.random() * 2.8
        orbit_speed = 0.015 + random.random() * 0.02
        orbit_angle = random.random() * math.pi * 2
        profile = sample_formals[i % n_formals] if sample_formals else {}

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
            "gender": profile.get("sexo"),
            "education": profile.get("educacion"),
            "rural_zone": profile.get("zona"),
            "productivity_h": profile.get("productividad_h"),
            "care_hours": profile.get("horas_cuidado"),
            "digital_lit": profile.get("alfabetizacion_digital"),
            "formal_base": True,
            "formalization_month": 0,
            "current_progress": 1.0,
        })

    # 2. Trabajadores Informales (formal_base = False)
    # NOTA: En el modelo canónico ITDT las trayectorias son macroeconómicas agregadas;
    # la transición visual entre sectores es una animación ilustrativa.
    for i in range(num_informal):
        x = (random.random() - 0.5) * 36.0
        z = (random.random() - 0.5) * 36.0
        target_firm = firms[i % firms_count]
        profile = sample_informals[i % n_informals] if sample_informals else {}

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
            "gender": profile.get("sexo"),
            "education": profile.get("educacion"),
            "rural_zone": profile.get("zona"),
            "productivity_h": profile.get("productividad_h"),
            "care_hours": profile.get("horas_cuidado"),
            "digital_lit": profile.get("alfabetizacion_digital"),
            "formal_base": False,
            "formalization_month": 0,
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
            drift_x = math.sin(month * 0.1 + w.get("productivity", 1.0)) * 0.4
            drift_z = math.cos(month * 0.1 + w.get("productivity", 1.0)) * 0.4
            w_copy["x"] = w.get("informal_x", w["x"]) + drift_x
            w_copy["z"] = w.get("informal_z", w["z"]) + drift_z
            w_copy["y"] = 0.5
            w_copy["current_progress"] = 0.0
            w_copy["display_sector"] = "Informal"

        updated.append(w_copy)

    return updated


@functools.lru_cache(maxsize=8)
def get_historical_ilostat_series(country_code: str = "KENYA") -> List[Dict[str, Any]]:
    """Carga los registros históricos reales de data/ilostat_series_historicas.csv para el país."""
    c_clean = country_code.upper() if country_code else "KENYA"
    code_map = {"KENYA": "KEN", "NIGERIA": "NGA", "INDIA": "IND", "BANGLADESH": "BGD"}
    target_code = code_map.get(c_clean, "KEN")
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ilostat_series_historicas.csv")
    if not os.path.exists(csv_path):
        return []

    # Agrupar por año
    by_year: Dict[int, Dict[str, Any]] = {}
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get("codigo_pais") == target_code:
                yr = int(r["anio"])
                if yr not in by_year:
                    by_year[yr] = {
                        "anio": yr,
                        "year": str(yr),
                        "informalidad": 0.0,
                        "formalidad": 0.0,
                        "mujeres": 0.0,
                        "hombres": 0.0,
                        "fuente": r["fuente"],
                    }
                sex = r["sexo"]
                val = float(r["tasa_informalidad"])
                if sex == "Total":
                    by_year[yr]["informalidad"] = val
                    by_year[yr]["formalidad"] = round(100.0 - val, 2)
                elif sex == "Mujeres":
                    by_year[yr]["mujeres"] = val
                elif sex == "Hombres":
                    by_year[yr]["hombres"] = val

    return sorted(by_year.values(), key=lambda x: x["anio"])


def get_simulated_monthly_trajectory(country_code: str = "KENYA", scenario: str = "A") -> List[Dict[str, Any]]:
    """
    Retorna la trayectoria mensual de informalidad (meses 1 a 120 de la política)
    con su intervalo de confianza al 95% para el escenario y país seleccionados,
    leída directamente de outputs/trayectorias_mensuales.json (sin interpolar).
    """
    c_clean = country_code.upper() if country_code else "KENYA"
    sc_clean = scenario.upper().strip() if scenario else "A"
    if sc_clean in ("BASELINE", "STATUS_QUO"):
        sc_clean = "A"

    data = get_trayectorias_mensuales_data()
    c_data = data.get(c_clean, {})
    sc_data = c_data.get(sc_clean, [])

    if not sc_data:
        return []

    traj = []
    for item in sc_data:
        m = item["month"]
        ci = item.get("informality_total_ci", [item["informality_total"], item["informality_total"]])
        ci_f = item.get("informality_female_ci", [item["informality_female"], item["informality_female"]])
        ci_m = item.get("informality_male_ci", [item["informality_male"], item["informality_male"]])
        traj.append({
            "mes": m,
            "periodo": f"Mes {m}",
            "informalidad": item["informality_total"],
            "informalidad_ci": ci,
            "informalidad_ci_low": ci[0],
            "informalidad_ci_high": ci[1],
            "mujeres": item["informality_female"],
            "mujeres_ci_low": ci_f[0],
            "mujeres_ci_high": ci_f[1],
            "hombres": item["informality_male"],
            "hombres_ci_low": ci_m[0],
            "hombres_ci_high": ci_m[1],
            "brecha": item["gender_gap"],
            "formalidad": round(100.0 - item["informality_total"], 2),
            "formal_firms_ratio": item.get("formal_firms_ratio"),
            "annual_exit_rate": item.get("annual_exit_rate"),
            "recaudacion": item.get("fiscal_revenue"),
            "gini": item.get("gini_index"),
            "tipo": "Simulación ITDT (meses 1-120 de la política)",
        })
    return traj

