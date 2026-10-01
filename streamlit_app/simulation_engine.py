"""
Simulation Engine for Agent-Based Labor Market Modeling and Dynamic Metrics.
Calculates structural macro-metrics and generates 3D coordinates for 2,500 worker particles.
"""

import math
import random
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from streamlit_app.data.mock_data import COUNTRY_PROFILES, MOCK_FIRMS

def calculate_structural_metrics(
    country_code: str,
    policy_params: Dict[str, float],
    scenario: str,
    month: int = 0
) -> Dict[str, Any]:
    """
    Computes live macro structural metrics based on country baseline,
    active policy sliders, active scenario, and continuous month (0 to 120).
    """
    profile = COUNTRY_PROFILES.get(country_code, COUNTRY_PROFILES["KENYA"])
    base_informality = profile["baseInformalityRate"]
    base_gini = profile["baseGini"]

    # Temporal realization progress: non-linear curve from 0.0 (month 0) to 1.0 (month 120)
    phase_progress = min(1.0, math.pow(max(0, month) / 120.0, 0.75))

    # Policy lever impacts:
    reg_reduction = policy_params.get("registrationCostReduction", 0.0)
    sme_subsidy = policy_params.get("smeSubsidyUSDMonth", 0.0)
    skills_cov = policy_params.get("skillsTrainingCoverage", 0.0)
    insp_cov = policy_params.get("smartInspectionCoverage", 0.0)
    tax_rate = policy_params.get("socialProtectionTax", 12.0)

    reg_impact = ((reg_reduction / 100.0) * 8.5) * phase_progress
    sub_impact = ((sme_subsidy / 150.0) * 11.0) * phase_progress
    train_impact = ((skills_cov / 100.0) * 6.5) * phase_progress
    insp_impact = ((insp_cov / 100.0) * 4.5) * phase_progress
    tax_burden = ((tax_rate - 12.0) * 0.25 * phase_progress) if tax_rate > 12.0 else 0.0

    # Scenario specific shocks:
    scenario_shift = 0.0
    if scenario == "SCENARIO_A_REGISTRATION":
        scenario_shift = -14.0 * phase_progress
    elif scenario == "SCENARIO_B_WORKER_SUBSIDY":
        scenario_shift = -18.5 * phase_progress
    elif scenario == "SCENARIO_E_AUTOMATION_SHOCK":
        # Disruption accelerates after month 20
        scenario_shift = (+10.5 * phase_progress) if month >= 20 else 0.0

    net_informality = max(
        28.0,
        min(96.0, base_informality - reg_impact - sub_impact - train_impact - insp_impact + tax_burden + scenario_shift)
    )

    net_gini = max(
        0.26,
        min(0.55, base_gini - (100.0 - net_informality) * 0.0015)
    )

    total_pop = 2500
    formal_count = int(round(total_pop * (1.0 - net_informality / 100.0) * 0.92))
    informal_count = int(round(total_pop * (net_informality / 100.0)))
    unemployed_count = total_pop - formal_count - informal_count

    avg_formal_wage = profile["formalWageBaselineUSD"] + (skills_cov / 100.0) * 6.0 + phase_progress * 9.0
    avg_informal_wage = profile["informalWageBaselineUSD"] + (sme_subsidy / 150.0) * 3.5 + phase_progress * 2.5

    # Fiscal estimates in Million USD
    fiscal_revenue = (formal_count * (tax_rate / 100.0) * avg_formal_wage * 30 * 12) / 1_000_000.0
    policy_cost = (sme_subsidy * 1200 + skills_cov * 800 + reg_reduction * 350) / 1000.0
    net_fiscal_balance = fiscal_revenue - policy_cost

    decent_work_index = int(round(max(20, min(95, 55 + (100.0 - net_informality) * 0.42))))

    return {
        "informalityRate": round(net_informality, 1),
        "giniIndex": round(net_gini, 3),
        "formalWorkersCount": formal_count,
        "informalWorkersCount": informal_count,
        "unemployedCount": max(0, unemployed_count),
        "avgFormalWageUSD": round(avg_formal_wage, 2),
        "avgInformalWageUSD": round(avg_informal_wage, 2),
        "fiscalRevenueMillionUSD": round(fiscal_revenue, 2),
        "policyCostMillionUSD": round(policy_cost, 2),
        "netFiscalBalanceMillionUSD": round(net_fiscal_balance, 2),
        "decentWorkIndex": decent_work_index,
        "phaseProgress": round(phase_progress, 3),
    }


def generate_worker_population(
    country_code: str,
    total_workers: int = 2500,
    seed: int = 42
) -> List[Dict[str, Any]]:
    """
    Generates deterministic 2,500 worker agents population with 3D baseline
    coordinates, education, gender, human capital and formalization schedules.
    """
    random.seed(seed)
    np.random.seed(seed)
    profile = COUNTRY_PROFILES.get(country_code, COUNTRY_PROFILES["KENYA"])
    inf_rate = profile["baseInformalityRate"]

    informal_ratio = inf_rate / 100.0
    formal_ratio = (1.0 - informal_ratio) * 0.92

    num_formal = int(round(total_workers * formal_ratio))
    num_informal = int(round(total_workers * informal_ratio))
    num_unemployed = total_workers - num_formal - num_informal

    educations = ["Primaria", "Secundaria", "Técnica", "Universitaria"]
    genders = ["Femenino", "Masculino", "No binario"]
    subsectors_formal = ["Manufactura Avanzada", "Tecnología & Software", "Logística Portuaria", "Agroindustria Formal"]
    subsectors_informal = ["Comercio Ambulante", "Micro-taller Metalmecánico", "Servicios Personales", "Transporte Informal"]

    workers: List[Dict[str, Any]] = []

    # 1. Formal Workers (Orbiting formal crystal hubs at Y=2.0)
    for i in range(num_formal):
        firm = MOCK_FIRMS[i % 5]
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

    # 2. Informal Workers (Located in outer valleys at Y=0.5, moving toward hubs)
    for i in range(num_informal):
        x = (random.random() - 0.5) * 36.0
        z = 3.0 + (random.random() - 0.2) * 22.0
        human_capital = random.randint(18, 72)
        income = round(4.5 + (human_capital / 100.0) * 14.0 + random.random() * 4.0, 1)
        base_month = int(round(18 + (100.0 - human_capital) * 1.1 + (random.random() - 0.5) * 16))

        target_firm = MOCK_FIRMS[i % 5]

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

    # 3. Unemployed Workers (Periphery, Y=0.2)
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
    policy_params: Dict[str, float] = None
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
            # Continuous orbital motion around firm hub
            angle = w["orbit_angle"] + month * 0.08
            w_copy["x"] = w["base_x"] + math.cos(angle) * w["orbit_radius"]
            w_copy["z"] = w["base_z"] + math.sin(angle) * w["orbit_radius"]
            w_copy["y"] = 2.0
            w_copy["current_progress"] = 1.0
            w_copy["display_sector"] = "Formal"
        elif w["sector"] == "informal":
            target_month = max(4, w["formalization_month"] - reg_accel - sub_accel)
            if month >= target_month:
                # Transition completed or in orbit
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
                # Gentle Brownian drift in informal valley
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
