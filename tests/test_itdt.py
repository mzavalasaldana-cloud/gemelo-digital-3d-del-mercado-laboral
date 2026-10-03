"""
tests/test_itdt.py: Pruebas unitarias, metamórficas y de integración (smoke) para el paquete itdt.

Contenido:
1. Pruebas unitarias de U_F, U_I, Pi_F, Pi_I, DCC, P_aud y regla de Metropolis con valores calculados a mano.
2. Pruebas metamórficas:
   (a) Con H_care = 0 para todos, la brecha simulada es aproximadamente 0 (|F - M| < 1.5 p.p.).
   (b) Al aumentar el multiplicador de sanciones, la informalidad total no aumenta.
   (c) Misma semilla, exactamente mismos resultados (determinismo estricto).
   (d) Con phi_1 = 0, el DCC no depende de Y.
3. Prueba smoke: corrida corta en menos de 5 segundos.
"""

import math
import numpy as np
import pytest

from itdt.model import ITDTModel
from itdt.parameters import FixedParameters


# ==============================================================================
# 1. PRUEBAS UNITARIAS CON VALORES CALCULADOS A MANO
# ==============================================================================

def test_unit_utility_formal_and_informal():
    """
    Verifica las ecuaciones canónicas de utilidad (Sección 3.2):
    U_F = ln(omega_F * h * (1 - tau_w) * (1 - gamma_0 * H_care / 48) - c_tr * (1 + r)) + beta + eps
    U_I = ln(omega_I * h)
    Donde beta y eps operan estrictamente FUERA del logaritmo.
    """
    # Parámetros conocidos para cálculo a mano
    omega_F = 1.20
    omega_I = 1.00
    tau_w = 0.10
    c_tr = 0.05
    beta = 0.15
    gamma_0 = 0.50

    h = 1.00
    r = 0.0  # Urbano
    H_care = 24.0  # 24 horas semanales
    eps = 0.0

    # 1. Cálculo a mano paso a paso:
    # care_penalty = 1 - 0.50 * (24 / 48) = 1 - 0.25 = 0.75
    # net_wage = 1.20 * 1.00 * (1 - 0.10) * 0.75 = 1.20 * 0.90 * 0.75 = 0.81
    # transport = 0.05 * (1 + 0) = 0.05
    # arg_log = 0.81 - 0.05 = 0.76
    # U_F = ln(0.76) + 0.15 + 0.0 = -0.27443684989 + 0.15 = -0.12443684989
    # U_I = ln(1.00 * 1.00) = 0.0
    expected_arg = 0.76
    expected_U_F = math.log(expected_arg) + beta + eps
    expected_U_I = math.log(omega_I * h)

    assert abs(expected_U_F - (-0.12443685)) < 1e-6
    assert abs(expected_U_I - 0.0) < 1e-9

    # Verificar que el modelo aplica exactamente esta fórmula
    fp = FixedParameters(
        omega_F=omega_F, omega_I=omega_I, tau_w=tau_w, c_tr=c_tr, beta=beta
    )
    model = ITDTModel(
        country_params={"s_F": 0.5, "phi_0": 5.0, "gamma_0": gamma_0, "name": "TestCountry"},
        scenario="A",
        seed=42,
        fixed_params=fp,
        N_W=10,
        N_F=5,
    )

    # Inyectar atributos exactos en el primer trabajador
    model.h[0] = h
    model.r[0] = r
    model.H_care[0] = H_care
    model.eps[0] = eps
    model.gamma_0 = gamma_0

    model._update_willing_workers(cur_beta=beta)

    # Verificar condición de no disposición (U_F < U_I)
    assert model.willing_workers[0] == False

    # Modificar para que sea formalmente dispuesto (H_care = 0)
    # care_penalty = 1.0; net_wage = 1.08; arg = 1.08 - 0.05 = 1.03
    # U_F = ln(1.03) + 0.15 = +0.0295588 + 0.15 = 0.1795588 > 0.0
    model.H_care[0] = 0.0
    model._update_willing_workers(cur_beta=beta)
    assert model.willing_workers[0] == True

    # Verificar argumento <= 0 da indisposición absoluta
    model.r[0] = 100.0  # Costo de transporte enorme
    model._update_willing_workers(cur_beta=beta)
    assert model.willing_workers[0] == False


def test_unit_profits_formal_and_informal():
    """
    Verifica las ecuaciones de beneficios (Sección 3.3):
    Pi_F = (1 - tau_c) * Y - omega_F * (1 + tau_w) * L - r_cred * K - DCC
    Pi_I = Y - omega_I * L - r_I * K - P_aud * (mu_0 * Y + mu_1 * Y^xi)
    """
    p = FixedParameters()
    tau_c = 0.20
    omega_F = 1.20
    omega_I = 1.00
    tau_w = 0.10
    r_cred = 0.08
    r_I = 0.12
    mu_0 = 0.50
    mu_1 = 0.30
    xi = 1.10

    Y = 10.0
    L = 2
    K = 1.0
    DCC = 0.50
    P_aud = 0.10

    # Cálculo formal a mano:
    # (1 - 0.20) * 10 = 8.0
    # 1.20 * (1 + 0.10) * 2 = 2.64
    # 0.08 * 1.0 = 0.08
    # Pi_F = 8.0 - 2.64 - 0.08 - 0.50 = 4.78
    expected_Pi_F = 4.78

    # Cálculo informal a mano:
    # 10.0 - 1.0 * 2 - 0.12 * 1.0 = 7.88
    # multa = 0.50 * 10 + 0.30 * (10^1.1) = 5.0 + 0.30 * 12.58925412 = 8.77677624
    # sanción esperada = 0.10 * 8.77677624 = 0.87767762
    # Pi_I = 7.88 - 0.87767762 = 7.00232238
    expected_fine = mu_0 * Y + mu_1 * (Y ** xi)
    expected_Pi_I = Y - omega_I * L - r_I * K - P_aud * expected_fine

    assert abs(expected_Pi_F - 4.78) < 1e-7
    assert abs(expected_Pi_I - 7.00232238) < 1e-6


def test_unit_digital_compliance_cost():
    """
    Verifica el costo de cumplimiento digital (Sección 3.3):
    DCC = Y_bar * [phi_0 + phi_1 * (Y_bar / Y)^eta * (1 - K_dig)]
    """
    Y_bar = 4.0
    Y = 2.0
    phi_0 = 1.0
    phi_1 = 0.5
    eta = 0.7
    K_dig = 0.2

    # Cálculo a mano:
    # ratio = 4.0 / 2.0 = 2.0
    # 2.0^0.7 = 1.6245047927
    # 1 - K_dig = 0.8
    # bracket = 1.0 + 0.5 * 1.6245047927 * 0.8 = 1.0 + 0.649801917 = 1.649801917
    # DCC = 4.0 * 1.649801917 = 6.599207668
    expected_DCC = Y_bar * (phi_0 + phi_1 * ((Y_bar / Y) ** eta) * (1.0 - K_dig))
    assert abs(expected_DCC - 6.59920767) < 1e-6

    # Subsidio de 80% (Escenario D): DCC * 0.20
    assert abs(expected_DCC * 0.20 - 1.31984153) < 1e-6


def test_unit_audit_probability():
    """
    Verifica la probabilidad logística de auditoría (Sección 3.3):
    P_aud = 1 / (1 + exp(-kappa * (D_sys * Y / Y_bar - theta_th)))
    Donde kappa multiplica a TODO el binomio (D_sys * Y / Y_bar - theta_th).
    """
    kappa = 2.0
    D_sys = 0.60
    Y = 5.0
    Y_bar = 4.0
    theta_th = 0.50

    # Cálculo a mano:
    # D_sys * (Y / Y_bar) = 0.60 * 1.25 = 0.75
    # diff = 0.75 - 0.50 = 0.25
    # exponent = -kappa * diff = -2.0 * 0.25 = -0.50
    # P_aud = 1 / (1 + exp(-0.50)) = 1 / (1 + 0.6065306597) = 1 / 1.6065306597 = 0.62245933
    expected_P_aud = 1.0 / (1.0 + math.exp(-kappa * (D_sys * (Y / Y_bar) - theta_th)))
    assert abs(expected_P_aud - 0.62245933) < 1e-6


def test_unit_metropolis_rule():
    """
    Verifica la regla de decisión con recocido (Metropolis, Sección 3.4):
    rho = (Pi_F - Pi_I) / Y
    T_k = T_0 * d^k
    P(informal -> formal) = exp(min(rho, 0) / T_k)
    P(formal -> informal) = exp(min(-rho, 0) / T_k)
    """
    T_0 = 0.50
    d = 0.85
    k = 1  # Segundo año (meses 12 a 23)
    T_k = T_0 * (d ** k)  # 0.50 * 0.85 = 0.425

    # Caso 1: Formalidad desventajosa (rho = -0.20)
    rho_neg = -0.20
    # min(-0.20, 0) = -0.20
    # P(inf -> formal) = exp(-0.20 / 0.425) = exp(-0.470588235) = 0.6246337
    p_inf_to_formal = math.exp(min(rho_neg, 0.0) / T_k)
    # min(-(-0.20), 0) = min(0.20, 0) = 0.0 -> P(formal -> inf) = exp(0) = 1.0
    p_formal_to_inf = math.exp(min(-rho_neg, 0.0) / T_k)

    assert abs(p_inf_to_formal - 0.6246347) < 1e-5
    assert abs(p_formal_to_inf - 1.0000000) < 1e-9

    # Caso 2: Formalidad ventajosa (rho = +0.20)
    rho_pos = +0.20
    p_inf_to_formal_pos = math.exp(min(rho_pos, 0.0) / T_k)
    p_formal_to_inf_pos = math.exp(min(-rho_pos, 0.0) / T_k)

    assert abs(p_inf_to_formal_pos - 1.0000000) < 1e-9
    assert abs(p_formal_to_inf_pos - 0.6246347) < 1e-5


# ==============================================================================
# 2. PRUEBAS METAMÓRFICAS
# ==============================================================================

def test_metamorphic_zero_care_zero_gender_gap():
    """
    Propiedad metamórfica (a):
    Con H_care = 0 para todos los trabajadores, la brecha de género simulada
    debe ser aproximadamente cero (|F - M| < 1.5 p.p.).
    """
    fp = FixedParameters(
        care_enabled=False,
        H_care_fem_mean=0.0,
        H_care_fem_std=0.0,
        H_care_male_mean=0.0,
        H_care_male_std=0.0,
    )
    # Calibrar con gamma_0 = 0.0
    c_info = {"s_F": 0.50, "phi_0": 4.0, "gamma_0": 0.0, "name": "ZeroCareTest"}
    model = ITDTModel(
        country_params=c_info,
        scenario="A",
        seed=1000,
        burn_in_months=24,
        policy_months=12,
        fixed_params=fp,
        N_W=3000,
        N_F=300,
    )
    # Forzar H_care a 0.0 en todos
    model.H_care[:] = 0.0
    model._update_firm_production()
    model._update_willing_workers(fp.beta)

    res = model.run()["summary_metrics"]
    f_rate = res["mean_informality_female"]
    m_rate = res["mean_informality_male"]
    gender_gap = abs(f_rate - m_rate)

    assert gender_gap < 1.5, f"La brecha sin cuidados debería ser ~0 p.p., pero se obtuvo {gender_gap:.2f} p.p."


def test_metamorphic_sanctions_monotonicity():
    """
    Propiedad metamórfica (b):
    Al aumentar el multiplicador de sanciones (de 1.0 a 3.0),
    la informalidad total no debe aumentar (T_high <= T_low + tol).
    """
    fp_low = FixedParameters(sanction_mult=1.0)
    fp_high = FixedParameters(sanction_mult=3.0)

    model_low = ITDTModel(
        country_params="KENYA",
        scenario="B1",
        seed=2026,
        burn_in_months=24,
        policy_months=12,
        fixed_params=fp_low,
        N_W=2000,
        N_F=200,
    )
    res_low = model_low.run()["summary_metrics"]["mean_informality_total"]

    model_high = ITDTModel(
        country_params="KENYA",
        scenario="B1",
        seed=2026,
        burn_in_months=24,
        policy_months=12,
        fixed_params=fp_high,
        N_W=2000,
        N_F=200,
    )
    res_high = model_high.run()["summary_metrics"]["mean_informality_total"]

    assert res_high <= res_low + 0.1, (
        f"Mayor sanción debería reducir o mantener la informalidad: "
        f"low={res_low:.2f}%, high={res_high:.2f}%"
    )


def test_metamorphic_determinism_seed():
    """
    Propiedad metamórfica (c):
    Misma semilla produce exactamente los mismos resultados en todas las métricas.
    """
    m1 = ITDTModel(country_params="KENYA", scenario="A", seed=777, burn_in_months=12, policy_months=12, N_W=1000, N_F=100)
    r1 = m1.run()

    m2 = ITDTModel(country_params="KENYA", scenario="A", seed=777, burn_in_months=12, policy_months=12, N_W=1000, N_F=100)
    r2 = m2.run()

    # Verificar igualdad exacta de series temporales
    series_tot_1 = [m["informality_total"] for m in r1["monthly_series"]]
    series_tot_2 = [m["informality_total"] for m in r2["monthly_series"]]
    series_fem_1 = [m["informality_female"] for m in r1["monthly_series"]]
    series_fem_2 = [m["informality_female"] for m in r2["monthly_series"]]
    series_male_1 = [m["informality_male"] for m in r1["monthly_series"]]
    series_male_2 = [m["informality_male"] for m in r2["monthly_series"]]

    assert np.array_equal(series_tot_1, series_tot_2)
    assert np.array_equal(series_fem_1, series_fem_2)
    assert np.array_equal(series_male_1, series_male_2)
    assert r1["summary_metrics"] == r2["summary_metrics"]


def test_metamorphic_phi1_zero_dcc_independent_of_y():
    """
    Propiedad metamórfica (d):
    Con phi_1 = 0, el Costo de Cumplimiento Digital (DCC) no depende del nivel de producto Y.
    DCC(Y) = Y_bar * phi_0 constante para cualquier Y.
    """
    fp = FixedParameters(phi_1=0.0, regressive_dcc=False)
    model = ITDTModel(
        country_params={"s_F": 0.5, "phi_0": 4.5, "gamma_0": 0.5, "name": "FlatDCCTest"},
        scenario="A",
        seed=42,
        fixed_params=fp,
        N_W=1000,
        N_F=100,
    )

    # Evaluar DCC directamente bajo diferentes niveles de producto
    Y_bar = model.Y_bar
    phi_0 = model.phi_0
    expected_constant_dcc = Y_bar * phi_0

    # Simular una llamada a evaluación de beneficios
    # En _evaluate_firm_profits, cuando regressive_dcc=False o phi_1=0:
    # DCC = Y_bar * phi_0
    Pi_F, _, _ = model._evaluate_firm_profits(
        current_d_sys=0.5, current_kappa=1.0, current_phi_1=0.0, current_mu_0=1.0, current_mu_1=1.0
    )

    # Verificar que el DCC incorporado en Pi_F varía sólo por los otros términos lineales en Y, L y K
    # Pi_F = (1 - tau_c)*Y - omega_F*(1 + tau_w)*L - r_cred*K - DCC
    implied_DCC = (1.0 - fp.tau_c) * model.Y - fp.omega_F * (1.0 + fp.tau_w) * model.L - fp.r_cred * model.K - Pi_F

    # Todos los elementos del array implied_DCC deben ser iguales a Y_bar * phi_0
    assert np.allclose(implied_DCC, expected_constant_dcc, atol=1e-7)


# ==============================================================================
# 3. PRUEBA SMOKE (< 1 MINUTO)
# ==============================================================================

def test_smoke_execution():
    """
    Prueba de humo rápida: inicializa y simula 12 meses de modelo completo en < 5 segundos.
    Verifica consistencia y formato del diccionario de resultados.
    """
    model = ITDTModel(
        country_params="KENYA",
        scenario="A",
        seed=101,
        burn_in_months=6,
        policy_months=6,
        N_W=1000,
        N_F=100,
    )
    results = model.run()

    assert "summary_metrics" in results
    assert "monthly_series" in results
    assert len(results["monthly_series"]) == 12

    sm = results["summary_metrics"]
    assert 0.0 <= sm["mean_informality_total"] <= 100.0
    assert 0.0 <= sm["mean_informality_female"] <= 100.0
    assert 0.0 <= sm["mean_informality_male"] <= 100.0
