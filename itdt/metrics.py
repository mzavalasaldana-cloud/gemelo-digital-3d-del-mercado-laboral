"""
itdt.metrics: Métricas de evaluación, gradientes distributivos y registro mensual.
"""

from typing import Dict, Any, List, Optional
import numpy as np

def compute_monthly_metrics(
    month: int,
    is_burn_in: bool,
    worker_is_formal: np.ndarray,
    g: np.ndarray,
    e: np.ndarray,
    r: np.ndarray,
    h: np.ndarray,
    is_formal_firm: np.ndarray,
    Y: np.ndarray,
    L: np.ndarray,
    num_exits: int,
    tau_c: float,
    tau_w: float,
    omega_F: float,
    d_sys: float,
    T_k: float,
    willing_workers: np.ndarray,
    precomputed_bins: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Computa el registro mensual completo del modelo para el paso t.
    """
    N_W = len(worker_is_formal)
    N_F = len(is_formal_firm)

    # 1. Tasas de informalidad
    inf_total = (1.0 - np.mean(worker_is_formal)) * 100.0
    
    if precomputed_bins:
        fem_mask = precomputed_bins["fem_mask"]
        male_mask = precomputed_bins["male_mask"]
    else:
        fem_mask = g == 1
        male_mask = g == 0

    inf_female = (1.0 - np.mean(worker_is_formal[fem_mask])) * 100.0 if np.any(fem_mask) else 0.0
    inf_male = (1.0 - np.mean(worker_is_formal[male_mask])) * 100.0 if np.any(male_mask) else 0.0
    gender_gap = inf_female - inf_male

    # 2. Cierres de empresas (tasa anualizada en %)
    annual_exit_rate = (num_exits / N_F) * 12.0 * 100.0

    # 3. Recaudación fiscal
    corporate_tax = float(np.sum(tau_c * Y[is_formal_firm]))
    labor_contributions = float(np.sum(tau_w * omega_F * h[worker_is_formal]))
    total_fiscal_revenue = corporate_tax + labor_contributions

    # 4. Gradientes distributivos
    # Por educación (0 = básica, 1 = media, 2 = superior)
    grad_edu = {}
    if precomputed_bins and "edu_masks" in precomputed_bins:
        for edu_level in [0, 1, 2]:
            mask_edu = precomputed_bins["edu_masks"][edu_level]
            grad_edu[edu_level] = round(float((1.0 - np.mean(worker_is_formal[mask_edu])) * 100.0), 2)
    else:
        for edu_level in [0, 1, 2]:
            mask_edu = e == edu_level
            grad_edu[edu_level] = round(float((1.0 - np.mean(worker_is_formal[mask_edu])) * 100.0), 2) if np.any(mask_edu) else 0.0

    # Por zona (rural = 1, urbano = 0)
    if precomputed_bins:
        rural_mask = precomputed_bins["rural_mask"]
        urban_mask = precomputed_bins["urban_mask"]
    else:
        rural_mask = r == 1
        urban_mask = r == 0

    grad_zone = {
        "rural": round(float((1.0 - np.mean(worker_is_formal[rural_mask])) * 100.0), 2) if np.any(rural_mask) else 0.0,
        "urban": round(float((1.0 - np.mean(worker_is_formal[urban_mask])) * 100.0), 2) if np.any(urban_mask) else 0.0,
    }

    # Por quintiles de productividad h
    grad_quintiles = {}
    if precomputed_bins and "quintile_bins" in precomputed_bins:
        quintile_bins = precomputed_bins["quintile_bins"]
        for q in range(1, 6):
            q_mask = quintile_bins == q
            grad_quintiles[q] = round(float((1.0 - np.mean(worker_is_formal[q_mask])) * 100.0), 2)
    else:
        quintile_thresholds = np.percentile(h, [20, 40, 60, 80])
        quintile_bins = np.digitize(h, quintile_thresholds) + 1
        for q in range(1, 6):
            q_mask = quintile_bins == q
            grad_quintiles[q] = round(float((1.0 - np.mean(worker_is_formal[q_mask])) * 100.0), 2) if np.any(q_mask) else 0.0

    # Conteo de vacantes formales
    formal_vacancies = int(np.sum(L[is_formal_firm]))
    formal_firms_count = int(np.sum(is_formal_firm))

    r_fem = round(inf_female, 2)
    r_male = round(inf_male, 2)
    r_gap = round(r_fem - r_male, 2)

    return {
        "month": month,
        "is_burn_in": is_burn_in,
        "informality_total": round(inf_total, 2),
        "informality_female": r_fem,
        "informality_male": r_male,
        "gender_gap": r_gap,
        "annual_exit_rate": round(annual_exit_rate, 2),
        "firm_closures_count": int(num_exits),
        "formal_firms_count": formal_firms_count,
        "informal_firms_count": N_F - formal_firms_count,
        "formal_vacancies": formal_vacancies,
        "willing_workers_count": int(np.sum(willing_workers)),
        "fiscal_revenue": round(total_fiscal_revenue, 2),
        "corporate_tax_revenue": round(corporate_tax, 2),
        "labor_contributions_revenue": round(labor_contributions, 2),
        "d_sys": round(d_sys, 4),
        "temperature": round(T_k, 4),
        "informality_by_education": grad_edu,
        "informality_by_zone": grad_zone,
        "informality_by_quintile": grad_quintiles,
    }


def aggregate_evaluation_window(monthly_records: List[Dict[str, Any]], window_size: int = 12) -> Dict[str, Any]:
    """
    Calcula el resumen de las métricas sobre los últimos window_size meses de simulación
    (equivalente a los meses 109-120 de la política en el artículo).
    """
    if not monthly_records:
        return {}

    eval_slice = monthly_records[-window_size:]

    mean_inf_total = float(np.mean([m["informality_total"] for m in eval_slice]))
    mean_inf_fem = float(np.mean([m["informality_female"] for m in eval_slice]))
    mean_inf_male = float(np.mean([m["informality_male"] for m in eval_slice]))
    mean_gap = float(np.mean([m["gender_gap"] for m in eval_slice]))
    mean_exit_rate = float(np.mean([m["annual_exit_rate"] for m in eval_slice]))
    mean_fiscal = float(np.mean([m["fiscal_revenue"] for m in eval_slice]))

    edu_avg = {
        "basic_e0": round(float(np.mean([m["informality_by_education"][0] for m in eval_slice])), 2),
        "middle_e1": round(float(np.mean([m["informality_by_education"][1] for m in eval_slice])), 2),
        "advanced_e2": round(float(np.mean([m["informality_by_education"][2] for m in eval_slice])), 2),
    }

    zone_avg = {
        "rural": round(float(np.mean([m["informality_by_zone"]["rural"] for m in eval_slice])), 2),
        "urban": round(float(np.mean([m["informality_by_zone"]["urban"] for m in eval_slice])), 2),
    }

    quintiles_avg = {
        q: round(float(np.mean([m["informality_by_quintile"][q] for m in eval_slice])), 2)
        for q in range(1, 6)
    }

    return {
        "mean_informality_total": round(mean_inf_total, 2),
        "mean_informality_female": round(mean_inf_fem, 2),
        "mean_informality_male": round(mean_inf_male, 2),
        "mean_gender_gap": round(mean_gap, 2),
        "mean_annual_exit_rate": round(mean_exit_rate, 2),
        "mean_fiscal_revenue": round(mean_fiscal, 2),
        "gradients": {
            "education": edu_avg,
            "zone": zone_avg,
            "productivity_quintiles": quintiles_avg,
        },
        "evaluation_window_months": [m["month"] for m in eval_slice],
    }
