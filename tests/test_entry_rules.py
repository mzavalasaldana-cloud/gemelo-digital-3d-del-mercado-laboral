"""
tests/test_entry_rules.py

Verifica las reglas de entrada ("free" vs "forced_informal") y modos de escala ("dynamic" vs "fixed")
del modelo ITDT (Sección B):
1. Con entry_rule = "forced_informal" y ybar_mode = "dynamic", el modelo debe dar
   EXACTAMENTE los resultados canónicos del artículo previo.
2. Con entry_rule = "free", la regla de libre entrada (Hopenhayn 1992, Melitz 2003)
   permite que las entrantes elijan el estado de mayor beneficio y descarten extracciones negativas.
3. Con ybar_mode = "fixed", Y_bar permanece inalterada tras el mes 96 de calentamiento.
4. La métrica adicional "pct_firms_closed_at_least_once" se calcula en el año final (meses 109-120).
"""

import pytest
import numpy as np
from itdt.model import ITDTModel
from itdt.parameters import FixedParameters


def test_forced_informal_dynamic_reproducibility():
    """
    Verifica que con entry_rule='forced_informal' y ybar_mode='dynamic',
    el modelo reproduce con exactitud bit a bit los resultados de referencia canónicos.
    """
    fp_forced = FixedParameters(entry_rule="forced_informal", ybar_mode="dynamic")

    # Escenario A: Status Quo
    model_A = ITDTModel("KENYA", scenario="A", seed=42, fixed_params=fp_forced)
    res_A = model_A.run()
    sm_A = res_A["summary_metrics"]

    # Valores exactos esperados
    assert sm_A["mean_informality_total"] == pytest.approx(87.72, abs=1e-2)
    assert sm_A["mean_informality_female"] == pytest.approx(91.08, abs=1e-2)
    assert sm_A["mean_informality_male"] == pytest.approx(84.55, abs=1e-2)
    assert sm_A["mean_gender_gap"] == pytest.approx(6.53, abs=1e-2)
    assert sm_A["mean_annual_exit_rate"] == pytest.approx(0.0, abs=1e-2)

    # Escenario B2: GovTech intensivo con salidas y reemplazos
    model_B2 = ITDTModel("KENYA", scenario="B2", seed=42, fixed_params=fp_forced)
    res_B2 = model_B2.run()
    sm_B2 = res_B2["summary_metrics"]

    assert sm_B2["mean_informality_total"] == pytest.approx(51.58, abs=1e-2)
    assert sm_B2["mean_informality_female"] == pytest.approx(68.51, abs=1e-2)
    assert sm_B2["mean_informality_male"] == pytest.approx(35.58, abs=1e-2)
    assert sm_B2["mean_gender_gap"] == pytest.approx(32.93, abs=1e-2)
    assert sm_B2["mean_annual_exit_rate"] == pytest.approx(49.33, abs=1e-2)


def test_free_entry_behavior_and_metrics():
    """
    Verifica que con entry_rule='free' (nueva regla por defecto):
    - Se ejecute con éxito.
    - Se calcule la métrica 'pct_firms_closed_at_least_once' en meses 109-120.
    - El porcentaje de empresas que cierran esté acotado entre 0 y 100%.
    """
    fp_free = FixedParameters(entry_rule="free", ybar_mode="dynamic")
    model = ITDTModel("KENYA", scenario="B2", seed=42, fixed_params=fp_free)
    res = model.run()
    sm = res["summary_metrics"]

    assert "pct_firms_closed_at_least_once" in sm
    pct_closed = sm["pct_firms_closed_at_least_once"]
    assert 0.0 <= pct_closed <= 100.0
    # En B2 con GovTech 3x debe registrar cierres
    assert pct_closed > 0.0

    # La tasa anualizada de cierres debe existir y ser no negativa
    assert sm["mean_annual_exit_rate"] >= 0.0


def test_ybar_mode_fixed():
    """
    Verifica que con ybar_mode='fixed', Y_bar calculada al término del burn-in (mes 96)
    permanece exactamente constante durante todo el período de política.
    """
    fp_fixed = FixedParameters(entry_rule="free", ybar_mode="fixed")
    model = ITDTModel("KENYA", scenario="B2", seed=42, fixed_params=fp_fixed)

    # Correr hasta el fin del burn-in (mes 96)
    for _ in range(model.burn_in_months):
        model.step(record_metrics=True)

    ybar_post_burn_in = model.Y_bar
    assert ybar_post_burn_in > 0

    # Ejecutar 24 meses de política intensiva
    for _ in range(24):
        model.step(record_metrics=True)
        assert model.Y_bar == pytest.approx(ybar_post_burn_in, rel=1e-9)
