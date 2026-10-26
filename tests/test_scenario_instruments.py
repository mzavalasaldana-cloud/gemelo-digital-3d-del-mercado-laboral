"""
Test de consistencia entre los instrumentos de escenarios reportados en report_generator.py
y la lógica exacta de política de itdt.model.ITDTModel y itdt.parameters.FixedParameters.
"""

import pytest
import numpy as np
from itdt.parameters import FixedParameters
from itdt.model import ITDTModel
from streamlit_app.utils.report_generator import build_scenario_instruments, SCENARIO_INSTRUMENTS


@pytest.mark.parametrize("scenario", ["A", "B1", "B2", "C", "D"])
def test_scenario_instruments_match_model(scenario: str):
    """
    Verifica que los parámetros del reporte coincidan estrictamente con los evaluados
    por ITDTModel.step durante el período de política (t >= burn_in_months).
    """
    p = FixedParameters()
    info = build_scenario_instruments(scenario)
    params = info["params"]

    # Instanciar ITDTModel con 1 mes de burn-in y ejecutar step para inspeccionar variables activas
    model = ITDTModel("KENYA", scenario=scenario, seed=123, burn_in_months=1, policy_months=12)
    # Ejecutar mes 0 (burn-in)
    model.step(record_metrics=False)
    # Ejecutar mes 1 (primer mes de política activa)
    model.step(record_metrics=False)

    # 1. Sensibilidad de auditoría (kappa)
    expected_kappa = p.kappa * (2.5 if scenario in ("B1", "B2", "D") else 1.0)
    assert abs(params["kappa"] - expected_kappa) < 1e-6

    # 2. Crecimiento de cobertura digital (D_sys_growth)
    expected_d_growth = p.D_sys_growth * (3.0 if scenario in ("B1", "B2", "D") else 1.0)
    assert abs(params["d_growth"] - expected_d_growth) < 1e-6

    # 3. Componente regresivo DCC (phi_1)
    expected_phi_1 = p.phi_1 * (1.5 if scenario in ("B1", "B2", "D") else 1.0)
    assert abs(params["phi_1"] - expected_phi_1) < 1e-6

    # 4. Sanciones por informalidad (mu_0, mu_1)
    expected_mu_mult = 3.0 if scenario in ("B2", "D") else 1.0
    assert abs(params["mu_0"] - p.mu_0 * expected_mu_mult) < 1e-6
    assert abs(params["mu_1"] - p.mu_1 * expected_mu_mult) < 1e-6

    # 5. Cuidado no remunerado de las mujeres (H_care)
    expected_care_mult = 0.40 if scenario in ("C", "D") else 1.0
    assert abs(params["care_mult"] - expected_care_mult) < 1e-6
    # Comprobar directamente en el array del modelo ITDT
    fem_care_ratio = model.H_care[model.fem_mask] / model.H_care_base[model.fem_mask]
    assert np.allclose(fem_care_ratio, expected_care_mult, atol=1e-5)

    # 6. Subsidio al DCC (Escenario D)
    expected_dcc_sub = (scenario == "D")
    assert params["dcc_subsidy"] == expected_dcc_sub

    # 7. Valor de protección social (beta)
    expected_beta = p.beta * (1.5 if scenario == "D" else 1.0)
    assert abs(params["beta"] - expected_beta) < 1e-6


def test_scenario_instruments_dictionary_populated():
    """Comprueba que SCENARIO_INSTRUMENTS contenga todos los escenarios canónicos."""
    for sc in ("A", "B1", "B2", "C", "D"):
        assert sc in SCENARIO_INSTRUMENTS
        assert len(SCENARIO_INSTRUMENTS[sc]["instruments"]) >= 7
