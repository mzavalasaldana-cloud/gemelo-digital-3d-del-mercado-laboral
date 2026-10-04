"""
itdt.parameters: Parámetros fijos, datos de países (Tabla A1 y Tabla 2) y configuraciones de escenarios.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import os
import csv

@dataclass
class FixedParameters:
    """Parámetros fijos comunes a los cuatro países tomados de la Tabla A1 del artículo."""
    # Submodelo de empresas y producción
    alpha: float = 0.62          # Participación salarial típica (retornos constantes)
    tau_w: float = 0.10          # Contribución a seguridad social del trabajador
    tau_c: float = 0.20          # Impuesto a las sociedades (renta corporativa)
    omega_F: float = 1.30        # Salario formal por unidad de productividad (prima formal +30%)
    omega_I: float = 1.00        # Salario informal por unidad de productividad
    r_cred: float = 0.08         # Tasa de interés de crédito formal
    r_I: float = 0.16            # Tasa de interés de crédito informal (doble del formal)

    # Producción CES alternativa (Sección 3.9 / Robustez)
    # sigma = 1.0 equivale a Cobb-Douglas con exponente alpha
    ces_sigma: float = 1.0       # Elasticidad de sustitución (1.0 = Cobb-Douglas, 0.5, 1.5)

    # Choque exógeno de demanda (Sección 3.9)
    demand_shock_month: Optional[int] = None # Mes en el que aplica el choque (e.g. 60)
    demand_shock_pct: float = -0.05          # Magnitud del choque sobre A_j (-5%)

    # Costo digital de cumplimiento (DCC)
    phi_1: float = 0.30          # Componente regresivo base del DCC
    eta: float = 0.42            # Elasticidad regresiva del DCC respecto al tamaño relativo
    regressive_dcc: bool = True  # Bandera de ablación para componente regresivo

    # Probabilidad de auditoría y sanciones
    mu_0: float = 0.25           # Sanción base proporcional al producto
    mu_1: float = 0.02           # Parámetro de sanción no lineal
    xi: float = 1.35             # Exponente de no linealidad en sanciones
    kappa: float = 4.12          # Sensibilidad logística de detección
    theta_th: float = 1.00       # Umbral relativo de trazabilidad
    sanction_mult: float = 1.0   # Multiplicador para barrido de sanciones (1.0 a 4.0)

    # Entorno digital y fiscalización
    D_sys0: float = 0.30         # Cobertura digital inicial
    D_sys_growth: float = 0.0015 # Crecimiento mensual de la cobertura digital (+0.15 p.p./mes)

    # Submodelo de trabajadores
    c_tr: float = 0.08           # Costo de transporte base urbano
    c_tr_rural_mult: float = 2.0 # Multiplicador de transporte en zona rural (doble en rural)
    beta: float = 0.25           # Valor de la protección social en unidades logarítmicas
    eps_std: float = 0.30        # Desviación de preferencia idiosincrática por formalidad

    # Cuidado (horas semanales de Addati et al. 2018)
    care_enabled: bool = True    # Bandera de ablación de cuidado
    H_care_fem_mean: float = 30.9
    H_care_fem_std: float = 6.0
    H_care_male_mean: float = 9.7
    H_care_male_std: float = 4.0

    # Dinámica y recocido simulado
    perfect_rationality: bool = False # Bandera para racionalidad perfecta (E2 / E4)
    T_0: float = 0.50            # Temperatura inicial de Metropolis
    d: float = 0.85              # Tasa anual de enfriamiento (T_k = T_0 * d^k)
    review_prob: float = 1.0 / 3.0  # Probabilidad mensual de revisión de estado por empresa
    exit_prob: float = 0.10      # Probabilidad mensual de salida si beneficio negativo

    # Escala y horizonte
    N_W: int = 6000              # Población de trabajadores
    N_F: int = 600               # Población de empresas
    burn_in_months: int = 96     # Período de calentamiento (meses)
    policy_months: int = 120     # Período de política (meses)


def load_ilostat_s_F_data() -> Dict[str, float]:
    """Carga la proporción s_F directamente desde data/ilostat_s_F.csv."""
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ilostat_s_F.csv")
    s_F_dict = {}
    if os.path.exists(csv_path):
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                c_key = row["country"].strip().upper()
                s_F_dict[c_key] = float(row["s_F"])
                # También mapear código ISO
                s_F_dict[row["country_code"].strip().upper()] = float(row["s_F"])
    return s_F_dict


import json

_s_F_data = load_ilostat_s_F_data()

# Base empírica por país observada en ILOSTAT
# NOTA: phi_0 y gamma_0 NO están escritos a mano; se leen dinámicamente de outputs/calibration_estimates.json
COUNTRY_DATABASE: Dict[str, Dict[str, Any]] = {
    "KENYA": {
        "name": "Kenia",
        "country_code": "KEN",
        "year": 2019,
        "s_F": _s_F_data.get("KENYA", 0.476259), # Proporción oficial ILOSTAT
        "F_obs": 90.19,                         # Tasa femenina observada ILOSTAT (%)
        "M_obs": 83.13,                         # Tasa masculina observada ILOSTAT (%)
        "T_obs": 86.49,                         # Tasa total observada ILOSTAT (%)
    },
    "NIGERIA": {
        "name": "Nigeria",
        "country_code": "NGA",
        "year": 2024,
        "s_F": _s_F_data.get("NIGERIA", 0.503854),
        "F_obs": 96.39,
        "M_obs": 89.92,
        "T_obs": 93.18,
    },
    "INDIA": {
        "name": "India",
        "country_code": "IND",
        "year": 2024,
        "s_F": _s_F_data.get("INDIA", 0.309070),
        "F_obs": 91.93,
        "M_obs": 86.76,
        "T_obs": 88.36,
    },
    "BANGLADESH": {
        "name": "Bangladés",
        "country_code": "BGD",
        "year": 2023,
        "s_F": _s_F_data.get("BANGLADESH", 0.345429),
        "F_obs": 95.77,
        "M_obs": 78.08,
        "T_obs": 84.19,
    },
}


def load_calibration_estimates() -> Dict[str, Dict[str, float]]:
    """
    Carga phi_0 y gamma_0 exclusivamente desde outputs/calibration_estimates.json.
    """
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "calibration_estimates.json")
    estimates = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, mode="r", encoding="utf-8") as f:
                data = json.load(f)
                summary = data.get("summary", {})
                for c_key, c_val in summary.items():
                    estimates[c_key.upper()] = {
                        "phi_0": float(c_val["phi_0"]),
                        "gamma_0": float(c_val["gamma_0"]),
                    }
        except Exception:
            pass
    return estimates


def update_country_database_from_calibration():
    """
    Actualiza COUNTRY_DATABASE poblando phi_0 y gamma_0 exclusivamente desde outputs/calibration_estimates.json.
    """
    estimates = load_calibration_estimates()
    for c_key, vals in estimates.items():
        if c_key in COUNTRY_DATABASE:
            COUNTRY_DATABASE[c_key]["phi_0"] = vals["phi_0"]
            COUNTRY_DATABASE[c_key]["gamma_0"] = vals["gamma_0"]


# Poblar automáticamente COUNTRY_DATABASE desde outputs/calibration_estimates.json
update_country_database_from_calibration()


def resolve_country_params(country_input: Any) -> Dict[str, Any]:
    """
    Normaliza el parámetro country_params aceptando un string de país o un dict de parámetros.
    Garantiza que phi_0 y gamma_0 se lean de outputs/calibration_estimates.json.
    """
    update_country_database_from_calibration()
    if isinstance(country_input, str):
        key = country_input.strip().upper()
        # Aliases comunes
        aliases = {
            "KENIA": "KENYA",
            "KEN": "KENYA",
            "NGA": "NIGERIA",
            "IND": "INDIA",
            "BGD": "BANGLADESH",
            "BANGLADES": "BANGLADESH",
        }
        resolved_key = aliases.get(key, key)
        if resolved_key in COUNTRY_DATABASE:
            c_info = COUNTRY_DATABASE[resolved_key].copy()
            if "phi_0" not in c_info or "gamma_0" not in c_info:
                raise RuntimeError(
                    f"País '{resolved_key}' no tiene estimaciones calibradas (phi_0, gamma_0). "
                    "outputs/calibration_estimates.json no contiene este país o no existe. "
                    "Ejecute 'make calibrate' para generarlo."
                )
            return c_info
        raise ValueError(f"País '{country_input}' no reconocido. Opciones válidas: {list(COUNTRY_DATABASE.keys())}")
    
    if isinstance(country_input, dict):
        required = ["s_F", "phi_0", "gamma_0"]
        missing = [k for k in required if k not in country_input]
        if missing:
            raise ValueError(f"El diccionario country_params carece de los campos requeridos: {missing}")
        return country_input.copy()

    raise TypeError("country_params debe ser un string con el nombre del país o un diccionario con s_F, phi_0 y gamma_0.")
