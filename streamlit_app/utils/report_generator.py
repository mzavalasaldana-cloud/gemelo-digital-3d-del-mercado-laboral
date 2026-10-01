"""
Report and Brief Export Generator for Labor Market Digital Twin.
Generates PDF (ReportLab), Excel (openpyxl), HTML, CSV and JSON.
"""

import io
import json
import pandas as pd
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(
    country_name: str,
    scenario_name: str,
    metrics: Dict[str, Any],
    policy_params: Dict[str, float]
) -> bytes:
    """Generates a styled executive policy brief in PDF format."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=8,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#475569"),
        spaceAfter=16,
    )
    heading2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=12,
        spaceAfter=8,
    )
    body_style = styles["BodyText"]

    # Header
    story.append(Paragraph("INFORME EJECUTIVO DE POLÍTICA LABORAL Y FORMALIZACIÓN", title_style))
    story.append(Paragraph(f"Gemelo Digital 3D | País: <b>{country_name}</b> | Escenario: <b>{scenario_name}</b> | Horizonte: 10 Años", subtitle_style))
    story.append(Spacer(1, 10))

    # Summary Paragraph
    summary_text = (
        f"El presente informe sintetiza los resultados de la simulación micro-económica basada en agentes. "
        f"Bajo las intervenciones parametrizadas, la tasa de informalidad proyectada alcanza el <b>{metrics.get('informalityRate', 0)}%</b> "
        f"con un Índice de Gini de <b>{metrics.get('giniIndex', 0)}</b> y un Índice de Trabajo Decente OIT de <b>{metrics.get('decentWorkIndex', 0)}/100</b>."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 14))

    # Metrics Table
    story.append(Paragraph("1. Indicadores Estructurales del Mercado Laboral", heading2_style))
    metrics_data = [
        ["Indicador Macroeconómico", "Valor Simulado", "Impacto vs Línea Base"],
        ["Tasa de Informalidad Laboral", f"{metrics.get('informalityRate', 0)}%", "Favorable (Reducción)"],
        ["Índice de Concentración de Gini", f"{metrics.get('giniIndex', 0)}", "Mayor Equidad Salarial"],
        ["Índice de Trabajo Decente OIT", f"{metrics.get('decentWorkIndex', 0)} / 100", "Alineado con ODS 8"],
        ["Salario Promedio Formal (USD/día)", f"${metrics.get('avgFormalWageUSD', 0)}", "+ Habilidades y Productividad"],
        ["Salario Promedio Informal (USD/día)", f"${metrics.get('avgInformalWageUSD', 0)}", "+ Red de Apoyo PYME"],
        ["Ingresos Fiscales Proyectados", f"${metrics.get('fiscalRevenueMillionUSD', 0)}M USD", "Sostenibilidad Tributaria"],
        ["Costo de Implementación del Paquete", f"${metrics.get('policyCostMillionUSD', 0)}M USD", "Inversión Pública"],
        ["Balance Fiscal Neto", f"${metrics.get('netFiscalBalanceMillionUSD', 0)}M USD", "Superávit / Déficit Controlado"],
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
    story.append(Paragraph("2. Paquete de Políticas Públicas Aplicado", heading2_style))
    policies_data = [
        ["Palanca de Reforma", "Intensidad / Nivel", "Mecanismo de Transmisión"],
        ["Reducción de Costos de Registro", f"{policy_params.get('registrationCostReduction', 0)}%", "Disminuye barrera de entrada a formalidad"],
        ["Subsidio Salarial Directo a PYMEs", f"${policy_params.get('smeSubsidyUSDMonth', 0)} USD/mes", "Fomenta absorción de empleo formal"],
        ["Cobertura de Formación y Habilidades", f"{policy_params.get('skillsTrainingCoverage', 0)}%", "Aumenta productividad laboral marginal"],
        ["Inspección Laboral Inteligente", f"{policy_params.get('smartInspectionCoverage', 0)}%", "Detección no punitiva y regularización"],
        ["Tasa de Contribución Social", f"{policy_params.get('socialProtectionTax', 0)}%", "Financiamiento de cobertura solidaria"],
    ]
    t2 = Table(policies_data, colWidths=[200, 120, 220])
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
    policy_params: Dict[str, float],
    microdata_sample: pd.DataFrame
) -> bytes:
    """Generates multi-sheet Excel file with summary, metrics, and microdata."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        # Sheet 1: Resumen
        summary_df = pd.DataFrame([
            {"Parámetro": "País Analizado", "Valor": country_name},
            {"Parámetro": "Tasa de Informalidad Proyectada", "Valor": f"{metrics.get('informalityRate')}%"},
            {"Parámetro": "Índice de Gini", "Valor": metrics.get("giniIndex")},
            {"Parámetro": "Índice de Trabajo Decente", "Valor": f"{metrics.get('decentWorkIndex')}/100"},
            {"Parámetro": "Trabajadores Formales", "Valor": metrics.get("formalWorkersCount")},
            {"Parámetro": "Trabajadores Informales", "Valor": metrics.get("informalWorkersCount")},
            {"Parámetro": "Salario Formal Promedio (USD)", "Valor": metrics.get("avgFormalWageUSD")},
            {"Parámetro": "Salario Informal Promedio (USD)", "Valor": metrics.get("avgInformalWageUSD")},
            {"Parámetro": "Ingresos Fiscales ($M)", "Valor": metrics.get("fiscalRevenueMillionUSD")},
            {"Parámetro": "Costo de Políticas ($M)", "Valor": metrics.get("policyCostMillionUSD")},
            {"Parámetro": "Balance Fiscal Neto ($M)", "Valor": metrics.get("netFiscalBalanceMillionUSD")},
        ])
        summary_df.to_excel(writer, sheet_name="Resumen Ejecutivo", index=False)

        # Sheet 2: Políticas
        policies_df = pd.DataFrame([
            {"Palanca de Política": k, "Valor Configurado": v} for k, v in policy_params.items()
        ])
        policies_df.to_excel(writer, sheet_name="Parámetros Políticas", index=False)

        # Sheet 3: Microdatos
        if microdata_sample is not None and not microdata_sample.empty:
            microdata_sample.head(500).to_excel(writer, sheet_name="Muestra Microdatos", index=False)

    return buffer.getvalue()


def generate_html_report(
    country_name: str,
    scenario_name: str,
    metrics: Dict[str, Any],
    policy_params: Dict[str, float]
) -> str:
    """Generates standalone interactive HTML brief."""
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
        <p>Informe Ejecutivo: <strong>{country_name}</strong> | Escenario: <strong>{scenario_name}</strong></p>
        
        <div class="grid">
            <div class="card">
                <div class="card-label">Informalidad Laboral</div>
                <div class="card-val">{metrics.get('informalityRate')}%</div>
            </div>
            <div class="card">
                <div class="card-label">Índice de Gini</div>
                <div class="card-val">{metrics.get('giniIndex')}</div>
            </div>
            <div class="card">
                <div class="card-label">Trabajo Decente OIT</div>
                <div class="card-val">{metrics.get('decentWorkIndex')}/100</div>
            </div>
        </div>

        <h3>Paquete de Políticas Simulado</h3>
        <table>
            <tr><th>Palanca</th><th>Valor</th></tr>
            <tr><td>Reducción Costos Registro</td><td>{policy_params.get('registrationCostReduction')}%</td></tr>
            <tr><td>Subsidio PYMEs USD/mes</td><td>${policy_params.get('smeSubsidyUSDMonth')} USD</td></tr>
            <tr><td>Cobertura Habilidades</td><td>{policy_params.get('skillsTrainingCoverage')}%</td></tr>
            <tr><td>Inspección Inteligente</td><td>{policy_params.get('smartInspectionCoverage')}%</td></tr>
            <tr><td>Tasa Protección Social</td><td>{policy_params.get('socialProtectionTax')}%</td></tr>
        </table>
    </div>
</body>
</html>"""
    return html
