"""
itdt.simulation: Unified Simulation Engine for Labor Market Digital Twin.
Unifies agent kinematics, 3D particle state transitions, and macro-structural metric calculations.
"""

import math
import random
from typing import Dict, Any, List, Optional, Tuple

COUNTRY_BASELINES: Dict[str, Dict[str, Any]] = {
    "KENYA": {
        "name": "Kenia",
        "baseInformality": 82.7,
        "baseInformalityRate": 82.7,
        "baseGini": 0.408,
        "formalWageBaselineUSD": 28.5,
        "informalWageBaselineUSD": 8.2,
    },
    "NIGERIA": {
        "name": "Nigeria",
        "baseInformality": 92.9,
        "baseInformalityRate": 92.9,
        "baseGini": 0.351,
        "formalWageBaselineUSD": 22.0,
        "informalWageBaselineUSD": 6.5,
    },
    "INDIA": {
        "name": "India",
        "baseInformality": 88.6,
        "baseInformalityRate": 88.6,
        "baseGini": 0.357,
        "formalWageBaselineUSD": 25.0,
        "informalWageBaselineUSD": 7.2,
    },
    "BANGLADESH": {
        "name": "Bangladés",
        "baseInformality": 84.9,
        "baseInformalityRate": 84.9,
        "baseGini": 0.324,
        "formalWageBaselineUSD": 20.0,
        "informalWageBaselineUSD": 5.8,
    },
}

MOCK_FIRMS_COORDS: List[Dict[str, Any]] = [
    {"id": "firm-f-01", "name": "Apex Synth & Tech Corp", "x": -8.0, "z": -6.0, "height": 6.0, "type": "formal"},
    {"id": "firm-f-02", "name": "Metropolis Port Logistics Ltd", "x": 7.0, "z": -7.0, "height": 5.0, "type": "formal"},
    {"id": "firm-f-03", "name": "Vanguard Industrial Textiles", "x": 0.0, "z": -10.0, "height": 6.5, "type": "formal"},
    {"id": "firm-f-04", "name": "BioAgro Kenya Processing", "x": 10.0, "z": 6.0, "height": 4.5, "type": "formal"},
    {"id": "firm-f-05", "name": "Equator Solar Energy Solutions", "x": -11.0, "z": 7.0, "height": 5.0, "type": "formal"},
]


def terrain_elevation(x: float, z: float, country: str = "KENYA") -> float:
    """Calculates terrain altitude matching the 3D shader topography."""
    dist_from_center = math.hypot(x, z)
    if dist_from_center < 10.0:
        # Central plateaus (formal zone)
        plateau = max(0.0, 1.4 - (dist_from_center / 10.0) * 1.2)
        return plateau
    else:
        # Valleys and hills
        wave = math.sin(x * 0.18) * math.cos(z * 0.18) * 0.6
        return max(-0.5, wave)


def calculate_structural_metrics(
    country_code: str,
    policy_params: Optional[Dict[str, float]] = None,
    scenario: str = "BASELINE",
    month: int = 0
) -> Dict[str, Any]:
    """
    Computes macro structural metrics based on country baseline,
    active policy parameters, scenario shock, and month (0 to 120).
    """
    if policy_params is None:
        policy_params = {}

    baseline = COUNTRY_BASELINES.get(country_code, COUNTRY_BASELINES["KENYA"])
    base_informality = baseline.get("baseInformality", 82.7)
    base_gini = baseline.get("baseGini", 0.408)
    formal_wage_base = baseline.get("formalWageBaselineUSD", 28.5)
    informal_wage_base = baseline.get("informalWageBaselineUSD", 8.2)

    # Temporal realization curve (non-linear progress across 120 months)
    phase_progress = min(1.0, math.pow(max(0, month) / 120.0, 0.75))

    # Policy levers
    reg_reduction = policy_params.get("registrationCostReduction", 0.0)
    sme_subsidy = policy_params.get("smeSubsidyUSDMonth", 0.0)
    skills_cov = policy_params.get("skillsTrainingCoverage", 0.0)
    insp_cov = policy_params.get("smartInspectionCoverage", 0.0)
    tax_rate = policy_params.get("socialProtectionTax", 15.0)

    reg_impact = ((reg_reduction / 100.0) * 8.5) * phase_progress
    sub_impact = ((sme_subsidy / 150.0) * 11.0) * phase_progress
    train_impact = ((skills_cov / 100.0) * 6.5) * phase_progress
    insp_impact = ((insp_cov / 100.0) * 4.5) * phase_progress
    tax_burden = ((tax_rate - 15.0) * 0.30 * phase_progress) if tax_rate > 15.0 else 0.0

    # Scenario shifts
    scenario_shift = 0.0
    if scenario == "SCENARIO_A_REGISTRATION":
        scenario_shift = -14.0 * phase_progress
    elif scenario == "SCENARIO_B_WORKER_SUBSIDY":
        scenario_shift = -18.5 * phase_progress
    elif scenario == "SCENARIO_E_AUTOMATION_SHOCK":
        scenario_shift = (10.5 if month >= 20 else 0.0) * phase_progress

    net_informality = max(
        28.0,
        min(96.0, base_informality - reg_impact - sub_impact - train_impact - insp_impact + tax_burden + scenario_shift)
    )

    net_gini = max(
        0.26,
        min(0.55, base_gini - (100.0 - net_informality) * 0.0014)
    )

    total_pop = 2500
    formal_count = int(round(total_pop * (1.0 - net_informality / 100.0) * 0.92))
    informal_count = int(round(total_pop * (net_informality / 100.0)))
    unemployed_count = max(0, total_pop - formal_count - informal_count)

    avg_formal_wage = formal_wage_base + (skills_cov / 100.0) * 6.0 + phase_progress * 9.0
    avg_informal_wage = informal_wage_base + (sme_subsidy / 150.0) * 3.5 + phase_progress * 3.0

    # Fiscal estimates in Million USD
    fiscal_revenue = (formal_count * (tax_rate / 100.0) * avg_formal_wage * 30 * 12) / 1_000_000.0
    policy_cost = (sme_subsidy * 1200 + skills_cov * 800 + reg_reduction * 350) / 10000.0
    net_fiscal_balance = fiscal_revenue - policy_cost
    decent_work_idx = int(round(max(20, min(95, 55 + (100.0 - net_informality) * 0.4))))

    return {
        "informalityRate": round(net_informality, 1),
        "giniIndex": round(net_gini, 3),
        "formalWorkersCount": formal_count,
        "informalWorkersCount": informal_count,
        "unemployedCount": unemployed_count,
        "avgFormalWageUSD": round(avg_formal_wage, 1),
        "avgInformalWageUSD": round(avg_informal_wage, 1),
        "fiscalRevenueMillionUSD": round(fiscal_revenue, 1),
        "policyCostMillionUSD": round(policy_cost, 1),
        "netFiscalBalanceMillionUSD": round(net_fiscal_balance, 2),
        "decentWorkIndex": decent_work_idx,
        "phaseProgress": round(phase_progress, 3),
    }


class WorkerAgentSim:
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

        # Brownian valley coordinates
        self.informal_x = (random.random() - 0.5) * 36.0
        self.informal_z = 2.0 + (random.random() - 0.2) * 22.0
        self.vx = (random.random() - 0.5) * 0.04
        self.vz = (random.random() - 0.5) * 0.04

        # Orbital formal parameters
        self.orbit_radius = 1.4 + random.random() * 2.6
        self.orbit_speed = 0.012 + random.random() * 0.016
        self.orbit_angle = random.random() * math.pi * 2

        self.x = self.informal_x
        self.y = 0.5
        self.z = self.informal_z
        self.current_progress = 1.0 if sector == 'formal' else 0.0


class SimulationEngine:
    """
    Unified Simulation Engine managing stateful population and streaming 3D particle positions.
    """
    def __init__(self, country: str = "KENYA", scenario: str = "BASELINE"):
        self.country = country
        self.scenario = scenario
        self.month = 0
        self.is_playing = False
        self.playback_speed = 1.0
        self.total_workers = 2500

        self.policy_params: Dict[str, float] = {
            "registrationCostReduction": 0.0,
            "smeSubsidyUSDMonth": 0.0,
            "skillsTrainingCoverage": 0.0,
            "socialProtectionTax": 15.0,
            "smartInspectionCoverage": 0.0,
        }

        self.workers: List[WorkerAgentSim] = []
        self._initialize_population()

    def _initialize_population(self):
        self.workers.clear()
        baseline = COUNTRY_BASELINES.get(self.country, COUNTRY_BASELINES["KENYA"])
        inf_rate = baseline["baseInformality"]

        informal_ratio = inf_rate / 100.0
        formal_ratio = (1.0 - informal_ratio) * 0.92

        num_formal = int(round(self.total_workers * formal_ratio))
        num_informal = int(round(self.total_workers * informal_ratio))
        num_unemployed = self.total_workers - num_formal - num_informal

        # 1. Formal Workers
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
            self.workers.append(w)

        # 2. Informal Workers
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

        # 3. Unemployed Workers
        for i in range(num_unemployed):
            hc = float(random.randint(15, 55))
            w = WorkerAgentSim(
                id_num=num_formal + num_informal + i,
                sector='unemployed',
                human_capital=hc,
                formalization_month=999,
                firm_idx=0
            )
            self.workers.append(w)

    def set_country(self, country: str):
        if country in COUNTRY_BASELINES:
            self.country = country
            self._initialize_population()

    def set_policy_params(self, params: Dict[str, Any]):
        self.policy_params.update(params)

    def set_scenario(self, scenario: str):
        self.scenario = scenario
        if scenario == "SCENARIO_A_REGISTRATION":
            self.policy_params["registrationCostReduction"] = 80.0
            self.policy_params["smeSubsidyUSDMonth"] = 40.0
        elif scenario == "SCENARIO_B_WORKER_SUBSIDY":
            self.policy_params["smeSubsidyUSDMonth"] = 75.0
            self.policy_params["skillsTrainingCoverage"] = 60.0
        elif scenario == "BASELINE":
            self.policy_params = {
                "registrationCostReduction": 0.0,
                "smeSubsidyUSDMonth": 0.0,
                "skillsTrainingCoverage": 0.0,
                "socialProtectionTax": 15.0,
                "smartInspectionCoverage": 0.0,
            }

    def calculate_metrics(self) -> Dict[str, Any]:
        return calculate_structural_metrics(
            country_code=self.country,
            policy_params=self.policy_params,
            scenario=self.scenario,
            month=self.month
        )

    def step(self) -> Dict[str, Any]:
        """
        Advances the simulation by 1 month and computes updated particle positions
        producing the compact stream payload [[id, x, y, z, progress], ...].
        """
        if self.month < 120:
            self.month += 1
        else:
            self.month = 0

        current_month = self.month
        compact_workers = []

        for w in self.workers:
            # 1. Target formalization progress
            if w.sector == 'unemployed':
                target_prog = 0.0
            elif w.formalization_month == 0:
                target_prog = 1.0
            elif current_month >= w.formalization_month:
                target_prog = 1.0
            elif current_month >= w.formalization_month - 10:
                target_prog = (current_month - (w.formalization_month - 10)) / 10.0
            else:
                target_prog = 0.0

            w.current_progress += (target_prog - w.current_progress) * 0.25
            p = w.current_progress

            # 2. Brownian Motion (Informal)
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

            # 3. Orbital Motion (Formal)
            host_firm = MOCK_FIRMS_COORDS[w.firm_idx]
            w.orbit_angle += w.orbit_speed * 1.8
            x_form = host_firm["x"] + math.cos(w.orbit_angle) * w.orbit_radius
            z_form = host_firm["z"] + math.sin(w.orbit_angle) * w.orbit_radius
            ground_y_form = terrain_elevation(x_form, z_form, self.country)
            y_form = max(ground_y_form + 0.4, ground_y_form + 0.5)

            # 4. Interpolate coordinates
            if w.sector == 'unemployed':
                w.x = w.informal_x
                w.z = w.informal_z
                w.y = ground_y_inf + 0.15
            else:
                w.x = w.informal_x + (x_form - w.informal_x) * p
                w.z = w.informal_z + (z_form - w.informal_z) * p
                w.y = y_inf + (y_form - y_inf) * p

            # Minified payload: [id, x, y, z, progress]
            compact_workers.append([
                w.id_num,
                round(w.x, 2),
                round(w.y, 2),
                round(w.z, 2),
                round(p, 2),
            ])

        metrics = self.calculate_metrics()
        return {
            "month": current_month,
            "year": 2024 + (current_month // 12),
            "metrics": metrics,
            "workers": compact_workers,
        }


def generate_worker_population(
    country_code: str,
    total_workers: int = 2500,
    seed: int = 42
) -> List[Dict[str, Any]]:
    """
    Generates deterministic worker population with attributes and 3D positions.
    """
    random.seed(seed)
    baseline = COUNTRY_BASELINES.get(country_code, COUNTRY_BASELINES["KENYA"])
    inf_rate = baseline["baseInformality"]

    informal_ratio = inf_rate / 100.0
    formal_ratio = (1.0 - informal_ratio) * 0.92

    num_formal = int(round(total_workers * formal_ratio))
    num_informal = int(round(total_workers * informal_ratio))
    num_unemployed = max(0, total_workers - num_formal - num_informal)

    educations = ["Primaria", "Secundaria", "Técnica", "Universitaria"]
    genders = ["Femenino", "Masculino", "No binario"]
    subsectors_formal = ["Manufactura Avanzada", "Tecnología & Software", "Logística Portuaria", "Agroindustria Formal"]
    subsectors_informal = ["Comercio Ambulante", "Micro-taller Metalmecánico", "Servicios Personales", "Transporte Informal"]

    workers: List[Dict[str, Any]] = []

    # 1. Formal Workers
    for i in range(num_formal):
        firm = MOCK_FIRMS_COORDS[i % len(MOCK_FIRMS_COORDS)]
        orbit_radius = 1.4 + random.random() * 2.8
        orbit_speed = 0.015 + random.random() * 0.02
        orbit_angle = random.random() * math.pi * 2
        human_capital = random.randint(65, 98)
        income = round(24.0 + (human_capital / 100.0) * 32.0 + random.random() * 8.0, 1)

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
            "income_usd": income,
            "social_capital": random.randint(45, 90),
            "risk_tolerance": random.randint(20, 50),
            "flexibility_pref": random.randint(20, 50),
            "age": 22 + random.randint(0, 38),
            "gender": genders[i % 3],
            "education": educations[min(3, human_capital // 28)],
            "subsector": subsectors_formal[i % len(subsectors_formal)],
            "formalization_prob": 98,
            "formalization_month": 0,
            "current_progress": 1.0,
        })

    # 2. Informal Workers
    for i in range(num_informal):
        x = (random.random() - 0.5) * 36.0
        z = 3.0 + (random.random() - 0.2) * 22.0
        human_capital = random.randint(18, 72)
        income = round(4.5 + (human_capital / 100.0) * 14.0 + random.random() * 4.0, 1)
        base_month = int(round(18 + (100.0 - human_capital) * 1.1 + (random.random() - 0.5) * 16))
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
            "income_usd": income,
            "social_capital": random.randint(60, 95),
            "risk_tolerance": random.randint(45, 85),
            "flexibility_pref": random.randint(55, 95),
            "age": 18 + random.randint(0, 46),
            "gender": genders[i % 3],
            "education": educations[min(2, human_capital // 35)],
            "subsector": subsectors_informal[i % len(subsectors_informal)],
            "formalization_prob": int(15 + (human_capital / 100.0) * 55),
            "formalization_month": base_month,
            "current_progress": 0.0,
        })

    # 3. Unemployed Workers
    for i in range(num_unemployed):
        x = (random.random() - 0.5) * 40.0
        z = (random.random() - 0.5) * 40.0
        human_capital = random.randint(15, 50)

        workers.append({
            "id": f"w-u-{i:04d}",
            "code": f"U-{3000 + i}",
            "sector": "unemployed",
            "x": x,
            "y": 0.2,
            "z": z,
            "base_x": x,
            "base_z": z,
            "firm_id": None,
            "human_capital": human_capital,
            "income_usd": 1.2,
            "social_capital": random.randint(25, 60),
            "risk_tolerance": random.randint(30, 60),
            "flexibility_pref": 50,
            "age": 18 + random.randint(0, 42),
            "gender": genders[i % 3],
            "education": educations[0],
            "subsector": "Búsqueda Activa",
            "formalization_prob": 12,
            "formalization_month": 999,
            "current_progress": 0.0,
        })

    return workers


def update_worker_positions_for_month(
    workers: List[Dict[str, Any]],
    month: int,
    scenario: str = "BASELINE",
    policy_params: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Interpolates worker 3D positions and transitions based on the active month.
    """
    if policy_params is None:
        policy_params = {}

    updated = []
    reg_accel = policy_params.get("registrationCostReduction", 0.0) / 100.0 * 20.0
    sub_accel = policy_params.get("smeSubsidyUSDMonth", 0.0) / 150.0 * 25.0

    for w in workers:
        w_copy = dict(w)
        if w["sector"] == "formal":
            angle = w["orbit_angle"] + month * 0.08
            w_copy["x"] = w["base_x"] + math.cos(angle) * w["orbit_radius"]
            w_copy["z"] = w["base_z"] + math.sin(angle) * w["orbit_radius"]
            w_copy["y"] = 2.0
            w_copy["current_progress"] = 1.0
            w_copy["display_sector"] = "Formal"
        elif w["sector"] == "informal":
            target_month = max(4, w["formalization_month"] - reg_accel - sub_accel)
            if month >= target_month:
                progress = min(1.0, (month - target_month + 1) / 12.0)
                tx = w.get("target_firm_x", 0.0)
                tz = w.get("target_firm_z", 0.0)
                start_x = w.get("informal_x", w["x"])
                start_z = w.get("informal_z", w["z"])

                curr_x = start_x + (tx - start_x) * progress
                curr_z = start_z + (tz - start_z) * progress
                curr_y = 0.5 + progress * 1.5

                w_copy["x"] = curr_x
                w_copy["z"] = curr_z
                w_copy["y"] = curr_y
                w_copy["current_progress"] = progress
                w_copy["display_sector"] = "Formalizado" if progress >= 0.95 else "En Transición"
            else:
                drift_x = math.sin(month * 0.1 + w["human_capital"]) * 0.4
                drift_z = math.cos(month * 0.1 + w["human_capital"]) * 0.4
                w_copy["x"] = w.get("informal_x", w["x"]) + drift_x
                w_copy["z"] = w.get("informal_z", w["z"]) + drift_z
                w_copy["y"] = 0.5
                w_copy["current_progress"] = 0.0
                w_copy["display_sector"] = "Informal"
        else:
            w_copy["display_sector"] = "Desempleado"

        updated.append(w_copy)

    return updated
