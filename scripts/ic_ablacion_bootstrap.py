# Uso: python scripts/ic_ablacion_bootstrap.py outputs/ablacion_replicas.json outputs/ablacion_ic95.json
import json, sys
import numpy as np
res = json.load(open(sys.argv[1]))
countries = ['KENYA', 'NIGERIA', 'INDIA', 'BANGLADESH']
rng = np.random.default_rng(2026)
out = {}
for vid in ['full', 'no_care', 'no_dcc', 'neither']:
    out[vid] = {}
    for met in ['fem', 'male', 'gap', 'exit', 'own_f', 'own_m']:
        vec = {c: np.array(res[vid][c]['diffs'][met]) for c in countries}
        point = float(np.mean([vec[c].mean() for c in countries]))
        boots = []
        for _ in range(4000):
            bc = rng.choice(countries, size=4, replace=True)
            boots.append(np.mean([rng.choice(vec[c], size=len(vec[c]), replace=True).mean() for c in bc]))
        out[vid][met] = point
        out[vid][met + '_ci'] = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]
    print(vid, {k: (round(v, 2) if isinstance(v, float) else [round(x, 2) for x in v]) for k, v in out[vid].items()})
# Diferencia pareada dueño − dueña en el aumento de empresas formales (generador aparte)
rng2 = np.random.default_rng(2027)
for vid in ['full', 'no_care', 'no_dcc', 'neither']:
    vec = {c: np.array(res[vid][c]['diffs']['own_m']) - np.array(res[vid][c]['diffs']['own_f']) for c in countries}
    point = float(np.mean([vec[c].mean() for c in countries]))
    boots = [np.mean([rng2.choice(vec[c], size=len(vec[c]), replace=True).mean() for c in rng2.choice(countries, size=4, replace=True)]) for _ in range(4000)]
    out[vid]['own_m_minus_f'] = point
    out[vid]['own_m_minus_f_ci'] = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]
    print(vid, 'dueño - dueña', round(point, 2), [round(x, 2) for x in out[vid]['own_m_minus_f_ci']])
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), indent=1)
