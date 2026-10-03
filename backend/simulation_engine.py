"""
backend.simulation_engine: Adaptador del motor de simulación para FastAPI.
Delega toda la lógica de simulación al paquete compartido 'itdt'.
"""

from itdt.simulation import (
    COUNTRY_BASELINES,
    MOCK_FIRMS_COORDS,
    terrain_elevation,
    WorkerAgentSim,
    SimulationEngine,
    calculate_structural_metrics,
)

__all__ = [
    "COUNTRY_BASELINES",
    "MOCK_FIRMS_COORDS",
    "terrain_elevation",
    "WorkerAgentSim",
    "SimulationEngine",
    "calculate_structural_metrics",
]
