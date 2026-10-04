"""
Trabajo Decente OIT & ODS 8: 10 ILO Decent Work Indicators, Gap Radar and SDG Targets.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from streamlit_app.config import t, COLORS
from streamlit_app.data.mock_data import ILO_DECENT_WORK_INDICATORS, COUNTRY_PROFILES
from streamlit_app.simulation_engine import calculate_structural_metrics
from streamlit_app.utils.ui_components import (
    render_metric_card, 
    render_section_header,
    render_explainability_card
)

def render_ilo_decent_work_view():
    """Renders the ILO Decent Work Standards & SDG 8 assessment module."""
    country_code = st.session_state.get("country", "KENYA")
    scenario = st.session_state.get("scenario", "A")
    if scenario in ("BASELINE", "STATUS_QUO"):
        scenario = "A"
    st.session_state.scenario = scenario

    month = st.session_state.get("month", 0)
    policy_params = st.session_state.get("policy_params", {})
    profile = COUNTRY_PROFILES.get(country_code, COUNTRY_PROFILES["KENYA"])
    metrics = calculate_structural_metrics(country_code, policy_params, scenario, month)
    gender_gap = metrics.get("genderGap", 0.0)

    # Header
    st.markdown(f"""
    <div style="background: rgba(11, 18, 32, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(0, 240, 255, 0.35);
                border-radius: 12px; padding: 14px 22px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h2 style="margin: 0; font-size: 1.45rem; color: #f8fafc;">
                    ⚖️ TRABAJO DECENTE OIT & OBJETIVOS DE DESARROLLO SOSTENIBLE (ODS 8)
                </h2>
                <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #94a3b8;">
                    Marco de Medición Oficial OIT &bull; 10 Dimensiones de Trabajo Decente &bull; Metas 2030
                </p>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span class="glow-badge badge-emerald">Índice Global: {metrics['decentWorkIndex']}/100 (Indicador ilustrativo, no forma parte del artículo)</span>
                <span class="glow-badge badge-cyan">{profile['flag']} {profile['name']}</span>
                <span class="glow-badge badge-purple">Escenario {scenario}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Scenario Quick Selector
    scen_cols = st.columns([2, 4])
    with scen_cols[0]:
        sc_keys = ["A", "B1", "B2", "C", "D"]
        sc_labels = {
            "A": "A: Status Quo",
            "B1": "B1: GovTech Moderado",
            "B2": "B2: GovTech Sanciones 3×",
            "C": "C: Red de Cuidados",
            "D": "D: Integrado",
        }
        sel_sc = st.selectbox(
            "Escenario Activo",
            options=sc_keys,
            format_func=lambda s: sc_labels.get(s, s),
            index=sc_keys.index(scenario) if scenario in sc_keys else 0,
            key="ilo_scenario_select"
        )
        if sel_sc != scenario:
            st.session_state.scenario = sel_sc
            st.rerun()

    # 4 Quick KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card("Cumplimiento Global OIT", f"{metrics['decentWorkIndex']}%", delta="Indicador ilustrativo, no forma parte del artículo", icon="🛡️", badge="Ilustrativo")
    with k2:
        render_metric_card("Tasa de Empleo Informal", f"{metrics['informalityRate']}%", delta="Meta OIT: 45%", delta_positive=(metrics['informalityRate'] <= 45), icon="📉")
    with k3:
        render_metric_card("Brecha Salarial / Cuidado", f"{gender_gap:+.1f} p.p.", delta="F vs M", delta_positive=(abs(gender_gap) <= 3.0), icon="🚻")
    with k4:
        formal_pct = round(100.0 - metrics['informalityRate'], 1)
        render_metric_card("Cobertura Seg. Social", f"{formal_pct}%", delta="Empleo Formal", delta_positive=True, icon="🏥")


    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    col_radar, col_table = st.columns([1.2, 1.4])

    with col_radar:
        render_section_header("Radar de Desempeño vs Meta 2030", icon="🎯", badge="10 Dimensiones")

        categories = [
            "Empleo Informal",
            "Salarios Bajos",
            "Jornadas Excesivas",
            "Seguridad Social",
            "Brecha Género",
            "Diálogo Social",
            "Jóvenes NINI",
            "Seguridad Ocupacional"
        ]

        # Derived dynamic scores for radar (0 to 100 where 100 is target achieved)
        current_scores = [
            max(20, min(100, 100 - (metrics['informalityRate'] - 45) * 1.5)),
            68,
            55,
            int(55 + (100 - metrics['informalityRate']) * 0.4),
            62,
            48,
            58,
            74,
        ]
        target_scores = [100, 100, 100, 100, 100, 100, 100, 100]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=target_scores + [target_scores[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(16, 185, 129, 0.1)',
            line=dict(color='#10b981', dash='dash', width=2),
            name='Meta ODS 8 (2030)'
        ))
        theme = st.session_state.get("theme", "light")
        radar_line_col = "#0284c7" if theme == "light" else "#00f0ff"
        radar_fill_col = "rgba(2, 132, 199, 0.2)" if theme == "light" else "rgba(0, 240, 255, 0.25)"
        radial_grid = "rgba(0, 0, 0, 0.08)" if theme == "light" else "rgba(255, 255, 255, 0.1)"
        radial_col = "#64748b" if theme == "light" else "#94a3b8"
        angular_col = "#0f172a" if theme == "light" else "#f8fafc"
        legend_col = "#0f172a" if theme == "light" else "#f8fafc"

        fig_radar.add_trace(go.Scatterpolar(
            r=current_scores + [current_scores[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor=radar_fill_col,
            line=dict(color=radar_line_col, width=3),
            name=f'Actual ({profile["name"]})'
        ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color=radial_col, gridcolor=radial_grid),
                angularaxis=dict(color=angular_col, gridcolor=radial_grid)
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(font=dict(color=legend_col, size=11), orientation="h", y=-0.15),
            margin=dict(l=30, r=30, t=20, b=40),
            height=340,
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        render_explainability_card(
            title="Explicabilidad: Radar de Cumplimiento OIT y ODS 8",
            what_it_is="Representación polar multicriterio que compara el estado del país frente al estándar 100% de cumplimiento fijado en la Agenda 2030 de la OIT.",
            how_to_read="El polígono exterior verde discontinuo es la meta perfecta (100). El polígono cian muestra el rendimiento alcanzado. Las hendiduras hacia el centro indican brechas críticas.",
            policy_impact="Permite detectar desequilibrios: países con alta formalidad pero déficit en diálogo social o seguridad ocupacional."
        )

    with col_table:
        render_section_header("Matriz de Indicadores y Brechas OIT", icon="📋", badge="Normativa")

        for ind in ILO_DECENT_WORK_INDICATORS:
            is_inf = (ind["code"] == "DW-INF")
            val = f"{metrics['informalityRate']}%" if is_inf else f"{ind['target2030'] + 12.0} {ind['unit']}"
            target = f"{ind['target2030']} {ind['unit']}"

            st.markdown(f"""
            <div class="holo-card" style="padding: 10px 14px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b style="color: #f8fafc; font-size: 0.9rem;">{ind['name']}</b>
                    <span class="glow-badge badge-cyan">{ind['category']}</span>
                </div>
                <div style="font-size: 0.82rem; color: #cbd5e1; margin-top: 4px;">
                    <b>Valor Simulado:</b> <span style="color:#00f0ff;">{val}</span> &bull; 
                    <b>Meta OIT 2030:</b> <span style="color:#10b981;">{target}</span>
                </div>
                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">
                    {ind['description']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        render_explainability_card(
            title="Explicabilidad: Matriz de los 10 Pilares de Trabajo Decente",
            what_it_is="Desglose de indicadores cuantitativos armonizados con el Manual de Conceptos y Métodos de la OIT.",
            how_to_read="Contrasta el valor corriente con la meta normativa internacional fijada para el 2030.",
            policy_impact="Base legal y estadística para la elaboración de Informes Nacionales Voluntarios (VNR) ante Naciones Unidas."
        )

