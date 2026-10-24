#!/usr/bin/env python3
"""
scripts/generar_figuras_articulo.py

Generador de figuras de alta fidelidad para el artículo académico (Revista CRORR):
- Fig. 2. Arquitectura de ITDT (diagrama vectorial, ancho final 120 mm).
- Fig. 5. Barrido de la intensidad de sanción (ancho final 145 mm, alto 80 mm).
- Fig. 6. Informalidad por escenario y sexo (meses 109–120) (ancho final 145 mm, alto 75 mm).

Requisitos editoriales:
- Tipografía mínima impresa: 8 pt para etiquetas, leyendas y marcas de ejes; 9 pt para títulos de ejes.
- Sin título dentro del gráfico (el título va en el pie de figura de la revista).
- Todo en español con terminología exacta ("statu quo", "Brecha (M − H)").
- Distinguible en blanco y negro (marcadores, tramas de sombreado y estilos de línea distintos).
- Exportación dual: PNG a 600 dpi exactamente a la escala requerida y PDF vectorial.
"""

import os
import sys
import re
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from PIL import Image

# Configurar backend sin interfaz gráfica
matplotlib.use("Agg")

# Configuración tipográfica uniforme: Arial o DejaVu Sans
matplotlib.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Helvetica"]
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["mathtext.fontset"] = "dejavusans"
matplotlib.rcParams["axes.edgecolor"] = "#2c3e50"
matplotlib.rcParams["axes.linewidth"] = 0.8
matplotlib.rcParams["grid.color"] = "#e5e8e8"
matplotlib.rcParams["grid.linestyle"] = ":"
matplotlib.rcParams["grid.linewidth"] = 0.6

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "figuras_articulo")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==============================================================================
# FIGURA 2: ARQUITECTURA DE ITDT (DIAGRAMA VECTORIAL)
# ==============================================================================

def generar_figura_2():
    """
    Genera Fig. 2 (Arquitectura de ITDT).
    Ancho final: 120 mm (4.724 pulg), Alto: 92 mm (3.622 pulg).
    A 600 dpi: exactamente 2835 x 2173 px.
    Tipografía: 10 pt negrita en títulos de bloques, 9 pt en cuerpo, >= 8.5 pt en flechas.
    """
    print("[*] Generando Fig. 2: Arquitectura de ITDT...")
    w_in = 120.0 / 25.4
    h_in = 92.0 / 25.4

    fig, ax = plt.subplots(figsize=(w_in, h_in), dpi=600)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Colores elegantes e institucionales
    c_gov_bg = "#f4f6f9"
    c_gov_edge = "#1a365d"
    c_gov_hdr = "#1a365d"

    c_wrk_bg = "#fdfefe"
    c_wrk_edge = "#78281f"
    c_wrk_hdr = "#78281f"

    c_frm_bg = "#f8f9fa"
    c_frm_edge = "#1b4f72"
    c_frm_hdr = "#1b4f72"

    # 1. BLOQUE SUPERIOR: ESTADO / GOBIERNO
    # Coordenadas: [x=6, y=66, w=88, h=30]
    gov_box = FancyBboxPatch(
        (6, 66), 88, 30,
        boxstyle="round,pad=1.2,rounding_size=3.0",
        facecolor=c_gov_bg,
        edgecolor=c_gov_edge,
        linewidth=1.2,
        zorder=2
    )
    ax.add_patch(gov_box)

    ax.text(
        50, 92.5, "Estado / Gobierno ($G$)",
        ha="center", va="center",
        fontsize=10.0, fontweight="bold", color=c_gov_hdr
    )

    gov_text = (
        "• Política tributaria: alícuota fiscal $\\tau$, umbral formal $\\bar{y}$\n"
        "• Fiscalización: auditoría aleatoria $P_{\\mathrm{aud}}$, multas y sanciones $\\mu_0, \\mu_1, \\xi$\n"
        "• Modernización GovTech: subsidio al costo digital de cumplimiento (DCC)\n"
        "• Política social: red pública de cuidados (cobertura $c$ para reducir desutilidad)"
    )
    ax.text(
        9, 78.5, gov_text,
        ha="left", va="center",
        fontsize=8.8, color="#1c2833", linespacing=1.35
    )

    # 2. BLOQUE INFERIOR IZQUIERDO: TRABAJADORES
    # Coordenadas: [x=3, y=5, w=44, h=48]
    wrk_box = FancyBboxPatch(
        (3, 5), 44, 48,
        boxstyle="round,pad=1.2,rounding_size=3.0",
        facecolor=c_wrk_bg,
        edgecolor=c_wrk_edge,
        linewidth=1.2,
        zorder=2
    )
    ax.add_patch(wrk_box)

    ax.text(
        25, 49.5, "Trabajadores ($N_W = 6\\,000$)",
        ha="center", va="center",
        fontsize=10.0, fontweight="bold", color=c_wrk_hdr
    )

    wrk_text = (
        "• Estado: Formal ($F$) o Informal ($I$)\n"
        "• Elección: compara utilidades\n"
        "   $U_{i,F}$ frente a $U_{i,I}$\n"
        "• Desutilidad por cuidados:\n"
        "   carga de cuidado $H_{\\mathrm{care},i}$\n"
        "• Heterogeneidad individual:\n"
        "   educación y productividad $h_i$\n"
        "• Adopción tecnológica:\n"
        "   alfabetización digital $K_{\\mathrm{dig},i}$"
    )
    ax.text(
        5.5, 26.5, wrk_text,
        ha="left", va="center",
        fontsize=8.5, color="#1c2833", linespacing=1.32
    )

    # 3. BLOQUE INFERIOR DERECHO: EMPRESAS
    # Coordenadas: [x=53, y=5, w=44, h=48]
    frm_box = FancyBboxPatch(
        (53, 5), 44, 48,
        boxstyle="round,pad=1.2,rounding_size=3.0",
        facecolor=c_frm_bg,
        edgecolor=c_frm_edge,
        linewidth=1.2,
        zorder=2
    )
    ax.add_patch(frm_box)

    ax.text(
        75, 49.5, "Empresas ($N_F = 600$)",
        ha="center", va="center",
        fontsize=10.0, fontweight="bold", color=c_frm_hdr
    )

    frm_text = (
        "• Estado: Formal ($F$) o Informal ($I$)\n"
        "• Elección: compara beneficios\n"
        "   $\\Pi_{j,F}$ frente a $\\Pi_{j,I}$\n"
        "• Cumplimiento: costo digital\n"
        "   $\\mathrm{DCC}_j$ y riesgo de auditoría $P_{\\mathrm{aud},j}$\n"
        "• Dinámica: revisión de estado con\n"
        "   regla de Metropolis ($T_k = T_0 d^k$)\n"
        "• Quiebra si $\\Pi_j < 0$ y entrada libre"
    )
    ax.text(
        55.5, 26.5, frm_text,
        ha="left", va="center",
        fontsize=8.5, color="#1c2833", linespacing=1.32
    )

    # 4. CONECTORES Y FLUJOS
    arrow_kw = dict(arrowstyle="-|>", mutation_scale=11, linewidth=1.1, color="#2c3e50", zorder=3)

    # Flecha Estado -> Trabajadores
    arr_g_w = FancyArrowPatch((26, 66), (26, 53), connectionstyle="arc3,rad=0.0", **arrow_kw)
    ax.add_patch(arr_g_w)
    ax.text(
        27.5, 59.5, "Red de cuidados\n(reduce $H_{\\mathrm{care}}$)",
        ha="left", va="center", fontsize=8.2, color="#566573", fontweight="semibold"
    )

    # Flecha Estado -> Empresas
    arr_g_f = FancyArrowPatch((74, 66), (74, 53), connectionstyle="arc3,rad=0.0", **arrow_kw)
    ax.add_patch(arr_g_f)
    ax.text(
        72.5, 59.5, "Impuestos $\\tau$, fiscalización,\nsubsidio DCC",
        ha="right", va="center", fontsize=8.2, color="#566573", fontweight="semibold"
    )

    # Flecha bidireccional Trabajadores <-> Empresas (Mercado Laboral)
    arr_lr = FancyArrowPatch(
        (47, 28), (53, 28),
        arrowstyle="<|-|>", mutation_scale=11, linewidth=1.2, color="#1a5276", zorder=3
    )
    ax.add_patch(arr_lr)

    badge_market = FancyBboxPatch(
        (37, 20), 26, 12,
        boxstyle="round,pad=0.8,rounding_size=2.0",
        facecolor="#ebf5fb",
        edgecolor="#2980b9",
        linewidth=0.9,
        zorder=4
    )
    ax.add_patch(badge_market)
    ax.text(
        50, 26, "Vacantes formales\nasignadas por ranking\nde productividad",
        ha="center", va="center", fontsize=8.0, color="#1b4f72", fontweight="bold", zorder=5
    )

    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)

    png_path = os.path.join(OUTPUT_DIR, "fig2_arquitectura.png")
    pdf_path = os.path.join(OUTPUT_DIR, "fig2_arquitectura.pdf")

    fig.savefig(png_path, dpi=600)
    fig.savefig(pdf_path)
    plt.close(fig)

    # Verificar ancho exacto con PIL
    with Image.open(png_path) as im:
        print(f" -> Guardado: {png_path} ({im.size[0]} x {im.size[1]} px)")
        print(f" -> Guardado: {pdf_path}")
        assert abs(im.size[0] - 2835) <= 2, f"Ancho inesperado: {im.size[0]}"


# ==============================================================================
# FIGURA 5: BARRIDO DE LA INTENSIDAD DE SANCIÓN
# ==============================================================================

def generar_figura_5():
    """
    Genera Fig. 5 (Barrido de la intensidad de sanción).
    Ancho final: 145 mm (5.709 pulg), Alto: 80 mm (3.150 pulg).
    A 600 dpi: exactamente 3425 x 1890 px.
    Datos: outputs/sanctions_sweep_data.csv.
    Eje Y común e izquierdo: cambios frente al statu quo (p.p.).
    Eje Y derecho: cierre anual de empresas (%).
    Leyenda fuera del área de datos (abajo).
    """
    print("[*] Generando Fig. 5: Barrido de sanciones...")
    csv_path = os.path.join(BASE_DIR, "outputs", "sanctions_sweep_data.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No existe: {csv_path}")

    df = pd.read_csv(csv_path)

    w_in = 145.0 / 25.4
    h_in = 80.0 / 25.4

    fig, ax1 = plt.subplots(figsize=(w_in, h_in), dpi=600)
    ax2 = ax1.twinx()

    x = df["multiplier"].values

    # 1. EJE DERECHO: Barras de cierre anual de empresas (%)
    bar_width = 0.18
    bars = ax2.bar(
        x, df["exit_rate_mean"],
        width=bar_width,
        color="#d5dbdb",
        edgecolor="#566573",
        linewidth=0.8,
        hatch="///",
        alpha=0.85,
        label="Cierre anual de empresas (%)",
        zorder=1
    )
    ax2.set_ylabel("Cierre anual de empresas (%)", fontsize=9.2, fontweight="bold", color="#424949", labelpad=7)
    ax2.set_ylim(0.0, 50.0)
    ax2.tick_params(axis="y", labelsize=8.2, colors="#424949", width=0.8)
    ax2.grid(False)

    # 2. EJE IZQUIERDO: Líneas de cambios (p.p.)
    # Colores contrastados y distinguibles en B&W mediante marcadores y estilos
    c_tot = "#1b2631"   # Casi negro
    c_fem = "#922b21"   # Granate oscuro
    c_mal = "#1b4f72"   # Azul acero
    c_gap = "#5b2c6f"   # Púrpura oscuro

    l_tot = ax1.plot(
        x, df["diff_total_mean"],
        color=c_tot, linestyle="-", linewidth=1.7, marker="o", markersize=4.8,
        label="Δ Total", zorder=4
    )[0]
    ax1.fill_between(
        x,
        df["diff_total_mean"] - df["diff_total_std"],
        df["diff_total_mean"] + df["diff_total_std"],
        color=c_tot, alpha=0.12, zorder=2
    )

    l_fem = ax1.plot(
        x, df["diff_female_mean"],
        color=c_fem, linestyle="-", linewidth=1.7, marker="s", markersize=4.8,
        label="Δ Mujeres", zorder=4
    )[0]
    ax1.fill_between(
        x,
        df["diff_female_mean"] - df["diff_female_std"],
        df["diff_female_mean"] + df["diff_female_std"],
        color=c_fem, alpha=0.12, zorder=2
    )

    l_mal = ax1.plot(
        x, df["diff_male_mean"],
        color=c_mal, linestyle="-", linewidth=1.7, marker="^", markersize=5.0,
        label="Δ Hombres", zorder=4
    )[0]
    ax1.fill_between(
        x,
        df["diff_male_mean"] - df["diff_male_std"],
        df["diff_male_mean"] + df["diff_male_std"],
        color=c_mal, alpha=0.12, zorder=2
    )

    l_gap = ax1.plot(
        x, df["diff_gap_mean"],
        color=c_gap, linestyle="--", linewidth=1.8, marker="D", markersize=4.8,
        label="Δ Brecha (M − H)", zorder=5
    )[0]
    ax1.fill_between(
        x,
        df["diff_gap_mean"] - df["diff_gap_std"],
        df["diff_gap_mean"] + df["diff_gap_std"],
        color=c_gap, alpha=0.16, zorder=2
    )

    # Línea base en 0
    ax1.axhline(0.0, color="#7f8c8d", linestyle=":", linewidth=0.9, zorder=3)

    ax1.set_xlabel("Multiplicador de intensidad de sanciones", fontsize=9.2, fontweight="bold", labelpad=6)
    ax1.set_ylabel("Cambio frente al statu quo (p.p.)", fontsize=9.2, fontweight="bold", labelpad=6)
    ax1.set_ylim(-55.0, 42.0)
    ax1.set_xlim(0.8, 4.2)
    ax1.set_xticks([1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
    ax1.tick_params(axis="both", labelsize=8.2, width=0.8)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Leyenda combinada colocada debajo de los datos
    handles = [l_tot, l_fem, l_mal, l_gap, bars]
    labels = [h.get_label() for h in handles]

    ax1.legend(
        handles, labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=5,
        fontsize=8.0,
        frameon=True,
        facecolor="#ffffff",
        edgecolor="#bdc3c7",
        handlelength=1.6,
        columnspacing=1.0,
        handletextpad=0.5
    )

    # Ajuste manual exacto para garantizar 3425 px sin recorte
    fig.subplots_adjust(top=0.96, bottom=0.25, left=0.11, right=0.89)

    png_path = os.path.join(OUTPUT_DIR, "fig5_barrido_sanciones.png")
    pdf_path = os.path.join(OUTPUT_DIR, "fig5_barrido_sanciones.pdf")

    fig.savefig(png_path, dpi=600)
    fig.savefig(pdf_path)
    plt.close(fig)

    with Image.open(png_path) as im:
        print(f" -> Guardado: {png_path} ({im.size[0]} x {im.size[1]} px)")
        print(f" -> Guardado: {pdf_path}")
        assert abs(im.size[0] - 3425) <= 2, f"Ancho inesperado: {im.size[0]}"


# ==============================================================================
# FIGURA 6: NIVELES DE INFORMALIDAD POR ESCENARIO Y SEXO
# ==============================================================================

def parse_mean_se(val_str):
    """Parsea cadenas como '88.31 (2.27)' en (88.31, 2.27)."""
    m = re.match(r"([\d\.\-]+)\s*\(([\d\.\-]+)\)", str(val_str).strip())
    if m:
        return float(m.group(1)), float(m.group(2))
    return float(val_str), 0.0


def generar_figura_6():
    """
    Genera Fig. 6 (Informalidad por escenario y sexo, meses 109–120).
    Ancho final: 145 mm (5.709 pulg), Alto: 75 mm (2.953 pulg).
    A 600 dpi: exactamente 3425 x 1772 px.
    Datos: outputs/table5_levels.csv.
    Barras: Mujeres (M), Hombres (H), Total (T).
    Etiqueta sobre cada grupo: Brecha (M − H).
    """
    print("[*] Generando Fig. 6: Niveles por escenario...")
    csv_path = os.path.join(BASE_DIR, "outputs", "table5_levels.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No existe: {csv_path}")

    df = pd.read_csv(csv_path)

    w_in = 145.0 / 25.4
    h_in = 75.0 / 25.4

    fig, ax = plt.subplots(figsize=(w_in, h_in), dpi=600)

    scenarios = ["A", "B1", "B2", "C", "D"]
    sc_labels = [
        "A: statu quo",
        "B1: GovTech\nmoderado",
        "B2: GovTech\nintensivo",
        "C: red de\ncuidados",
        "D: integrado"
    ]

    f_means, f_ses = [], []
    m_means, m_ses = [], []
    t_means, t_ses = [], []
    gaps = []

    for idx, row in df.iterrows():
        t_m, t_s = parse_mean_se(row["Informalidad total (%)"])
        f_m, f_s = parse_mean_se(row["Mujeres (%)"])
        m_m, m_s = parse_mean_se(row["Hombres (%)"])
        gap_val = float(str(row["Brecha F − M (p.p.)"]).split()[0])

        t_means.append(t_m); t_ses.append(t_s)
        f_means.append(f_m); f_ses.append(f_s)
        m_means.append(m_m); m_ses.append(m_s)
        gaps.append(gap_val)

    x = np.arange(len(scenarios))
    bar_width = 0.25

    # Estilos contrastados para B&W
    color_fem = "#922b21"
    color_male = "#1f618d"
    color_tot = "#2c3e50"

    err_kw = dict(capsize=2.5, capthick=0.8, elinewidth=0.8, ecolor="#1a252f")

    b_fem = ax.bar(
        x - bar_width, f_means, bar_width,
        yerr=f_ses, error_kw=err_kw,
        color=color_fem, edgecolor="#641e16", linewidth=0.7,
        hatch="///", alpha=0.90, label="Mujeres (M)", zorder=3
    )

    b_male = ax.bar(
        x, m_means, bar_width,
        yerr=m_ses, error_kw=err_kw,
        color=color_male, edgecolor="#154360", linewidth=0.7,
        hatch="\\\\\\", alpha=0.90, label="Hombres (H)", zorder=3
    )

    b_tot = ax.bar(
        x + bar_width, t_means, bar_width,
        yerr=t_ses, error_kw=err_kw,
        color=color_tot, edgecolor="#17202a", linewidth=0.7,
        hatch="..", alpha=0.90, label="Total (T)", zorder=3
    )

    # Etiquetas de brecha (M − H) en recuadro destacado
    for i in range(len(scenarios)):
        top_y = max(f_means[i], m_means[i], t_means[i])
        gap = gaps[i]
        ax.annotate(
            f"Brecha (M − H)\n{gap:+.1f} p.p.",
            xy=(x[i], top_y + 3.2),
            ha="center", va="bottom",
            fontsize=8.0, fontweight="bold",
            color="#1c2833",
            bbox=dict(boxstyle="round,pad=0.25,rounding_size=1.5", fc="#f8f9f9", ec="#a6acaf", linewidth=0.7),
            zorder=5
        )

    ax.set_ylabel("Tasa de informalidad (%)", fontsize=9.2, fontweight="bold", labelpad=6)
    ax.set_ylim(20.0, 114.0)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_xticks(x)
    ax.set_xticklabels(sc_labels, fontsize=8.4, fontweight="bold")
    ax.tick_params(axis="both", labelsize=8.2, width=0.8)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6, zorder=0)

    ax.legend(
        loc="upper right",
        fontsize=8.2,
        frameon=True,
        facecolor="#ffffff",
        edgecolor="#bdc3c7",
        handlelength=1.4,
        handletextpad=0.4
    )

    fig.subplots_adjust(top=0.97, bottom=0.18, left=0.10, right=0.98)

    png_path = os.path.join(OUTPUT_DIR, "fig6_niveles_escenarios.png")
    pdf_path = os.path.join(OUTPUT_DIR, "fig6_niveles_escenarios.pdf")

    fig.savefig(png_path, dpi=600)
    fig.savefig(pdf_path)
    plt.close(fig)

    with Image.open(png_path) as im:
        print(f" -> Guardado: {png_path} ({im.size[0]} x {im.size[1]} px)")
        print(f" -> Guardado: {pdf_path}")
        assert abs(im.size[0] - 3425) <= 2, f"Ancho inesperado: {im.size[0]}"


if __name__ == "__main__":
    generar_figura_2()
    generar_figura_5()
    generar_figura_6()
    print("\n[+] Figuras 2, 5 y 6 generadas exitosamente en:", OUTPUT_DIR)
