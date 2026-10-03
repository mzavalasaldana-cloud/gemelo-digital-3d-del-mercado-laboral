"""
itdt.parameters: Parámetros fijos, datos de países (Tabla A1 y Tabla 2) y configuraciones de escenarios.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union
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


_s_F_data = load_ilostat_s_F_data()

# Calibraciones empíricas por país (Tabla 2 del artículo)
# s_F cargado desde data/ilostat_s_F.csv (no derivado de F, M, T)
COUNTRY_DATABASE: Dict[str, Dict[str, Any]] = {
    "KENYA": {
        "name": "Kenia",
        "country_code": "KEN",
        "year": 2019,
        "s_F": _s_F_data.get("KENYA", 0.476259), # Proporción oficial ILOSTAT
        "phi_0": 3.08,                          # Parámetro calibrado DCC
        "gamma_0": 0.461,                       # Penalización de cuidados calibrada
        "F_obs": 90.19,                         # Tasa femenina observada ILOSTAT (%)
        "M_obs": 83.13,                         # Tasa masculina observada ILOSTAT (%)
        "T_obs": 86.49,                         # Tasa total observada ILOSTAT (%)
    },
    "NIGERIA": {
        "name": "Nigeria",
        "country_code": "NGA",
        "year": 2024,
        "s_F": _s_F_data.get("NIGERIA", 0.503854),
        "phi_0": 8.96,
        "gamma_0": 0.620,
        "F_obs": 96.39,
        "M_obs": 89.92,
        "T_obs": 93.18,
    },
    "INDIA": {
        "name": "India",
        "country_code": "IND",
        "year": 2024,
        "s_F": _s_F_data.get("INDIA", 0.309070),
        "phi_0": 4.84,
        "gamma_0": 0.464,
        "F_obs": 91.93,
        "M_obs": 86.76,
        "T_obs": 88.36,
    },
    "BANGLADESH": {
        "name": "Bangladés",
        "country_code": "BGD",
        "year": 2023,
        "s_F": _s_F_data.get("BANGLADESH", 0.345429),
        "phi_0": 2.03,
        "gamma_0": 0.763,
        "F_obs": 95.77,
        "M_obs": 78.08,
        "T_obs": 84.19,
    },
}


def resolve_country_params(country_input: Any) -> Dict[str, Any]:
    """
    Normaliza el parámetro country_params aceptando un string de país o un dict de parámetros.
    """
    if isinstance(country_input, str):
        key = country_input.strip().upper()
        if key in COUNTRY_DATABASE:
            return COUNTRY_DATABASE[key].copy()
        # Aliases comunes
        aliases = {
            "KENIA": "KENYA",
            "KEN": "KENYA",
            "NGA": "NIGERIA",
            "IND": "INDIA",
            "BGD": "BANGLADESH",
            "BANGLADES": "BANGLADESH",
        }
        if key in aliases and aliases[key] in COUNTRY_DATABASE:
            return COUNTRY_DATABASE[aliases[key]].copy()
        raise ValueError(f"País '{country_input}' no reconocido. Opciones válidas: {list(COUNTRY_DATABASE.keys())}")
    
    if isinstance(country_input, dict):
        required = ["s_F", "phi_0", "gamma_0"]
        missing = [k for k in required if k not in country_input]
        if missing:
            raise ValueError(f"El diccionario country_params carece de los campos requeridos: {missing}")
        return country_input.copy()

    raise TypeError("country_params debe ser un string con el nombre del país o un diccionario con s_F, phi_0 y gamma_0.")
