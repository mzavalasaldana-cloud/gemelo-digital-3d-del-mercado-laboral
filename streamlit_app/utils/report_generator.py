"""
Report and Brief Export Generator for Labor Market Digital Twin.
Generates PDF (ReportLab), Excel (openpyxl), HTML, CSV and JSON.
All scenario parameters and policy instruments are derived directly from
itdt.parameters.FixedParameters and itdt.model.ITDTModel.step logic.
"""

import io
import pandas as pd
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter  # type: ignore
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle  # type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore
from reportlab.lib import colors  # type: ignore
from itdt.parameters import FixedParameters


def build_scenario_instruments(scenario_key: str = "A") -> Dict[str, Any]:
    """
    Genera dinámicamente la tabla de instrumentos a partir de itdt.parameters.FixedParameters
    y de la lógica de política de itdt.model.ITDTModel.step.
    """
    p = FixedParameters()
    sc = str(scenario_key).upper().strip()
    if sc in ("BASELINE", "STATUS_QUO"):
        sc = "A"
    elif sc.startswith("ESCENARIO "):
        sc = sc.replace("ESCENARIO ", "").strip()

    if sc == "B1":
        kappa_val = p.kappa * 2.5
        d_growth_val = p.D_sys_growth * 3.0
        phi_1_val = p.phi_1 * 1.5
        mu_mult = 1.0
        care_mult = 1.0
        beta_val = p.beta * 1.0
        dcc_sub_str = "Sin subsidio"
        name = "GovTech Moderado"
        desc = "Sensibilidad de auditoría y cobertura digital aumentadas; facturación electrónica obligatoria (sanciones sin cambio)."
    elif sc == "B2":
        kappa_val = p.kappa * 2.5
        d_growth_val = p.D_sys_growth * 3.0
        phi_1_val = p.phi_1 * 1.5
        mu_mult = 3.0
        care_mult = 1.0
        beta_val = p.beta * 1.0
        dcc_sub_str = "Sin subsidio"
        name = "GovTech Intensivo"
        desc = "GovTech B1 complementado con sanciones por informalidad triplicadas (μ0 y μ1 × 3)."
    elif sc == "C":
        kappa_val = p.kappa * 1.0
        d_growth_val = p.D_sys_growth * 1.0
        phi_1_val = p.phi_1 * 1.0
        mu_mult = 1.0
        care_mult = 0.40
        beta_val = p.beta * 1.0
        dcc_sub_str = "Sin subsidio"
        name = "Cuidado Infantil / Corresponsabilidad"
        desc = "Reducción del 60% en horas de cuidado no remunerado de las mujeres (H_care × 0.40); resto como A."
    elif sc == "D":
        kappa_val = p.kappa * 2.5
        d_growth_val = p.D_sys_growth * 3.0
        phi_1_val = p.phi_1 * 1.5
        mu_mult = 3.0
        care_mult = 0.40
        beta_val = p.beta * 1.5
        dcc_sub_str = "Subsidio del 80% (L ≤ 10)"
        name = "Paquete Integral (GovTech + Cuidado + Subsidio DCC)"
        desc = "B2 + C + subsidio del 80% al DCC para empresas con L ≤ 10 + valoración de protección social β × 1.5."
    else:
        sc = "A"
        kappa_val = p.kappa * 1.0
        d_growth_val = p.D_sys_growth * 1.0
        phi_1_val = p.phi_1 * 1.0
        mu_mult = 1.0
        care_mult = 1.0
        beta_val = p.beta * 1.0
        dcc_sub_str = "Sin subsidio"
        name = "Status Quo (Línea Base)"
        desc = "Trayectoria base sin reformas de digitalización acelerada ni transferencias de cuidado."

    # Instrumentos según los 6 ejes canónicos de ITDT
    instruments = [
        (
            "Sensibilidad de probabilidad de auditoría (κ)",
            f"{kappa_val:.2f} ({'×2.5' if sc in ('B1', 'B2', 'D') else 'Base'})",
            "Sensibilidad logística de detección fiscal ante el tamaño relativo de la empresa",
        ),
        (
            "Crecimiento mensual de cobertura digital (D_sys)",
            f"{d_growth_val:.4f}/mes ({'×3 (0.45 p.p./mes)' if sc in ('B1', 'B2', 'D') else 'Base 0.0015/mes'})",
            "Velocidad de penetración de sistemas digitales y facturación",
        ),
        (
            "Costo cumplimiento digital regresivo (φ1)",
            f"{phi_1_val:.2f} ({'×1.5 (Fact. Electrónica)' if sc in ('B1', 'B2', 'D') else 'Base 0.30'})",
            "Componente regresivo del costo digital de cumplimiento (DCC)",
        ),
        (
            "Sanciones por informalidad (μ0, μ1)",
            f"{'×3.0 (Triplicadas)' if mu_mult > 1.0 else 'Sin cambio (Base)'}",
            f"Sanción base ({p.mu_0 * mu_mult:.2f}) y no lineal ({p.mu_1 * mu_mult:.3f}) ante auditoría",
        ),
        (
            "Horas de cuidado de las MUJERES (H_care)",
            f"{'×0.40 (−60%)' if care_mult < 1.0 else 'Sin cambio (Base)'}",
            "Carga de trabajo de cuidado no remunerado asignada a mujeres",
        ),
        (
            "Subsidio al DCC de microempresas",
            dcc_sub_str,
            "Alivio al costo digital para empresas con demanda laboral L ≤ 10",
        ),
        (
            "Valor de la protección social (β)",
            f"{beta_val:.3f} ({'×1.5' if sc == 'D' else 'Base 0.25'})",
            "Utilidad subjetiva percibida por formalidad laboral",
        ),
    ]

    return {
        "scenario": sc,
        "name": name,
        "description": desc,
        "instruments": instruments,
        "params": {
            "kappa": kappa_val,
            "d_growth": d_growth_val,
            "phi_1": phi_1_val,
            "mu_0": p.mu_0 * mu_mult,
            "mu_1": p.mu_1 * mu_mult,
            "mu_mult": mu_mult,
            "care_mult": care_mult,
            "beta": beta_val,
            "dcc_subsidy": sc == "D",
        },
    }


SCENARIO_INSTRUMENTS: Dict[str, Dict[str, Any]] = {
    sc: build_scenario_instruments(sc) for sc in ("A", "B1", "B2", "C", "D")
}


def _resolve_scenario_info(scenario_name: str, policy_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    sc = ""
    if policy_params and "scenario" in policy_params:
        sc = str(policy_params["scenario"]).upper().strip()
    if not sc and scenario_name:
        sc = scenario_name.upper().strip()
    if sc in ("BASELINE", "STATUS_QUO"):
        sc = "A"
    elif sc.startswith("ESCENARIO "):
        sc = sc.replace("ESCENARIO ", "").strip()
    return build_scenario_instruments(sc)


def generate_pdf_report(
    country_name: str,
    scenario_name: str,
    metrics: Dict[str, Any],
    policy_params: Dict[str, Any]
) -> bytes:
    """Generates a styled executive policy brief in PDF format."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story: List[Any] = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),  # type: ignore
        spaceAfter=8,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#475569"),  # type: ignore
        spaceAfter=16,
    )
    heading2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1e293b"),  # type: ignore
        spaceBefore=12,
        spaceAfter=8,
    )
    body_style = styles["BodyText"]

    # Header
    sc_info = _resolve_scenario_info(scenario_name, policy_params)
    story.append(Paragraph("INFORME EJECUTIVO DE POLÍTICA LABORAL Y FORMALIZACIÓN", title_style))
    story.append(Paragraph(f"Gemelo Digital 3D | País: <b>{country_name}</b> | Escenario: <b>{sc_info['name']}</b> | Horizonte: 10 Años", subtitle_style))
    story.append(Spacer(1, 10))

    # Summary Paragraph
    inf_str = f"{metrics['informalityRate']}%" if metrics.get('informalityRate') is not None else "Sin dato"
    gini_str = f"{metrics['giniIndex']}" if metrics.get('giniIndex') is not None else "Sin dato"
    rev_str = f"{metrics['fiscalRevenueModelUnits']:,.1f} u.m." if metrics.get('fiscalRevenueModelUnits') is not None else "Sin dato"
    exit_str = f"{metrics['annualExitRate']:.1f}%" if metrics.get('annualExitRate') is not None else "Sin dato"
    fem_str = f"{metrics['informalityFemale']}%" if metrics.get('informalityFemale') is not None else "Sin dato"
    male_str = f"{metrics['informalityMale']}%" if metrics.get('informalityMale') is not None else "Sin dato"
    gap_str = f"{metrics['genderGap']:+.2f} pp" if metrics.get('genderGap') is not None else "Sin dato"

    summary_text = (
        f"El presente informe sintetiza los resultados de la simulación macroeconómica del modelo ITDT. "
        f"Bajo las intervenciones parametrizadas, la tasa de informalidad proyectada alcanza el <b>{inf_str}</b> "
        f"con un Índice de Gini de <b>{gini_str}</b>."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 14))

    # Metrics Table
    story.append(Paragraph("1. Indicadores Estructurales del Mercado Laboral", heading2_style))
    metrics_data = [
        ["Indicador Macroeconómico", "Valor Simulado", "Impacto vs Línea Base"],
        ["Tasa de Informalidad Laboral", inf_str, "Favorable (Reducción)"],
        ["Informalidad Femenina", fem_str, "Desagregación por Sexo"],
        ["Informalidad Masculina", male_str, "Desagregación por Sexo"],
        ["Brecha de Género", gap_str, "Equidad de Género"],
        ["Índice de Concentración de Gini", gini_str, "Mayor Equidad Salarial"],
        ["Recaudación Fiscal (Unidades Modelo)", rev_str, "Sostenibilidad Tributaria ITDT"],
        ["Tasa Anual de Quiebra Empresarial", exit_str, "Fragilidad Estructural"],
    ]
    t1 = Table(metrics_data, colWidths=[240, 140, 160])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t1)
    story.append(Spacer(1, 14))

    # Policy Levers Table
    story.append(Paragraph(f"2. Parámetros del Escenario: {sc_info['name']}", heading2_style))
    story.append(Paragraph(sc_info["description"], body_style))
    story.append(Spacer(1, 6))

    policies_data = [["Instrumento de Política (ITDT)", "Intensidad / Parámetro Real", "Mecanismo de Transmisión"]]
    for inst, val, mec in sc_info["instruments"]:
        policies_data.append([inst, val, mec])

    t2 = Table(policies_data, colWidths=[200, 130, 210])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f9ff')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bae6fd')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    story.append(t2)
    story.append(Spacer(1, 14))

    # Policy Recommendations
    story.append(Paragraph("3. Recomendaciones Estratégicas OIT / Banco Mundial", heading2_style))
    rec_text = (
        "1. <b>Ventanilla Única Digital Móvil:</b> Priorizar la reducción de costos y tiempos de tramitación administrativa mediante canales digitales interoperables.<br/>"
        "2. <b>Gradualidad en la Tributación:</b> Implementar regímenes simplificados tipo Monotributo para microempresas informales durante los primeros 36 meses.<br/>"
        "3. <b>Certificación de Competencias:</b> Escalar el reconocimiento de aprendizajes previos para aumentar la empleabilidad de jóvenes y mujeres autoempleadas."
    )
    story.append(Paragraph(rec_text, body_style))

    doc.build(story)
    return buffer.getvalue()


def generate_excel_report(
    country_name: str,
    metrics: Dict[str, Any],
    policy_params: Dict[str, Any],
    microdata_sample: Optional[pd.DataFrame] = None
) -> bytes:
    """Generates multi-sheet Excel file with summary, metrics, and microdata."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        # Sheet 1: Resumen
        summary_df = pd.DataFrame([
            {"Parámetro": "País Analizado", "Valor": country_name},
            {"Parámetro": "Tasa de Informalidad Proyectada", "Valor": f"{metrics.get('informalityRate')}%"},
            {"Parámetro": "Informalidad Femenina", "Valor": f"{metrics.get('informalityFemale')}%"},
            {"Parámetro": "Informalidad Masculina", "Valor": f"{metrics.get('informalityMale')}%"},
            {"Parámetro": "Brecha de Género (pp)", "Valor": f"{metrics.get('genderGap')}"},
            {"Parámetro": "Índice de Gini", "Valor": metrics.get("giniIndex")},
            {"Parámetro": "Trabajadores Formales", "Valor": metrics.get("formalWorkersCount")},
            {"Parámetro": "Trabajadores Informales", "Valor": metrics.get("informalWorkersCount")},
            {"Parámetro": "Recaudación Fiscal (Unidades del Modelo)", "Valor": metrics.get("fiscalRevenueModelUnits", metrics.get("fiscalRevenueMillionUSD"))},
            {"Parámetro": "Tasa Anual de Quiebra (%)", "Valor": metrics.get("annualExitRate")},
            {"Parámetro": "Fuente Oficial", "Valor": "Modelo ITDT calibrado / ILOSTAT"},
        ])
        summary_df.to_excel(writer, sheet_name="Resumen Ejecutivo", index=False)

        # Sheet 2: Políticas reales del escenario
        sc_info = _resolve_scenario_info(policy_params.get("scenario", "A"), policy_params)
        policies_df = pd.DataFrame([
            {"Instrumento ITDT": inst, "Parámetro Real": val, "Mecanismo": mec}
            for inst, val, mec in sc_info["instruments"]
        ])
        policies_df.to_excel(writer, sheet_name="Instrumentos Escenario", index=False)

        # Sheet 3: Microdatos
        if microdata_sample is not None and not microdata_sample.empty:
            microdata_sample.head(500).to_excel(writer, sheet_name="Muestra Microdatos", index=False)

    return buffer.getvalue()


def generate_html_report(
    country_name: str,
    scenario_name: str,
    metrics: Dict[str, Any],
    policy_params: Dict[str, Any]
) -> str:
    """Generates standalone interactive HTML brief."""
    sc_info = _resolve_scenario_info(scenario_name, policy_params)
    table_rows = "".join(
        f"<tr><td>{inst}</td><td><strong>{val}</strong></td><td>{mec}</td></tr>"
        for inst, val, mec in sc_info["instruments"]
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Informe de Simulación: {country_name} | Gemelo Digital 3D</title>
    <style>
        body {{ font-family: 'Inter', -apple-system, sans-serif; background: #f8fafc; color: #0f172a; padding: 40px; margin: 0; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #ffffff; padding: 36px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
        h1 {{ color: #0284c7; margin-top: 0; font-size: 1.8rem; }}
        p {{ color: #475569; }}
        .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 24px 0; }}
        .card {{ background: #f8fafc; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; border-left: 4px solid #0284c7; }}
        .card-label {{ font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: 600; }}
        .card-val {{ font-size: 24px; font-weight: 800; color: #0f172a; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
        th {{ background: #f1f5f9; color: #0f172a; font-weight: 700; }}
        tr:hover {{ background-color: #f8fafc; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Gemelo Digital 3D del Mercado Laboral</h1>
        <p>Informe Ejecutivo: <strong>{country_name}</strong> | Escenario: <strong>{sc_info['name']}</strong></p>
        
        <div class="grid">
            <div class="card">
                <div class="card-label">Informalidad Laboral</div>
                <div class="card-val">{f"{metrics['informalityRate']}%" if metrics.get('informalityRate') is not None else "Sin dato"}</div>
            </div>
            <div class="card">
                <div class="card-label">Índice de Gini</div>
                <div class="card-val">{metrics.get('giniIndex') if metrics.get('giniIndex') is not None else "Sin dato"}</div>
            </div>
            <div class="card">
                <div class="card-label">Brecha de Género</div>
                <div class="card-val">{f"{metrics['genderGap']:+.2f} pp" if metrics.get('genderGap') is not None else "Sin dato"}</div>
            </div>
        </div>

        <h3>Parámetros Reales del Escenario: {sc_info['name']}</h3>
        <p>{sc_info['description']}</p>
        <table>
            <tr><th>Instrumento de Política (ITDT)</th><th>Parámetro Real</th><th>Mecanismo de Transmisión</th></tr>
            {table_rows}
        </table>
    </div>
</body>
</html>"""
    return html
