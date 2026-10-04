"""
streamlit_app.simulation_engine: Adaptador del motor de simulación para Streamlit.
Delega la lógica visual a 'web_demo.simulation' conectada con 'itdt.model.ITDTModel' y 'outputs/'.
"""

from web_demo.simulation import (
    calculate_structural_metrics,
    generate_worker_population,
    update_worker_positions_for_month,
    COUNTRY_BASELINES,
    MOCK_FIRMS_COORDS,
    terrain_elevation,
    SimulationEngine,
    load_outputs_data,
    SCENARIO_CONFIGS,
)

__all__ = [
    "calculate_structural_metrics",
    "generate_worker_population",
    "update_worker_positions_for_month",
    "COUNTRY_BASELINES",
    "MOCK_FIRMS_COORDS",
    "terrain_elevation",
    "SimulationEngine",
    "load_outputs_data",
    "SCENARIO_CONFIGS",
]

