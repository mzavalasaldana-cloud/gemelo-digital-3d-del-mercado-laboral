"""
itdt: Paquete unificado de simulación y modelo de agentes del mercado laboral (Digital Twin).
Implementa el modelo econométrico y ABM canónico (Secciones 3.1–3.4 y Tabla A1 del artículo).
"""

# 1. Modelo Canónico del Artículo
from .model import ITDTModel, run
from .parameters import FixedParameters, COUNTRY_DATABASE, resolve_country_params
from .metrics import compute_monthly_metrics, aggregate_evaluation_window

# 2. Adaptador de Visualización 3D y Compatibilidad
from .simulation import (
    COUNTRY_BASELINES,
    MOCK_FIRMS_COORDS,
    terrain_elevation,
    WorkerAgentSim,
    SimulationEngine,
    calculate_structural_metrics,
    generate_worker_population,
    update_worker_positions_for_month,
)

__all__ = [
    # API canónica del artículo
    "run",
    "ITDTModel",
    "FixedParameters",
    "COUNTRY_DATABASE",
    "resolve_country_params",
    "compute_monthly_metrics",
    "aggregate_evaluation_window",
    # Compatibilidad con UI existente
    "COUNTRY_BASELINES",
    "MOCK_FIRMS_COORDS",
    "terrain_elevation",
    "WorkerAgentSim",
    "SimulationEngine",
    "calculate_structural_metrics",
    "generate_worker_population",
    "update_worker_positions_for_month",
]
