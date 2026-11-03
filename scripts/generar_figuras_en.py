"""Figuras del artículo ITDT para CRORR. Uso (desde la raíz del repositorio):
    python scripts/cierres_por_dueno.py   # genera outputs/cierres_por_dueno.json
    python scripts/generar_figuras_en.py
Tipografía serif uniforme, PNG a 800 ppp + PDF vectorial.
Datos: outputs/cierres_por_dueno.json y outputs/sanctions_sweep_data.csv."""
import json, sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import pandas as pd

W = os.getcwd()  # ejecutar desde la raíz del repositorio
OUT = os.environ.get("FIG_DIR", os.path.join(W, "outputs", "figuras_articulo_en"))
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Liberation Serif", "TeX Gyre Termes", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 7.8,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 3, "ytick.major.size": 3,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#3d3d3a", "xtick.color": "#3d3d3a", "ytick.color": "#3d3d3a",
    "axes.labelcolor": "#1f1f1d", "text.color": "#1f1f1d",
    "legend.frameon": False, "savefig.dpi": 600, "pdf.fonttype": 42,
    "axes.titleweight": "normal", "axes.titlelocation": "left",
})
INK, INK2, GRID = "#1f1f1d", "#52514e", "#e4e3df"
FEM, MAL, TOT, GAP = "#eb6834", "#2a78d6", "#3d3d3a", "#0f8f63"   # mujeres, hombres, total, brecha
NEUT = "#9a9993"
WIDTH = 6.3  # pulgadas (160 mm)


def grid(ax, axis="y"):
    ax.grid(axis=axis, color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=800, bbox_inches="tight", pad_inches=0.03, facecolor="white")
    fig.savefig(os.path.join(OUT, name + ".pdf"), bbox_inches="tight", pad_inches=0.03, facecolor="white")
    plt.close(fig)


C = ["KENYA", "NIGERIA", "INDIA", "BANGLADESH"]
SC = ["A", "B1", "B2", "C", "D"]
SCLAB = ["A: statu\nquo", "B1: GovTech\nmoderado", "B2: GovTech\nintensivo", "C: red de\ncuidados", "D:\nintegrado"]
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(W, "outputs", "cierres_por_dueno.json")
_raw = json.load(open(SRC))
if isinstance(_raw, dict):  # salida de scripts/cierres_por_dueno.py
    D = [dict(r, total=r["informality_total"], fem=r["informality_female"], male=r["informality_male"],
              gap=r["gender_gap"], exit=r["annual_exit_rate"], exit_f=r["exit_female_owner"], exit_m=r["exit_male_owner"],
              form_f=r["formal_share_female_owner"], form_m=r["formal_share_male_owner"]) for r in _raw["replicas"]]
else:
    D = _raw


def reps(c, s):
    return sorted([r for r in D if r["country"] == c and r["scenario"] == s], key=lambda r: r["seed"])


def mean_sd(s, key):
    """Media de los 4 países y DE = promedio de las 4 DE por país (misma convención que la Tabla 5)."""
    m = np.mean([np.mean([r[key] for r in reps(c, s)]) for c in C])
    sd = np.mean([np.std([r[key] for r in reps(c, s)], ddof=1) for c in C])
    return m, sd


# ---------------------------------------------------------------- Figura 1
def box(ax, x, y, w, h, title, body, ec, fc, tc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.06",
                                linewidth=1.0, edgecolor=ec, facecolor=fc))
    ax.text(x + w / 2, y + h - 0.17, title, ha="center", va="top", fontsize=9.2, fontweight="bold", color=tc)
    ax.text(x + w / 2, y + 0.66, body, ha="center", va="center", fontsize=8.0, color=INK, linespacing=1.25)


def arrow(ax, p, q, **kw):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=9, linewidth=1.0, color=INK2,
                                 shrinkA=0, shrinkB=0, **kw))


def fig1():
    fig, ax = plt.subplots(figsize=(WIDTH, 3.15))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    w, h = 2.75, 1.95
    xs = [0.05, 3.62, 7.2]
    top, bot = 2.95, 0.05
    yel = ("#a16a00", "#fdf3d8", "#7a5000")
    grn = ("#1f7a4f", "#e3f4ea", "#155c3a")
    blu = ("#2a64b8", "#e3edfa", "#1d4f96")
    vio = ("#6a4bb5", "#efe9f9", "#53379a")
    box(ax, xs[0], top, w, h, "1. Comprensión\ndel negocio", "Pregunta de política,\nhipótesis H1 y H2,\nescenarios A–D", *yel)
    box(ax, xs[1], top, w, h, "2. Comprensión\nde los datos", "ILOSTAT por sexo,\neducación y zona;\nhoras de cuidado", *grn)
    box(ax, xs[2], top, w, h, "3. Preparación\nde los datos", "Descarga SDMX,\ncálculo de $s_F$; momentos de\ncalibración / validación", *grn)
    box(ax, xs[2], bot, w, h, "4. Modelado", "Trabajadores y empresas;\ncalibración SMM\nde $\\phi_0$ y $\\gamma_0$", *blu)
    box(ax, xs[1], bot, w, h, "5. Evaluación", "E1–E4, LOCO,\ngradientes, escenarios,\nablación y robustez", *blu)
    box(ax, xs[0], bot, w, h, "6. Despliegue", "Paquete Python, API,\npruebas automatizadas\ny repositorio (Zenodo)", *vio)
    ym_t, ym_b = top + h / 2, bot + h / 2
    arrow(ax, (xs[0] + w + 0.06, ym_t), (xs[1] - 0.06, ym_t))
    arrow(ax, (xs[1] + w + 0.06, ym_t), (xs[2] - 0.06, ym_t))
    arrow(ax, (xs[2] + w / 2, top - 0.06), (xs[2] + w / 2, bot + h + 0.06))
    arrow(ax, (xs[2] - 0.06, ym_b), (xs[1] + w + 0.06, ym_b))
    arrow(ax, (xs[1] - 0.06, ym_b), (xs[0] + w + 0.06, ym_b))
    arrow(ax, (xs[0] + w / 2, bot + h + 0.06), (xs[0] + w / 2, top - 0.06))
    # iteración evaluación -> comprensión del negocio
    arrow(ax, (xs[1] + w / 2, bot + h + 0.06), (xs[0] + w - 0.25, top - 0.06),
          connectionstyle="arc3,rad=-0.15", linestyle=(0, (3, 2)))
    ax.text(2.35, 2.42, "iteración", fontsize=7.3, color=INK2, style="italic", ha="center", va="center", rotation=0)
    save(fig, "figura1_crispdm")


# ---------------------------------------------------------------- Figura 2
def fig2():
    fig, ax = plt.subplots(figsize=(WIDTH, 3.6))
    ax.set_xlim(-0.02, 10.02); ax.set_ylim(0, 6); ax.axis("off")

    def panel(x, y, w, h, title, items, ec, fc, tc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.08",
                                    linewidth=1.0, edgecolor=ec, facecolor=fc))
        ax.text(x + w / 2, y + h - 0.2, title, ha="center", va="top", fontsize=9.5, fontweight="bold", color=tc)
        for k, it in enumerate(items):
            ax.text(x + 0.18, y + h - 0.68 - k * 0.36, "•  " + it, ha="left", va="top", fontsize=8.1, color=INK)

    panel(2.0, 4.0, 6.0, 1.9, "Governance module (State)",
          ["Taxes ($\\tau_w$, $\\tau_c$) and sanctions ($\\mu_0$, $\\mu_1$, $\\xi$)",
           "Digital coverage $D_{sys}(t)$ and audit probability $P_{aud}$",
           "DCC subsidy and public care network"], "#a16a00", "#fdf3d8", "#7a5000")
    panel(0.0, 0.05, 4.15, 2.85, "Workers ($N_W$ = 6,000)",
          ["Sex, education, area; productivity $h_i$",
           "Care hours $H_{care,i}$",
           "Digital literacy $K_{dig,i}$",
           "Compares $U_{i,F}$ and $U_{i,I}$ (eq. 1)",
           "State: formal / informal"], "#1f7a4f", "#e3f4ea", "#155c3a")
    panel(5.85, 0.05, 4.15, 2.85, "Firms ($N_F$ = 600)",
          ["Productivity $A_j$, capital $K_j$, owner",
           "Profits $\\Pi_{j,F}$ and $\\Pi_{j,I}$ (eq. 2)",
           "Compliance cost $DCC_j$ (eq. 3)",
           "Metropolis rule, exit and entry",
           "State: formal / informal"], "#2a64b8", "#e3edfa", "#1d4f96")
    arrow(ax, (3.2, 3.95), (2.0, 2.98))
    arrow(ax, (6.8, 3.95), (8.0, 2.98))
    ax.add_patch(FancyArrowPatch((4.22, 1.75), (5.78, 1.75), arrowstyle="<|-|>", mutation_scale=9,
                                 linewidth=1.0, color=INK2))
    ax.text(5.0, 1.6, "Formal\nvacancies by\nproductivity\nranking", ha="center", va="top",
            fontsize=7.4, color=INK2, linespacing=1.15)
    save(fig, "figura2_arquitectura")


# ---------------------------------------------------------------- Figura 3
def traj(s):
    arr = np.array([[r["monthly"] for r in reps(c, s)] for c in C])  # (4, 40, 120, 4)
    mean = arr.mean(axis=1).mean(axis=0)
    sd = arr.std(axis=1, ddof=1).mean(axis=0)
    return mean, sd


def fig3():
    t = np.arange(1, 121)
    mA, _ = traj("A"); mD, sD = traj("D"); mB, sB = traj("B2")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(WIDTH, 2.6), gridspec_kw={"width_ratios": [1.25, 1], "wspace": 0.32})
    for k, (col, lab, ls) in enumerate([(TOT, "Total", "-"), (FEM, "Women", "-"), (MAL, "Men", "-")]):
        a1.fill_between(t, mD[:, k] - sD[:, k], mD[:, k] + sD[:, k], color=col, alpha=0.13, linewidth=0)
        a1.plot(t, mD[:, k], color=col, lw=1.4, ls=ls, label=lab)
        a1.plot(t, mA[:, k], color=col, lw=0.9, ls=(0, (3, 2)), alpha=0.85)
    a1.text(121, mA[-1, 1] + 1.0, "A (status quo)", fontsize=7.2, color=INK2, ha="right", va="bottom", style="italic")
    a1.text(40, 57.5, "D (integrated)", fontsize=7.2, color=INK2, ha="center", va="top", style="italic")
    a1.set_xlim(0, 121); a1.set_ylim(40, 100)
    a1.set_xticks([1, 24, 48, 72, 96, 120])
    a1.set_xlabel("Policy month"); a1.set_ylabel("Informality rate (%)")
    a1.set_title("(a) Informality by sex: D vs. A")
    grid(a1)
    a1.legend(loc="lower left", ncol=3, handlelength=1.6, columnspacing=1.0)

    for m, s, col, lab, ls, mk in [(mA, None, NEUT, "A: status quo", (0, (3, 2)), None),
                                   (mB, sB, TOT, "B2: intensive GovTech", "-", "s"),
                                   (mD, sD, GAP, "D: integrated", "-", None)]:
        if s is not None:
            a2.fill_between(t, m[:, 3] - s[:, 3], m[:, 3] + s[:, 3], color=col, alpha=0.13, linewidth=0)
        a2.plot(t, m[:, 3], color=col, lw=1.4, ls=ls, label=lab, marker=mk, markevery=12, markersize=3.2)
    a2.set_xlim(0, 121); a2.set_ylim(0, 45); a2.set_xticks([1, 24, 48, 72, 96, 120])
    a2.set_xlabel("Policy month"); a2.set_ylabel("Women − men gap (p.p.)")
    a2.set_title("(b) Gender gap")
    grid(a2)
    a2.legend(loc="upper left", handlelength=1.8)
    save(fig, "figura3_trayectorias")
    return mD


# ---------------------------------------------------------------- Figura 4
def fig4():
    x = np.arange(5); w = 0.36
    ef = [mean_sd(s, "exit_f") for s in SC]; em = [mean_sd(s, "exit_m") for s in SC]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(WIDTH, 2.7), gridspec_kw={"wspace": 0.3})
    a1.bar(x - w / 2 - 0.01, [v[0] for v in ef], w, yerr=[v[1] for v in ef], color=FEM, label="Female owner",
           error_kw=dict(elinewidth=0.6, capsize=2, ecolor=INK))
    a1.bar(x + w / 2 + 0.01, [v[0] for v in em], w, yerr=[v[1] for v in em], color=MAL, label="Male owner",
           error_kw=dict(elinewidth=0.6, capsize=2, ecolor=INK))
    for i in (2, 4):
        top = max(ef[i][0] + ef[i][1], em[i][0] + em[i][1])
        a1.text(x[i], top + 1.2, f"RR = {ef[i][0] / em[i][0]:.2f}".replace(".", "."), ha="center", fontsize=7.6, color=INK)
    a1.set_xticks(x); a1.set_xticklabels(SC, fontsize=8.5); a1.set_xlabel("Scenario")
    a1.set_ylabel("Annual firm closures (%)"); a1.set_ylim(0, 42)
    a1.set_title("(a) Annual closures by owner sex"); grid(a1)
    h, l = a1.get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, 1.07), ncol=2)

    dff, dfm = [], []
    for s in SC[1:]:
        f = np.mean([np.mean([r["form_f"] for r in reps(c, s)]) - np.mean([r["form_f"] for r in reps(c, "A")]) for c in C])
        m = np.mean([np.mean([r["form_m"] for r in reps(c, s)]) - np.mean([r["form_m"] for r in reps(c, "A")]) for c in C])
        dff.append(f); dfm.append(m)
    x2 = np.arange(4)
    a2.bar(x2 - w / 2 - 0.01, dff, w, color=FEM, label="Female owner")
    a2.bar(x2 + w / 2 + 0.01, dfm, w, color=MAL, label="Male owner")
    for i in range(4):
        for dx, v in ((-w / 2, dff[i]), (w / 2, dfm[i])):
            a2.text(x2[i] + dx, max(v, 0) + 0.8, f"{v:+.1f}".replace("-", "−"), ha="center", va="bottom", fontsize=6.8, color=INK)
    a2.axhline(0, color=INK2, lw=0.6)
    a2.set_xticks(x2); a2.set_xticklabels(SC[1:], fontsize=8.5); a2.set_xlabel("Scenario")
    a2.set_ylabel("Δ formal firms vs. A (p.p.)"); a2.set_ylim(-3, 50)
    a2.set_title("(b) Net formalization by owner sex"); grid(a2)
    save(fig, "figura4_cierres_dueno")
    return ef, em, dff, dfm


# ---------------------------------------------------------------- Figura 5
def fig5():
    df = pd.read_csv(os.environ.get("SWEEP_CSV", os.path.join(W, "outputs", "sanctions_sweep_data.csv")))
    x = df["multiplier"].values
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(WIDTH, 2.7), gridspec_kw={"width_ratios": [1.45, 1], "wspace": 0.32})
    for ax in (a1, a2):
        ax.axvspan(2.0, 2.5, color="#efeeea", zorder=0, linewidth=0)
    for key, col, lab, mk, ls in [("total", TOT, "Δ total", "o", "-"), ("female", FEM, "Δ women", "s", "-"),
                                  ("male", MAL, "Δ men", "^", "-"), ("gap", GAP, "Δ gap (W − M)", "D", (0, (4, 2)))]:
        m, s = df[f"diff_{key}_mean"].values, df[f"diff_{key}_std"].values
        a1.fill_between(x, m - s, m + s, color=col, alpha=0.12, linewidth=0)
        a1.plot(x, m, color=col, lw=1.3, ls=ls, marker=mk, markersize=3.6, label=lab)
    a1.axhline(0, color=INK2, lw=0.6)
    a1.set_xticks(x); a1.set_xlabel("Sanction intensity multiplier")
    a1.set_ylabel("Change vs. A (p.p.)"); a1.set_ylim(-62, 48)
    a1.set_title("(a) Informality and gap"); grid(a1)
    h, l = a1.get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, 1.07), ncol=4, handlelength=2.2, columnspacing=1.4)
    a1.text(2.25, 47, "regime\nshift", ha="center", va="top", fontsize=7, color=INK2, style="italic")
    e, es = df["exit_rate_mean"].values, df["exit_rate_std"].values
    a2.bar(x, e, 0.32, yerr=es, color="#8f8e88", error_kw=dict(elinewidth=0.6, capsize=2, ecolor=INK))
    for xi, v in zip(x, e):
        a2.text(xi, v + (es[list(x).index(xi)]) + 1.0, f"{v:.1f}" if v >= 0.05 else "0.0", ha="center", fontsize=6.9)
    a2.set_xticks(x); a2.set_xlabel("Sanction intensity multiplier")
    a2.set_ylabel("Annual firm closures (%)"); a2.set_ylim(0, 45)
    a2.set_title("(b) Annual firm closures"); grid(a2)
    save(fig, "figura5_barrido_sancion")


# ---------------------------------------------------------------- Figura 6
def fig6():
    x = np.arange(5); w = 0.26
    vals = {k: [mean_sd(s, k) for s in SC] for k in ("fem", "male", "total")}
    fig, ax = plt.subplots(figsize=(WIDTH, 2.75))
    ek = dict(elinewidth=0.6, capsize=2, ecolor=INK)
    ax.bar(x - w - 0.02, [v[0] for v in vals["fem"]], w, yerr=[v[1] for v in vals["fem"]], color=FEM, label="Mujeres", error_kw=ek)
    ax.bar(x, [v[0] for v in vals["male"]], w, yerr=[v[1] for v in vals["male"]], color=MAL, label="Hombres", error_kw=ek)
    ax.bar(x + w + 0.02, [v[0] for v in vals["total"]], w, yerr=[v[1] for v in vals["total"]], color=TOT, label="Total", error_kw=ek)
    for i, s in enumerate(SC):
        gap = mean_sd(s, "gap")[0]
        top = max(vals["fem"][i][0] + vals["fem"][i][1], vals["male"][i][0] + vals["male"][i][1], vals["total"][i][0] + vals["total"][i][1])
        ax.text(x[i], top + 2.0, f"brecha {gap:+.2f} p.p.", ha="center", va="bottom", fontsize=7.4, color=INK)
    ax.set_xticks(x); ax.set_xticklabels([l.replace("D:\n", "D: ").replace("A: statu\n", "A: statu ") for l in SCLAB], fontsize=7.8)
    ax.set_ylabel("Informality rate (%)"); ax.set_ylim(0, 108); ax.set_yticks([0, 20, 40, 60, 80, 100])
    grid(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.12), ncol=3)
    save(fig, "figura6_escenarios")
    return vals


if __name__ == "__main__":
    # Figuras del artículo (versión de 10 páginas): 1 = arquitectura, 2 = barrido de sanción,
    # 3 = resultados por sexo del dueño, 4 = trayectorias mensuales
    fig2(); fig5(); fig4(); fig3()
    print("Figuras guardadas en", OUT)
