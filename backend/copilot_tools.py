"""
Control de Herramientas de Solo Lectura para el Copiloto IA (LaborTwin V1).
Accede exclusivamente a datos numéricos verificados de simulación sin permitir
acceso directo a bases de datos ni manipulación de PostgreSQL por parte del LLM.
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
    sim.month = max(0, min(120, month))
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
    }

