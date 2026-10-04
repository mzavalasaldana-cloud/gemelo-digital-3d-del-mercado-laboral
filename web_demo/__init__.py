"""
web_demo: Adaptador de simulación 3D y demostrador web interactivo.
Conecta los visualizadores espaciales (Three.js / Streamlit) con el modelo
canónico econométrico itdt.model.ITDTModel y las tablas empíricas de outputs/.
"""

from .simulation import (
    COUNTRY_BASELINES,
    MOCK_FIRMS_COORDS,
    terrain_elevation,
    WorkerAgentSim,
    SimulationEngine,
    calculate_structural_metrics,
    generate_worker_population,
    update_worker_positions_for_month,
    load_outputs_data,
    SCENARIO_CONFIGS,
)

__all__ = [
    "COUNTRY_BASELINES",
    "MOCK_FIRMS_COORDS",
    "terrain_elevation",
    "WorkerAgentSim",
    "SimulationEngine",
    "calculate_structural_metrics",
    "generate_worker_population",
    "update_worker_positions_for_month",
    "load_outputs_data",
    "SCENARIO_CONFIGS",
]
