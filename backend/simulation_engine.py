"""
backend.simulation_engine: Adaptador del motor de simulación para FastAPI.
Delega la lógica visual a 'web_demo.simulation' conectada con 'itdt.model.ITDTModel' y 'outputs/'.
"""

from web_demo.simulation import (
    COUNTRY_BASELINES,
    get_model_firms,
    get_historical_ilostat_series,
    get_simulated_monthly_trajectory,
    terrain_elevation,
    WorkerAgentSim,
    SimulationEngine,
    calculate_structural_metrics,
    load_outputs_data,
    SCENARIO_CONFIGS,
)

__all__ = [
    "COUNTRY_BASELINES",
    "get_model_firms",
    "get_historical_ilostat_series",
    "get_simulated_monthly_trajectory",
    "terrain_elevation",
    "WorkerAgentSim",
    "SimulationEngine",
    "calculate_structural_metrics",
    "load_outputs_data",
    "SCENARIO_CONFIGS",
]

