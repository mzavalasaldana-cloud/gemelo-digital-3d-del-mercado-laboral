"""
streamlit_app.simulation_engine: Adaptador del motor de simulación para Streamlit.
Delega toda la lógica de simulación al paquete compartido 'itdt'.
"""

from itdt.simulation import (
    calculate_structural_metrics,
    generate_worker_population,
    update_worker_positions_for_month,
    COUNTRY_BASELINES,
    MOCK_FIRMS_COORDS,
    terrain_elevation,
    SimulationEngine,
)

__all__ = [
    "calculate_structural_metrics",
    "generate_worker_population",
    "update_worker_positions_for_month",
    "COUNTRY_BASELINES",
    "MOCK_FIRMS_COORDS",
    "terrain_elevation",
    "SimulationEngine",
]
