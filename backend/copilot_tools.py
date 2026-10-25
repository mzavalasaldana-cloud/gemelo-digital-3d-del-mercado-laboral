"""
Control de Herramientas de Solo Lectura para el Copiloto IA (LaborTwin V1).
Accede exclusivamente a datos numéricos verificados de simulación y tablas de outputs/
en tiempo de ejecución, sin valores fijos escritos a mano en prompts.
"""

import os
import re
import csv
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from .simulation_engine import SimulationEngine, COUNTRY_BASELINES

OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"


def parse_query_simulation_params(
    user_query: str,
    default_country: str = "KENYA",
    default_scenario: str = "A",
    default_month: int = 0
) -> Tuple[str, str, int]:
    """
    Detecta en la consulta del usuario el país, escenario y mes solicitados.
    Permite responder con los datos de ESA combinación específica,
    independientemente de la vista activa en la interfaz.
    """
    ql = user_query.lower()

    # 1. Detección de País
    country = default_country.upper()
    if any(k in ql for k in ["kenia", "kenya"]):
        country = "KENYA"
    elif "nigeria" in ql:
        country = "NIGERIA"
    elif "india" in ql:
        country = "INDIA"
    elif "senegal" in ql:
        country = "SENEGAL"
    elif "bangladesh" in ql:
        country = "BANGLADESH"

    # 2. Detección de Escenario
    scenario = default_scenario.upper()
    sc_match = re.search(r'\b(?:escenario|scenario)\s*([a-d][1-2]?)\b', ql)
    if sc_match:
        scenario = sc_match.group(1).upper()
    elif "b2" in ql:
        scenario = "B2"
    elif "b1" in ql:
        scenario = "B1"
    elif any(k in ql for k in ["statu quo", "status quo", "escenario a"]):
        scenario = "A"
    elif any(k in ql for k in ["cuidados", "red de cuidados", "escenario c"]):
        scenario = "C"
    elif any(k in ql for k in ["integrado", "paquete integral", "escenario d"]):
        scenario = "D"

    # 3. Detección de Mes
    month = default_month
    m_match = re.search(r'\b(?:mes|month|m)\s*(\d{1,3})\b', ql)
    if m_match:
        try:
            month = max(0, min(120, int(m_match.group(1))))
        except ValueError:
            pass
    else:
        m_alt = re.search(r'\b(\d{1,3})\s*(?:meses|months)\b', ql)
        if m_alt:
            try:
                month = max(0, min(120, int(m_alt.group(1))))
            except ValueError:
                pass

    return country, scenario, month


def load_table6_changes_runtime() -> str:
    """Lee outputs/table6_changes.csv en tiempo de ejecución."""
    p = OUTPUTS_DIR / "table6_changes.csv"
    if not p.exists():
        return "No disponible en outputs/table6_changes.csv"
    try:
        with open(p, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows:
            return "Tabla 6 vacía"
        header = rows[0]
        lines = [" | ".join(header), " | ".join(["---"] * len(header))]
        for r in rows[1:]:
            lines.append(" | ".join(r))
        return "\n".join(lines)
    except Exception as e:
        return f"Error leyendo outputs/table6_changes.csv: {e}"


def load_table5_levels_runtime() -> str:
    """Lee outputs/table5_levels.csv en tiempo de ejecución."""
    p = OUTPUTS_DIR / "table5_levels.csv"
    if not p.exists():
        return "No disponible en outputs/table5_levels.csv"
    try:
        with open(p, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows:
            return "Tabla 5 vacía"
        header = rows[0]
        lines = [" | ".join(header), " | ".join(["---"] * len(header))]
        for r in rows[1:]:
            lines.append(" | ".join(r))
        return "\n".join(lines)
    except Exception as e:
        return f"Error leyendo outputs/table5_levels.csv: {e}"


def get_runtime_trajectory_point(country: str, scenario: str, month: int) -> Optional[Dict[str, Any]]:
    """Lee de outputs/trayectorias_mensuales.json el punto exacto simulado."""
    p = OUTPUTS_DIR / "trayectorias_mensuales.json"
    if not p.exists():
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        c_clean = country.upper()
        sc_clean = scenario.upper()
        entries = data.get(c_clean, {}).get(sc_clean, [])
        return next((e for e in entries if e.get("month") == month), None)
    except Exception:
        return None


def load_ml_benchmarks_runtime() -> str:
    """Lee en tiempo de ejecución outputs/motor_ia/metricas_modelos_*.json."""
    motor_dir = OUTPUTS_DIR / "motor_ia"
    lines = []
    for c in ["india", "nigeria"]:
        p = motor_dir / f"metricas_modelos_{c}.json"
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                name = data.get("champion_name", "N/D")
                cv_auc = data.get("champion_metrics", {}).get("cv_metrics", {}).get("roc_auc_mean", "N/D")
                test_auc = data.get("champion_metrics", {}).get("test_metrics", {}).get("roc_auc", "N/D")
                brier = data.get("champion_metrics", {}).get("cv_metrics", {}).get("brier_score_mean", "N/D")
                n_obs = data.get("total_observations", "N/D")
                obs_str = f"{n_obs:,}" if isinstance(n_obs, int) else str(n_obs)
                lines.append(
                    f"- {c.title()} ({obs_str} observaciones reales): Modelo ganador {name} con AUC CV {cv_auc}% (AUC Test {test_auc}%, Brier Score CV {brier})"
                )
            except Exception as e:
                lines.append(f"- {c.title()}: Error cargando métricas ({e})")
    return "\n".join(lines) if lines else "Sin métricas de Motor IA disponibles en disco."


def get_simulation_metrics(
    country: str = "KENYA",
    scenario: str = "A",
    month: int = 0,
    policy_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Calcula y extrae métricas estructurales verificadas y deterministas
    del motor de simulación para un país, escenario, mes y parámetros dados.
    Conectado directamente a itdt.model.ITDTModel y outputs/.
    """
    country_clean = country.upper() if country else "KENYA"
    if country_clean not in COUNTRY_BASELINES:
        country_clean = "KENYA"

    sc_clean = scenario.upper().strip() if scenario else "A"
    if sc_clean == "BASELINE":
        sc_clean = "A"

    sim = SimulationEngine(country=country_clean, scenario=sc_clean)
    sim.month = max(0, min(120, month))
    if policy_params:
        sim.set_policy_params(policy_params)

    metrics = sim.calculate_metrics()
    baseline = COUNTRY_BASELINES.get(country_clean, COUNTRY_BASELINES["KENYA"])

    # Enriquecer con punto exacto de la trayectoria precalculada si existe
    traj_point = get_runtime_trajectory_point(country_clean, sc_clean, sim.month)
    if traj_point:
        metrics["informalityRate"] = traj_point.get("informality_total", metrics.get("informalityRate"))
        metrics["informalityFemale"] = traj_point.get("informality_female", metrics.get("informalityFemale"))
        metrics["informalityMale"] = traj_point.get("informality_male", metrics.get("informalityMale"))
        metrics["genderGap"] = traj_point.get("gender_gap", metrics.get("genderGap"))
        metrics["annualExitRate"] = traj_point.get("annual_exit_rate", metrics.get("annualExitRate"))
        metrics["fiscalRevenueModelUnits"] = traj_point.get("fiscal_revenue", metrics.get("fiscalRevenueModelUnits"))
        metrics["giniIndex"] = traj_point.get("gini_index", metrics.get("giniIndex"))

    return {
        "country": country_clean,
        "scenario": sc_clean,
        "month": sim.month,
        "year": 2024 + (sim.month // 12),
        "baseInformalityRate": baseline["baseInformality"],
        "baseGiniIndex": metrics.get("baseGiniIndex"),
        "informalityRate": metrics.get("informalityRate"),
        "informalityFemale": metrics.get("informalityFemale"),
        "informalityMale": metrics.get("informalityMale"),
        "genderGap": metrics.get("genderGap"),
        "giniIndex": metrics.get("giniIndex"),
        "formalWorkersCount": metrics.get("formalWorkersCount"),
        "informalWorkersCount": metrics.get("informalWorkersCount"),
        "unemployedCount": metrics.get("unemployedCount"),
        "avgFormalWageModel": metrics.get("avgFormalWageModel"),
        "avgInformalWageModel": metrics.get("avgInformalWageModel"),
        "fiscalRevenueModelUnits": metrics.get("fiscalRevenueModelUnits", metrics.get("fiscalRevenue")),
        "corporateTaxRevenue": metrics.get("corporateTaxRevenue"),
        "laborContributionsRevenue": metrics.get("laborContributionsRevenue"),
        "annualExitRate": metrics.get("annualExitRate"),
        "source": metrics.get("source"),
        "sourceCitation": metrics.get("sourceCitation"),
        "policy_params": sim.policy_params,
        "trajectoryPoint": traj_point,
    }

