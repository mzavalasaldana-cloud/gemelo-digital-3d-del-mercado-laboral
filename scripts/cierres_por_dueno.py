#!/usr/bin/env python3
"""
scripts/cierres_por_dueno.py

Cierres anuales y formalización neta por sexo del dueño de la empresa (Tablas 5, 6 y 7; Figura 3 del artículo).

No modifica el modelo: ejecuta ITDTModel paso a paso y, antes de cada paso, guarda el sexo del dueño
de cada empresa; después del paso clasifica las salidas registradas en `exited_firm_indices`.
No consume números aleatorios adicionales, por lo que cada réplica es idéntica a la del simulador base.

Definiciones (meses 109-120 de la política):
  tasa de cierre dueña (dueño) = salidas de empresas con dueña (dueño) en los 12 meses
                                 / número medio de empresas con dueña (dueño) en riesgo  x 100
  formalización por sexo del dueño = % de empresas formales entre las de dueña (dueño) al final del mes 120
  RR = media entre países de la tasa con dueña / media entre países de la tasa con dueño
  IC 95 %: bootstrap en dos etapas (países y réplicas), B = 4000, semilla 2026 (mismo método que outputs/table6_changes.md).

Uso (desde la raíz del repositorio):
    python scripts/cierres_por_dueno.py                      # Tabla 5 y Figura 3: escenarios A-D, R = 40
    python scripts/cierres_por_dueno.py --modo ablacion      # Tabla 6: B2 vs A, 4 variantes, R = 20
    python scripts/cierres_por_dueno.py --modo especificaciones  # Tabla 7: B2 en las 4 especificaciones, R = 40
"""
import os
import sys
import json
import argparse
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.abspath("."))
from itdt.model import ITDTModel  # noqa: E402
from itdt.metrics import aggregate_evaluation_window  # noqa: E402

COUNTRIES = ["KENYA", "NIGERIA", "INDIA", "BANGLADESH"]
SCENARIOS = ["A", "B1", "B2", "C", "D"]
SEEDS = list(range(20260, 20300))


def run_replica(args):
    country, scenario, seed = args[:3]
    cfg, fp = (args[3], args[4]) if len(args) > 3 else (country, None)
    m = ITDTModel(cfg, scenario=scenario, seed=seed, burn_in_months=96, policy_months=120, fixed_params=fp)
    total = m.burn_in_months + m.policy_months
    hist = []  # (salidas dueña, salidas dueño, n dueña, n dueño) por mes
    while m.month < total:
        fem_owner = m.fem_mask[m.owners].copy()  # sexo del dueño antes de salidas y reemplazos
        rec = m.step(record_metrics=True)
        ex = np.asarray(rec.get("exited_firm_indices", []), dtype=int)
        hist.append((int(fem_owner[ex].sum()), int((~fem_owner[ex]).sum()), int(fem_owner.sum()), int((~fem_owner).sum())))
    summary = aggregate_evaluation_window(m.monthly_history, window_size=12)
    h = np.array(hist[-12:], dtype=float)
    fo = m.fem_mask[m.owners]
    return {
        "country": country, "scenario": scenario, "seed": seed,
        "informality_total": summary["mean_informality_total"],
        "informality_female": summary["mean_informality_female"],
        "informality_male": summary["mean_informality_male"],
        "gender_gap": summary["mean_gender_gap"],
        "annual_exit_rate": summary["mean_annual_exit_rate"],
        # trayectoria mensual de los 120 meses de política (Figura 3): total, mujeres, hombres, brecha
        "monthly": [(r["informality_total"], r["informality_female"], r["informality_male"], r["gender_gap"])
                    for r in m.monthly_history[m.burn_in_months:]],
        "exit_female_owner": h[:, 0].sum() / h[:, 2].mean() * 100.0,
        "exit_male_owner": h[:, 1].sum() / h[:, 3].mean() * 100.0,
        "formal_share_female_owner": float(np.sum(m.is_formal_firm & fo) / max(1, np.sum(fo)) * 100.0),
        "formal_share_male_owner": float(np.sum(m.is_formal_firm & ~fo) / max(1, np.sum(~fo)) * 100.0),
    }


def two_stage_bootstrap(by_country, stat, B=4000, seed=2026):
    rng = np.random.default_rng(seed)
    point = stat([v.mean(axis=0) for v in by_country.values()])
    keys = list(by_country)
    draws = []
    for _ in range(B):
        means = []
        for c in rng.choice(keys, size=len(keys), replace=True):
            v = by_country[c]
            means.append(v[rng.integers(0, len(v), len(v))].mean(axis=0))
        draws.append(stat(means))
    return point, float(np.nanpercentile(draws, 2.5)), float(np.nanpercentile(draws, 97.5))


VARIANTES = {"full": (True, True, 0.30), "no_care": (False, True, 0.30),
             "no_dcc": (True, False, 0.0), "neither": (False, False, 0.0)}


def country_cfg(c, phi_0, gamma_0):
    from itdt.parameters import COUNTRY_DATABASE, load_ilostat_s_F_data
    sf = load_ilostat_s_F_data()
    info = COUNTRY_DATABASE[c]
    s_F = float(sf[c]) if c in sf and sf[c] is not None else float(info["s_F"])
    return {"s_F": s_F, "phi_0": phi_0, "gamma_0": gamma_0, "name": info["name"]}


def rr_stat(ms):
    den = np.mean([m[1] for m in ms])
    return np.mean([m[0] for m in ms]) / den if den > 0 else np.nan


def main_ablacion(a):
    """Tabla 6: mismas calibraciones que outputs/ablacion_replicas.json (scripts/ic_ablacion_replicas.py)."""
    from itdt.parameters import FixedParameters
    cal = json.load(open("outputs/ablacion_replicas.json", encoding="utf-8"))
    jobs = []
    for v, (care, reg, phi1) in VARIANTES.items():
        fp = FixedParameters(care_enabled=care, regressive_dcc=reg, phi_1=phi1)
        for c in COUNTRIES:
            k = cal[v][c]["cal"]
            jobs += [(c, "B2", s, country_cfg(c, k["phi_0"], k["gamma_0"]), fp, v) for s in SEEDS[:20]]
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        reps = list(ex.map(run_replica, jobs, chunksize=4))
    out = {}
    for v in VARIANTES:
        by_c = {c: np.array([[r["exit_female_owner"], r["exit_male_owner"]] for r, j in zip(reps, jobs)
                             if j[5] == v and j[0] == c]) for c in COUNTRIES}
        rr, lo, hi = two_stage_bootstrap(by_c, rr_stat)
        ef = float(np.mean([x[:, 0].mean() for x in by_c.values()]))
        em = float(np.mean([x[:, 1].mean() for x in by_c.values()]))
        out[v] = dict(exit_female_owner=ef, exit_male_owner=em, rr=rr, rr_ci=[lo, hi])
        print(f"{v:8} B2 cierre dueña {ef:6.2f}  dueño {em:6.2f}  RR {rr:.2f} [{lo:.2f}, {hi:.2f}]")
    json.dump(out, open(a.out.replace(".json", "_ablacion.json"), "w", encoding="utf-8"), indent=1)


def main_especificaciones(a):
    """Tabla 7: recalibra cada especificación con scripts/robustez_reglas_entrada.py y corre B2 (R = 40)."""
    from itdt.parameters import FixedParameters, COUNTRY_DATABASE, load_ilostat_s_F_data
    sys.path.insert(0, os.path.abspath("scripts"))
    import robustez_reglas_entrada as rb
    sf = load_ilostat_s_F_data()
    out = {}
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for er, ym in [("forced_informal", "dynamic"), ("forced_informal", "fixed"), ("free", "dynamic"), ("free", "fixed")]:
            tasks = [(c, sf.get(c, COUNTRY_DATABASE[c]["s_F"]), COUNTRY_DATABASE[c]["F_obs"], COUNTRY_DATABASE[c]["M_obs"],
                      [1000, 1001, 1002, 1003, 1004, 1005], er, ym) for c in COUNTRIES]
            cal = {r["country"]: r for r in ex.map(rb._calibrate_single_country_worker, tasks)}
            fp = FixedParameters(entry_rule=er, ybar_mode=ym)
            jobs = [(c, "B2", s, country_cfg(c, cal[c]["phi_0"], cal[c]["gamma_0"]), fp) for c in COUNTRIES for s in SEEDS[: a.R]]
            reps = list(ex.map(run_replica, jobs, chunksize=4))
            ef = float(np.mean([np.mean([r["exit_female_owner"] for r in reps if r["country"] == c]) for c in COUNTRIES]))
            em = float(np.mean([np.mean([r["exit_male_owner"] for r in reps if r["country"] == c]) for c in COUNTRIES]))
            out[f"{er}/{ym}"] = dict(exit_female_owner=ef, exit_male_owner=em)
            print(f"{er:16} {ym:8} B2 cierre dueña {ef:6.2f}  dueño {em:6.2f}")
    json.dump(out, open(a.out.replace(".json", "_especificaciones.json"), "w", encoding="utf-8"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modo", choices=["escenarios", "ablacion", "especificaciones"], default="escenarios")
    ap.add_argument("--R", type=int, default=40)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--out", default="outputs/cierres_por_dueno.json")
    a = ap.parse_args()
    if a.modo == "ablacion":
        return main_ablacion(a)
    if a.modo == "especificaciones":
        return main_especificaciones(a)

    jobs = [(c, s, seed) for c in COUNTRIES for s in SCENARIOS for seed in SEEDS[: a.R]]
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        reps = list(ex.map(run_replica, jobs, chunksize=4))

    def get(c, s, keys):
        rs = sorted([r for r in reps if r["country"] == c and r["scenario"] == s], key=lambda r: r["seed"])
        return np.array([[r[k] for k in keys] for r in rs])

    rr = rr_stat
    table = {}
    print(f"{'Esc.':4} {'cierre dueña':>13} {'cierre dueño':>13} {'RR [IC 95 %]':>22} {'Δform dueña':>12} {'Δform dueño':>12}")
    for s in SCENARIOS:
        by_c = {c: get(c, s, ["exit_female_owner", "exit_male_owner"]) for c in COUNTRIES}
        ef = float(np.mean([v[:, 0].mean() for v in by_c.values()]))
        em = float(np.mean([v[:, 1].mean() for v in by_c.values()]))
        r, lo, hi = two_stage_bootstrap(by_c, rr) if em > 0.05 else (np.nan, np.nan, np.nan)
        d = {c: get(c, s, ["formal_share_female_owner", "formal_share_male_owner"])
             - get(c, "A", ["formal_share_female_owner", "formal_share_male_owner"]) for c in COUNTRIES}
        df = float(np.mean([v[:, 0].mean() for v in d.values()]))
        dm = float(np.mean([v[:, 1].mean() for v in d.values()]))
        table[s] = dict(exit_female_owner=ef, exit_male_owner=em, rr=r, rr_ci=[lo, hi],
                        d_formal_female_owner=df, d_formal_male_owner=dm)
        rr_txt = "n. d." if np.isnan(r) else f"{r:.2f} [{lo:.2f}, {hi:.2f}]"
        print(f"{s:4} {ef:13.2f} {em:13.2f} {rr_txt:>22} {df:+12.1f} {dm:+12.1f}")

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"resumen": table, "replicas": reps}, open(a.out, "w", encoding="utf-8"), indent=1)
    print("Guardado en", a.out)


if __name__ == "__main__":
    main()
