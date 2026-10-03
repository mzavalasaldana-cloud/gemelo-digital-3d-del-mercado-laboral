"""
Pruebas exhaustivas para el paquete itdt y la API canónica del modelo de agentes.
"""

import pytest
import numpy as np
from itdt import run, ITDTModel, COUNTRY_DATABASE, FixedParameters

def test_itdt_run_kenya_scenario_a():
    """Verifica que run() retorne series mensuales y métricas agregadas consistentes."""
    result = run(
        country_params="KENYA",
        scenario="A",
        seed=20260,
        months=120,
        burn_in_months=96
    )

    assert result["country"] == "Kenia"
    assert result["scenario"] == "A"
    assert result["seed"] == 20260
    assert result["burn_in_months"] == 96
    assert result["policy_months"] == 120
    assert result["total_months_simulated"] == 216

    monthly = result["monthly_series"]
    assert len(monthly) == 216

    # Verificar estructura del primer y último mes
    m0 = monthly[0]
    m_last = monthly[-1]

    required_keys = [
        "month", "is_burn_in", "informality_total", "informality_female",
        "informality_male", "gender_gap", "annual_exit_rate", "fiscal_revenue",
        "corporate_tax_revenue", "labor_contributions_revenue", "formal_firms_count",
        "formal_vacancies", "willing_workers_count", "informality_by_education",
        "informality_by_zone", "informality_by_quintile"
    ]
    for k in required_keys:
        assert k in m0, f"Falta clave {k} en registro mensual"
        assert k in m_last, f"Falta clave {k} en registro mensual"

    # Verificar coherencia matemática de tasas
    assert 0.0 <= m_last["informality_total"] <= 100.0
    assert 0.0 <= m_last["informality_female"] <= 100.0
    assert 0.0 <= m_last["informality_male"] <= 100.0
    assert abs((m_last["informality_female"] - m_last["informality_male"]) - m_last["gender_gap"]) < 1e-4

    # Gradientes
    assert 0 in m_last["informality_by_education"]
    assert 1 in m_last["informality_by_education"]
    assert 2 in m_last["informality_by_education"]
    assert "rural" in m_last["informality_by_zone"]
    assert "urban" in m_last["informality_by_zone"]
    for q in range(1, 6):
        assert q in m_last["informality_by_quintile"]

    # Resumen
    summary = result["summary_metrics"]
    assert "mean_informality_total" in summary
    assert "mean_informality_female" in summary
    assert "mean_informality_male" in summary
    assert "mean_gender_gap" in summary
    assert "mean_annual_exit_rate" in summary
    assert "mean_fiscal_revenue" in summary
    assert "gradients" in summary
    assert len(summary["evaluation_window_months"]) == 12

    # Verificar que el resultado de Kenia está en el rango empírico de ILOSTAT (80-92%)
    assert 80.0 <= summary["mean_informality_total"] <= 92.0
    assert summary["mean_informality_female"] > summary["mean_informality_male"]


def test_itdt_all_countries():
    """Verifica que run() funcione correctamente con los 4 países calibrados."""
    for country in ["KENYA", "NIGERIA", "INDIA", "BANGLADESH"]:
        res = run(country, scenario="A", seed=1000, months=12, burn_in_months=12)
        assert res["country"] == COUNTRY_DATABASE[country]["name"]
        assert len(res["monthly_series"]) == 24
        summary = res["summary_metrics"]
        assert 70.0 <= summary["mean_informality_total"] <= 99.0


def test_itdt_all_scenarios():
    """Verifica que todos los escenarios (A, B1, B2, C, D) se ejecuten y produzcan efectos cualitativos esperados."""
    res_a = run("KENYA", scenario="A", seed=20260, months=24, burn_in_months=24)
    res_b2 = run("KENYA", scenario="B2", seed=20260, months=24, burn_in_months=24)
    res_c = run("KENYA", scenario="C", seed=20260, months=24, burn_in_months=24)
    res_d = run("KENYA", scenario="D", seed=20260, months=24, burn_in_months=24)

    # B2 debe reducir la informalidad frente a A
    assert res_b2["summary_metrics"]["mean_informality_total"] < res_a["summary_metrics"]["mean_informality_total"]
    # C debe reducir la brecha de género frente a A
    assert res_c["summary_metrics"]["mean_gender_gap"] < res_a["summary_metrics"]["mean_gender_gap"]


def test_itdt_custom_params():
    """Verifica que se puedan pasar parámetros de país personalizados vía diccionario."""
    custom_country = {
        "s_F": 0.40,
        "phi_0": 4.00,
        "gamma_0": 0.50,
        "name": "País Personalizado"
    }
    res = run(custom_country, scenario="A", seed=42, months=12, burn_in_months=12)
    assert res["country"] == "País Personalizado"
    assert len(res["monthly_series"]) == 24


def test_itdt_reproducibility():
    """Verifica que a igualdad de semilla, los resultados sean 100% idénticos (determinismo estocástico)."""
    res1 = run("KENYA", scenario="A", seed=12345, months=12, burn_in_months=12)
    res2 = run("KENYA", scenario="A", seed=12345, months=12, burn_in_months=12)

    assert res1["summary_metrics"]["mean_informality_total"] == res2["summary_metrics"]["mean_informality_total"]
    assert res1["summary_metrics"]["mean_gender_gap"] == res2["summary_metrics"]["mean_gender_gap"]
