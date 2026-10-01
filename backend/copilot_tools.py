"""
Control de Herramientas de Solo Lectura para el Copiloto IA (LaborTwin V1).
Accede exclusivamente a datos numéricos verificados de simulación sin permitir
acceso directo a SQLite ni manipulación de base de datos por parte del LLM.
"""

from typing import Dict, Any, Optional
from .simulation_engine import SimulationEngine, COUNTRY_BASELINES

def get_simulation_metrics(
    country: str = "KENYA",
    scenario: str = "BASELINE",
    month: int = 0,
    policy_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Calcula y extrae métricas estructurales verificadas y deterministas
    del motor de simulación para un país, escenario, mes y parámetros dados.
    """
    country_clean = country.upper() if country else "KENYA"
    if country_clean not in COUNTRY_BASELINES:
        country_clean = "KENYA"

    sim = SimulationEngine(country=country_clean, scenario=scenario or "BASELINE")
    sim.month = max(0, min(120, int(month)))
    if policy_params:
        sim.set_policy_params(policy_params)

    metrics = sim.calculate_metrics()
    baseline = COUNTRY_BASELINES.get(country_clean, COUNTRY_BASELINES["KENYA"])

    return {
        "country": country_clean,
        "scenario": scenario or "BASELINE",
        "month": sim.month,
        "year": 2024 + (sim.month // 12),
        "baseInformalityRate": baseline["baseInformality"],
        "baseGiniIndex": baseline["baseGini"],
        "informalityRate": metrics["informalityRate"],
        "giniIndex": metrics["giniIndex"],
        "formalWorkersCount": metrics["formalWorkersCount"],
        "informalWorkersCount": metrics["informalWorkersCount"],
        "unemployedCount": metrics["unemployedCount"],
        "avgFormalWageUSD": metrics["avgFormalWageUSD"],
        "avgInformalWageUSD": metrics["avgInformalWageUSD"],
        "fiscalRevenueMillionUSD": metrics["fiscalRevenueMillionUSD"],
        "policyCostMillionUSD": metrics["policyCostMillionUSD"],
        "decentWorkIndex": metrics["decentWorkIndex"],
        "policy_params": sim.policy_params,
    }
