import math
import random
from typing import Dict, Any, List, Optional, Tuple

COUNTRY_BASELINES = {
    "KENYA": {"baseInformality": 82.7, "baseGini": 0.408},
    "NIGERIA": {"baseInformality": 92.9, "baseGini": 0.351},
    "INDIA": {"baseInformality": 88.6, "baseGini": 0.357},
    "BANGLADESH": {"baseInformality": 84.9, "baseGini": 0.324},
}

MOCK_FIRMS_COORDS = [
    {"id": "firm-f-01", "x": 0.0, "z": 0.0, "height": 6.0, "type": "formal"},
    {"id": "firm-f-02", "x": -8.0, "z": 6.0, "height": 4.5, "type": "formal"},
    {"id": "firm-f-03", "x": 9.0, "z": -7.0, "height": 5.0, "type": "formal"},
    {"id": "firm-f-04", "x": -10.0, "z": -8.0, "height": 4.0, "type": "formal"},
    {"id": "firm-f-05", "x": 11.0, "z": 8.0, "height": 4.5, "type": "formal"},
]

def terrain_elevation(x: float, z: float, country: str = "KENYA") -> float:
    """Calculates terrain altitude matching the frontend shader topography."""
    dist_from_center = math.hypot(x, z)
    if dist_from_center < 10.0:
        # Central plateaus (formal zone)
        plateau = max(0.0, 1.4 - (dist_from_center / 10.0) * 1.2)
        return plateau
    else:
        # Valleys and hills
        wave = math.sin(x * 0.18) * math.cos(z * 0.18) * 0.6
        return max(-0.5, wave)

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
    def __init__(self, country: str = "KENYA", scenario: str = "BASELINE"):
        self.country = country
        self.scenario = scenario
        self.month = 0
        self.is_playing = False
        self.playback_speed = 1.0
        self.total_workers = 2500
        
        self.policy_params = {
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
            # Initial position on firm orbit
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
        baseline = COUNTRY_BASELINES.get(self.country, COUNTRY_BASELINES["KENYA"])
        base_informality = baseline["baseInformality"]
        base_gini = baseline["baseGini"]

        phase_progress = min(1.0, math.pow(self.month / 120.0, 0.75))

        reg_impact = ((self.policy_params["registrationCostReduction"] / 100.0) * 8.5) * phase_progress
        sub_impact = ((self.policy_params["smeSubsidyUSDMonth"] / 150.0) * 11.0) * phase_progress
        train_impact = ((self.policy_params["skillsTrainingCoverage"] / 100.0) * 6.5) * phase_progress
        insp_impact = ((self.policy_params["smartInspectionCoverage"] / 100.0) * 4.5) * phase_progress
        tax_burden = ((self.policy_params["socialProtectionTax"] - 25.0) * 0.35 * phase_progress) if self.policy_params["socialProtectionTax"] > 25 else 0.0

        scenario_shift = 0.0
        if self.scenario == "SCENARIO_A_REGISTRATION":
            scenario_shift = -14.0 * phase_progress
        elif self.scenario == "SCENARIO_B_WORKER_SUBSIDY":
            scenario_shift = -18.5 * phase_progress
        elif self.scenario == "SCENARIO_E_AUTOMATION_SHOCK":
            scenario_shift = (10.5 if self.month >= 20 else 0.0) * phase_progress

        net_informality = max(32.0, min(96.0, base_informality - reg_impact - sub_impact - train_impact - insp_impact + tax_burden + scenario_shift))
        net_gini = max(0.27, min(0.55, base_gini - (100.0 - net_informality) * 0.0014))

        formal_count = int(round(2500 * (1.0 - net_informality / 100.0) * 0.92))
        informal_count = int(round(2500 * (net_informality / 100.0)))
        unemployed_count = 2500 - formal_count - informal_count

        avg_formal_wage = round(28.5 + (self.policy_params["skillsTrainingCoverage"] / 100.0) * 6.0 + phase_progress * 9.0, 1)
        avg_informal_wage = round(8.2 + (self.policy_params["smeSubsidyUSDMonth"] / 150.0) * 3.5 + phase_progress * 3.0, 1)

        fiscal_revenue = round((formal_count * 0.18 * 30.0) / 10.0, 1)
        policy_cost = round((self.policy_params["smeSubsidyUSDMonth"] * 1200 + self.policy_params["skillsTrainingCoverage"] * 800) / 10000.0, 1)
        decent_work_idx = int(round(55 + (100.0 - net_informality) * 0.4))

        return {
            "informalityRate": round(net_informality, 1),
            "giniIndex": round(net_gini, 3),
            "formalWorkersCount": formal_count,
            "informalWorkersCount": informal_count,
            "unemployedCount": unemployed_count,
            "avgFormalWageUSD": avg_formal_wage,
            "avgInformalWageUSD": avg_informal_wage,
            "fiscalRevenueMillionUSD": fiscal_revenue,
            "policyCostMillionUSD": policy_cost,
            "decentWorkIndex": decent_work_idx,
        }

    def step(self) -> Dict[str, Any]:
        """
        Advances the simulation by 1 month and computes updated positions
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
            target_prog = 0.0
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

            # Smooth interpolation
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

            # 4. Interpolate final coordinates
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
