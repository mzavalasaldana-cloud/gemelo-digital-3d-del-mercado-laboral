"""
Control de Herramientas de Solo Lectura para el Copiloto IA (LaborTwin V1).
Accede exclusivamente a datos numéricos verificados de simulación sin permitir
acceso directo a SQLite ni manipulación de base de datos por parte del LLM.
"""

from typing import Dict, Any, Optional
from .simulation_engine import SimulationEngine, COUNTRY_BASELINES

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
    sim.month = max(0, min(120, int(month)))
    if policy_params:
        sim.set_policy_params(policy_params)

    metrics = sim.calculate_metrics()
    baseline = COUNTRY_BASELINES.get(country_clean, COUNTRY_BASELINES["KENYA"])

    return {
        "country": country_clean,
        "scenario": sc_clean,
        "month": sim.month,
        "year": 2024 + (sim.month // 12),
        "baseInformalityRate": baseline["baseInformality"],
        "baseGiniIndex": metrics.get("baseGiniIndex", 0.35),
        "informalityRate": metrics["informalityRate"],
        "informalityFemale": metrics.get("informalityFemale", metrics["informalityRate"]),
        "informalityMale": metrics.get("informalityMale", metrics["informalityRate"]),
        "genderGap": metrics.get("genderGap", 0.0),
        "giniIndex": metrics["giniIndex"],
        "formalWorkersCount": metrics["formalWorkersCount"],
        "informalWorkersCount": metrics["informalWorkersCount"],
        "unemployedCount": metrics["unemployedCount"],
        "avgFormalWageModel": metrics.get("avgFormalWageModel"),
        "avgInformalWageModel": metrics.get("avgInformalWageModel"),
        "avgFormalWageUSD": metrics["avgFormalWageUSD"],
        "avgInformalWageUSD": metrics["avgInformalWageUSD"],
        "formalWageUSDNote": metrics.get("formalWageUSDNote", "Indicador ilustrativo, no forma parte del artículo"),
        "informalWageUSDNote": metrics.get("informalWageUSDNote", "Indicador ilustrativo, no forma parte del artículo"),
        "fiscalRevenueMillionUSD": metrics["fiscalRevenueMillionUSD"],
        "policyCostMillionUSD": metrics.get("policyCostMillionUSD", 0.0),
        "annualExitRate": metrics.get("annualExitRate", 0.0),
        "decentWorkIndex": metrics["decentWorkIndex"],
        "decentWorkIndexNote": metrics.get("decentWorkIndexNote", "Indicador ilustrativo, no forma parte del artículo"),
        "policy_params": sim.policy_params,
    }

