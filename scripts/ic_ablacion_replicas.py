# Uso (desde la raíz del repo): python scripts/ic_ablacion_replicas.py . 2 outputs
"""Reproduce la ablación recalibrada (Tabla 8 del repo) guardando las diferencias por réplica,
para calcular IC 95 % por bootstrap por conglomerados en dos etapas (mismo método que la Tabla 6)."""
import os, sys, json
from concurrent.futures import ProcessPoolExecutor
import numpy as np

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from itdt.model import ITDTModel
from itdt.parameters import FixedParameters, COUNTRY_DATABASE, load_ilostat_s_F_data
from itdt.experiments import REPLICA_SEEDS, TARGET_COUNTRIES

VARIANTS = [
    {"id": "full", "name": "Completo", "care": True, "reg_dcc": True, "phi_1": 0.30},
    {"id": "no_care", "name": "Sin restricción de cuidado", "care": False, "reg_dcc": True, "phi_1": 0.30},
    {"id": "no_dcc", "name": "Sin DCC regresivo", "care": True, "reg_dcc": False, "phi_1": 0.0},
    {"id": "neither", "name": "Sin ambos", "care": False, "reg_dcc": False, "phi_1": 0.0},
]
SEEDS = REPLICA_SEEDS[:20]


def task(args):
    v, c_key = args
    from itdt.calibrate import nested_bisection_calibration
    s_F_dict = load_ilostat_s_F_data()
    c_info = COUNTRY_DATABASE[c_key]
    s_F = float(s_F_dict[c_key]) if c_key in s_F_dict and s_F_dict[c_key] is not None else float(c_info["s_F"])
    F_obs, M_obs = c_info["F_obs"], c_info["M_obs"]
    fp_var = FixedParameters(care_enabled=v["care"], regressive_dcc=v["reg_dcc"], phi_1=v["phi_1"])
    if v["id"] == "full":
        cal = json.load(open("outputs/calibration_estimates.json", encoding="utf-8"))["summary"][c_key]
        phi_cal, gamma_cal = cal["phi_0"], cal["gamma_0"]
    elif v["care"]:
        cal = nested_bisection_calibration(country_key=c_key, s_F=s_F, F_obs=F_obs, M_obs=M_obs,
                                           seeds=[1000, 1001, 1002, 1003, 1004, 1005])
        phi_cal, gamma_cal = cal["phi_0"], cal["gamma_0"]
    else:
        from itdt.loco import bisection_calibrate_phi_to_target
        phi_cal, _, _, _ = bisection_calibrate_phi_to_target(
            country_key=c_key, s_F=s_F, target_value=M_obs, target_type="M", gamma_0=0.0,
            seeds=[1000, 1001, 1002, 1003, 1004, 1005], fixed_params=fp_var)
        gamma_cal = 0.0
    custom_c = {"s_F": s_F, "phi_0": phi_cal, "gamma_0": gamma_cal, "name": c_info["name"]}
    out = {k: [] for k in ["fem", "male", "gap", "exit", "own_f", "own_m"]}
    for s in SEEDS:
        m_a = ITDTModel(custom_c, scenario="A", seed=s, fixed_params=fp_var)
        ra = m_a.run()["summary_metrics"]
        m_b = ITDTModel(custom_c, scenario="B2", seed=s, fixed_params=fp_var)
        rb = m_b.run()["summary_metrics"]
        out["fem"].append(rb["mean_informality_female"] - ra["mean_informality_female"])
        out["male"].append(rb["mean_informality_male"] - ra["mean_informality_male"])
        out["gap"].append(rb["mean_gender_gap"] - ra["mean_gender_gap"])
        out["exit"].append(rb["mean_annual_exit_rate"] - ra["mean_annual_exit_rate"])
        rates = []
        for m in (m_a, m_b):
            fo = m.fem_mask[m.owners]
            rates.append((np.sum(m.is_formal_firm & fo) / max(1, np.sum(fo)) * 100.0,
                          np.sum(m.is_formal_firm & ~fo) / max(1, np.sum(~fo)) * 100.0))
        out["own_f"].append(rates[1][0] - rates[0][0])
        out["own_m"].append(rates[1][1] - rates[0][1])
    return v["id"], c_key, {"phi_0": phi_cal, "gamma_0": gamma_cal}, out


if __name__ == "__main__":
    jobs = [(v, c) for v in VARIANTS for c in TARGET_COUNTRIES]
    res = {}
    with ProcessPoolExecutor(max_workers=int(sys.argv[2]) if len(sys.argv) > 2 else 2) as ex:
        for vid, c, cal, out in ex.map(task, jobs):
            res.setdefault(vid, {})[c] = {"cal": cal, "diffs": out}
            print("listo", vid, c, cal, flush=True)
    json.dump(res, open(os.path.join(sys.argv[3] if len(sys.argv) > 3 else ".", "ablacion_replicas.json"), "w"), indent=1)
    print("FIN")
