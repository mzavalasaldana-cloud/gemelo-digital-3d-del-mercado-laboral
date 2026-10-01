"""
Dashboard Principal: Macro-economic KPIs, Policy Simulation Sliders, Scenarios, Lorenz Curves,
Time-Series Projections (2015-2034), Baseline vs Intervention Comparisons, and Historical Runs.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime

from streamlit_app.config import t, COLORS
from streamlit_app.data.mock_data import COUNTRY_PROFILES, INITIAL_POLICY_STATE
from streamlit_app.simulation_engine import calculate_structural_metrics
from streamlit_app.utils.ui_components import (
    render_metric_card, 
    render_section_header, 
    play_holo_sound_js,
    render_explainability_card,
    apply_chart_theme
)

def render_dashboard_view():
    """Renders the comprehensive 2D Executive Dashboard."""
    country_code = st.session_state.get("country", "KENYA")
    scenario = st.session_state.get("scenario", "BASELINE")
    month = st.session_state.get("month", 0)
    policy_params = st.session_state.get("policy_params", INITIAL_POLICY_STATE)
    profile = COUNTRY_PROFILES.get(country_code, COUNTRY_PROFILES["KENYA"])

    # Compute live metrics
    metrics = calculate_structural_metrics(country_code, policy_params, scenario, month)
    base_inf = profile["baseInformalityRate"]
    inf_delta = round(metrics["informalityRate"] - base_inf, 1)

    # 1. Top Header Banner
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(0,240,255,0.12) 0%, rgba(15,23,42,0.85) 100%);
                padding: 16px 24px; border-radius: 12px; border-left: 4px solid #00f0ff; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <h2 style="margin: 0; font-size: 1.5rem; color: #f8fafc;">
                    {profile['flag']} {profile['name']} &mdash; Diagnóstico Macroeconómico
                </h2>
                <p style="margin: 4px 0 0 0; font-size: 0.88rem; color: #94a3b8;">
                    {profile['contextDescription']} | Población: <b>{profile['population']}</b> | Moneda: <b>{profile['currency']}</b>
                </p>
            </div>
            <div style="display: flex; gap: 8px;">
                <span class="glow-badge badge-cyan">Mes {month} (Año {2024 + month // 12})</span>
                <span class="glow-badge badge-emerald">Escenario: {scenario}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Key Performance Indicators (6 Glassmorphic KPI Cards)
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        render_metric_card(
            label="Informalidad",
            value=f"{metrics['informalityRate']}%",
            delta=f"{inf_delta}% vs Base",
            delta_positive=(inf_delta < 0),
            icon="📉",
            badge="ODS 8.3"
        )
    with c2:
        render_metric_card(
            label="Índice de Gini",
            value=f"{metrics['giniIndex']}",
            delta=f"Equidad: {round((profile['baseGini'] - metrics['giniIndex'])*100, 1)} pts",
            delta_positive=(metrics['giniIndex'] <= profile['baseGini']),
            icon="⚖️",
            badge="Gini"
        )
    with c3:
        render_metric_card(
            label="Trabajo Decente",
            value=f"{metrics['decentWorkIndex']}/100",
            delta="+ OIT Estándar",
            delta_positive=True,
            icon="🛡️",
            badge="OIT Target"
        )
    with c4:
        render_metric_card(
            label="Salario Formal",
            value=f"${metrics['avgFormalWageUSD']}",
            delta="USD/Día",
            delta_positive=True,
            icon="💼",
            badge="Formal"
        )
    with c5:
        render_metric_card(
            label="Salario Informal",
            value=f"${metrics['avgInformalWageUSD']}",
            delta="USD/Día",
            delta_positive=True,
            icon="🪙",
            badge="Informal"
        )
    with c6:
        render_metric_card(
            label="Balance Fiscal",
            value=f"${metrics['netFiscalBalanceMillionUSD']}M",
            delta=f"Ingresos: ${metrics['fiscalRevenueMillionUSD']}M",
            delta_positive=(metrics['netFiscalBalanceMillionUSD'] >= 0),
            icon="🏛️",
            badge="Net USD"
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Main Dashboard Layout: Sliders & Scenarios (Left) + Charts (Right)
    col_left, col_right = st.columns([1.1, 1.4])

    with col_left:
        render_section_header("Palancas de Política Pública", icon="🎛️", badge="Reactivo")

        # Scenario Presets Quick Selector
        preset_names = {
            "BASELINE": "📍 Línea Base (Inercial)",
            "SCENARIO_A_REGISTRATION": "🚀 Ventanilla Única Digital (-80% Costo)",
            "SCENARIO_B_WORKER_SUBSIDY": "💰 Subsidio Salarial Directo a PYMEs",
            "SCENARIO_E_AUTOMATION_SHOCK": "⚡ Shock de Automatización",
            "CUSTOM": "🛠️ Personalizado",
        }
        
        selected_scenario = st.selectbox(
            "Seleccionar Escenario Macroeconómico Predefinido",
            options=list(preset_names.keys()),
            format_func=lambda x: preset_names[x],
            index=list(preset_names.keys()).index(scenario) if scenario in preset_names else 0,
            key="dashboard_scenario_select"
        )

        if selected_scenario != scenario:
            st.session_state.scenario = selected_scenario
            if selected_scenario == "SCENARIO_A_REGISTRATION":
                st.session_state.policy_params["registrationCostReduction"] = 80.0
                st.session_state.policy_params["smeSubsidyUSDMonth"] = 40.0
            elif selected_scenario == "SCENARIO_B_WORKER_SUBSIDY":
                st.session_state.policy_params["smeSubsidyUSDMonth"] = 75.0
                st.session_state.policy_params["skillsTrainingCoverage"] = 60.0
            elif selected_scenario == "BASELINE":
                st.session_state.policy_params = dict(INITIAL_POLICY_STATE)
            play_holo_sound_js("wave")
            st.rerun()

        # Policy Levers Sliders
        reg_red = st.slider(
            "1. Reducción Costos y Trámites de Registro (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(policy_params.get("registrationCostReduction", 30.0)),
            step=5.0,
            help="Disminuye la barrera de entrada al registro formal mediante ventanilla única digital.",
            key="slider_reg"
        )
        sme_sub = st.slider(
            "2. Subsidio Salarial a Micro y PYMEs (USD/mes)",
            min_value=0.0,
            max_value=150.0,
            value=float(policy_params.get("smeSubsidyUSDMonth", 50.0)),
            step=5.0,
            help="Subsidio directo por trabajador contratado formalmente durante 24 meses.",
            key="slider_sub"
        )
        skills_cov = st.slider(
            "3. Cobertura de Capacitación y Competencias (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(policy_params.get("skillsTrainingCoverage", 25.0)),
            step=5.0,
            help="Capacitación dual para aumentar el capital humano y productividad.",
            key="slider_skills"
        )
        tax_prot = st.slider(
            "4. Tasa de Contribución a Protección Social (%)",
            min_value=0.0,
            max_value=35.0,
            value=float(policy_params.get("socialProtectionTax", 12.0)),
            step=1.0,
            help="Aporte solidario formal para pensiones y salud.",
            key="slider_tax"
        )
        smart_insp = st.slider(
            "5. Inspección Laboral Digital e Inteligente (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(policy_params.get("smartInspectionCoverage", 20.0)),
            step=5.0,
            help="Fiscalización asistida por IA para formalizar unidades económicas sin multas abusivas.",
            key="slider_insp"
        )

        # Update params if changed
        if (reg_red != policy_params.get("registrationCostReduction") or
            sme_sub != policy_params.get("smeSubsidyUSDMonth") or
            skills_cov != policy_params.get("skillsTrainingCoverage") or
            tax_prot != policy_params.get("socialProtectionTax") or
            smart_insp != policy_params.get("smartInspectionCoverage")):
            st.session_state.policy_params = {
                "registrationCostReduction": reg_red,
                "smeSubsidyUSDMonth": sme_sub,
                "skillsTrainingCoverage": skills_cov,
                "socialProtectionTax": tax_prot,
                "smartInspectionCoverage": smart_insp,
            }
            st.session_state.scenario = "CUSTOM"
            st.rerun()

        # Action Buttons
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            if st.button("🚀 Ejecutar Simulación", use_container_width=True):
                play_holo_sound_js("wave")
                new_run = {
                    "id": f"RUN-{datetime.now().strftime('%M%S')}",
                    "name": f"{country_code}: Simulación {datetime.now().strftime('%H:%M')}",
                    "timestamp": "Justo ahora",
                    "country": country_code,
                    "scenario": selected_scenario,
                    "status": "completada",
                    "informalityChange": inf_delta,
                    "executionTimeSec": 3.6,
                }
                st.session_state.sim_runs.insert(0, new_run)
                st.success(f"✓ Corrida {new_run['id']} ejecutada y sincronizada.")
        with b_col2:
            if st.button("🔄 Restablecer Parámetros", use_container_width=True):
                st.session_state.policy_params = dict(INITIAL_POLICY_STATE)
                st.session_state.scenario = "BASELINE"
                play_holo_sound_js("click")
                st.rerun()

    with col_right:
        # Time Series Historical & Projected Projections (2015-2034)
        render_section_header("Proyección de Series Temporales (2015 - 2034)", icon="📈", badge="Macro Dinámica")

        years = list(range(2015, 2035))
        hist_years = list(range(2015, 2025))
        proj_years = list(range(2024, 2035))

        # Historical trend (2015-2024)
        hist_inf = [base_inf + (y - 2020) * 0.35 + (2.8 if y == 2020 else (1.6 if y == 2021 else 0)) for y in hist_years]
        hist_formal = [(100 - inf) * 0.91 for inf in hist_inf]
        
        # Projected trend (2024-2034) with policy convergence
        proj_inf = []
        target_inf = metrics["informalityRate"]
        for y in proj_years:
            step = (y - 2024) / 10.0
            inf_val = base_inf + (target_inf - base_inf) * (step ** 0.8)
            proj_inf.append(round(inf_val, 1))
        proj_formal = [round((100 - inf) * 0.92, 1) for inf in proj_inf]

        fig_ts = go.Figure()
        
        # Historical Informal Area
        fig_ts.add_trace(go.Scatter(
            x=hist_years, y=hist_inf,
            mode='lines',
            name='Informalidad Histórica (2015-2024)',
            line=dict(color='#f59e0b', width=2.5)
        ))
        # Projected Informal Area
        fig_ts.add_trace(go.Scatter(
            x=proj_years, y=proj_inf,
            mode='lines',
            name='Proyección con Políticas (2024-2034)',
            line=dict(color='#00f0ff', width=3, dash='solid'),
            fill='tonexty',
            fillcolor='rgba(0, 240, 255, 0.08)'
        ))
        # Projected Formal Area
        fig_ts.add_trace(go.Scatter(
            x=proj_years, y=proj_formal,
            mode='lines',
            name='Formalidad Proyectada (2024-2034)',
            line=dict(color='#10b981', width=2.5, dash='dash')
        ))

        # Vertical line for Current Year 2024
        theme = st.session_state.get("theme", "light")
        vline_col = "#64748b" if theme == "light" else "#ffffff"
        fig_ts.add_vline(x=2024, line_width=1.5, line_dash="dash", line_color=vline_col, annotation_text="2024 (Línea Base)", annotation_position="top left", annotation_font_color=vline_col)

        fig_ts.update_layout(
            title=dict(text="Transición del Mercado Laboral (2015 - 2034)"),
            xaxis=dict(title="Año", range=[2015, 2034]),
            yaxis=dict(title="% del Empleo Total", range=[0, 100]),
            margin=dict(l=30, r=20, t=35, b=50),
            height=260,
        )
        apply_chart_theme(fig_ts)
        st.plotly_chart(fig_ts, use_container_width=True)
        render_explainability_card(
            title="Explicabilidad: Serie Temporal de Transición Laboral (2015-2034)",
            what_it_is="Representa la trayectoria histórica observada (2015-2023) y la proyección a 10 años (2024-2034) de la distribución porcentual del empleo formal, empleo informal y desempleo.",
            how_to_read="La línea continua dorada muestra la informalidad histórica con choques reales (ej: COVID-19 en 2020). La línea continua cian modela la convergencia inducida por las reformas de política pública seleccionadas.",
            policy_impact="Permite evaluar la velocidad de amortiguamiento y reducción estructural de la informalidad bajo metas ODS 8. Si la brecha entre la curva cian y la línea base se ensancha, la política tiene alta efectividad transformacional.",
            formula="SARIMA(p,d,q) + Elasticidad de Formalización: ΔInf_t = -α * (Subsidio_t)^0.5 - β * (Capacitación_t)^0.8",
            alerts="Si la informalidad proyectada no desciende por debajo del 50% al año 2030, se requiere combinar incentivos de registro con subsidios directos a la nómina MiPyME."
        )

        # Baseline vs Simulated Intervention Comparison Bar Chart
        render_section_header("Comparativa: Línea Base vs Intervención Simulada", icon="⚖️", badge="Impacto Neto")

        base_formal_pct = round((100 - base_inf) * 0.9, 1)
        curr_formal_pct = round((100 - metrics["informalityRate"]) * 0.92, 1)
        base_decent = int(round(55 + (100 - base_inf) * 0.4))
        
        comp_df = pd.DataFrame({
            "Indicador": ["Informalidad (%)", "Empleo Formal (%)", "Trabajo Decente (0-100)", "Recaudación ($M USD)"],
            "Línea Base (Inercial)": [base_inf, base_formal_pct, base_decent, round(metrics['fiscalRevenueMillionUSD']*0.75, 1)],
            "Simulación Actual": [metrics["informalityRate"], curr_formal_pct, metrics["decentWorkIndex"], metrics["fiscalRevenueMillionUSD"]]
        })

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=comp_df["Indicador"],
            y=comp_df["Línea Base (Inercial)"],
            name="Línea Base (Inercial)",
            marker_color="#94a3b8" if theme == "light" else "#64748b"
        ))
        fig_comp.add_trace(go.Bar(
            x=comp_df["Indicador"],
            y=comp_df["Simulación Actual"],
            name="Simulación Actual (Intervención)",
            marker_color="#0284c7" if theme == "light" else "#00f0ff"
        ))

        fig_comp.update_layout(
            barmode='group',
            title=dict(text="Impacto Estructural Comparativo"),
            margin=dict(l=30, r=20, t=35, b=50),
            height=240,
        )
        apply_chart_theme(fig_comp)
        st.plotly_chart(fig_comp, use_container_width=True)
        render_explainability_card(
            title="Explicabilidad: Impacto Estructural Comparativo (Baseline vs Reforma)",
            what_it_is="Compara las 4 variables macroeconómicas troncales entre el escenario inercial (sin reformas) y el escenario con el paquete de políticas activas.",
            how_to_read="Las barras grises representan la inercia del mercado sin intervención estatal. Las barras cian muestran el estado alcanzado tras aplicar el paquete de reformas.",
            policy_impact="Demuestra si el paquete es autofinanciable: una mayor recaudación fiscal formal compensa el gasto en subsidios y programas de capacitación dual.",
            formula="Retorno Fiscal Neto = Recaudación Formal Proyectada - Costo Total de Subsidios e Inspección Digital"
        )

    # 4. Lorenz Curve & Employment Distribution
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    c_lorenz, c_runs = st.columns([1.2, 1.2])

    with c_lorenz:
        render_section_header("Curva de Lorenz & Concentración Salarial", icon="📊", badge="Gini")
        p = np.linspace(0, 1, 100)
        gini_val = metrics["giniIndex"]
        alpha = (1.0 + gini_val) / max(0.01, (1.0 - gini_val))
        lorenz_actual = p ** alpha
        base_alpha = (1.0 + profile["baseGini"]) / max(0.01, (1.0 - profile["baseGini"]))
        lorenz_baseline = p ** base_alpha

        curve_actual_col = "#0284c7" if theme == "light" else "#00f0ff"
        fill_col = "rgba(2, 132, 199, 0.08)" if theme == "light" else "rgba(0, 240, 255, 0.08)"

        fig_lorenz = go.Figure()
        fig_lorenz.add_trace(go.Scatter(x=p*100, y=p*100, mode='lines', name='Igualdad Perfecta (45°)', line=dict(color='#64748b', dash='dash', width=2)))
        fig_lorenz.add_trace(go.Scatter(x=p*100, y=lorenz_baseline*100, mode='lines', name=f'Línea Base (Gini {profile["baseGini"]})', line=dict(color='#f59e0b', width=2)))
        fig_lorenz.add_trace(go.Scatter(x=p*100, y=lorenz_actual*100, mode='lines', name=f'Simulación (Gini {gini_val})', line=dict(color=curve_actual_col, width=3), fill='tonexty', fillcolor=fill_col))

        fig_lorenz.update_layout(
            xaxis=dict(title="% Acumulado de Trabajadores"),
            yaxis=dict(title="% Acumulado del Ingreso"),
            margin=dict(l=30, r=20, t=20, b=50),
            height=240,
        )
        apply_chart_theme(fig_lorenz)
        st.plotly_chart(fig_lorenz, use_container_width=True)
        render_explainability_card(
            title="Explicabilidad: Curva de Lorenz y Coeficiente de Gini",
            what_it_is="Mide el grado de concentración del ingreso salarial en la fuerza de trabajo. Cuanto más se curve hacia abajo la línea, mayor es la desigualdad.",
            how_to_read="La línea de 45° discontinua es la distribución perfectamente equitativa. El área entre la línea de 45° y la curva de la simulación define el índice de Gini (0 = igualdad absoluta, 1 = concentración total).",
            policy_impact="Al formalizar trabajadores informales de bajos ingresos y mejorar su productividad, la curva cian se acerca a la diagonal, reduciendo la brecha salarial estructural.",
            formula="Gini = A / (A + B) = 1 - 2 * ∫[0 a 1] L(p) dp",
            alerts="Gini > 0.45 indica riesgo severo de polarización socioeconómica y descontento laboral."
        )

    with c_runs:
        render_section_header("Historial de Corridas de Simulación", icon="📜", badge="SQLite Sync")
        runs = st.session_state.get("sim_runs", [])
        if runs:
            df_runs = pd.DataFrame(runs)
            df_runs = df_runs[["id", "name", "country", "scenario", "informalityChange", "status", "timestamp"]]
            df_runs.columns = ["ID Corrida", "Nombre", "País", "Escenario", "Δ Inf (%)", "Estado", "Fecha / Hora"]
            st.dataframe(df_runs, use_container_width=True, hide_index=True, height=200)
            render_explainability_card(
                title="Explicabilidad: Registro Histórico y Trazabilidad de Simulaciones",
                what_it_is="Tabla auditada de ejecuciones experimentales persistidas en base de datos relacional para control de versiones de políticas.",
                how_to_read="Cada fila registra un ensayo contrafactual con su delta de formalización (Δ Inf %), permitiendo contrastar la sensibilidad de diferentes combinaciones paramétricas.",
                policy_impact="Permite justificar decisiones ante comités de política económica mediante evidencia reproducible y trazable."
            )
        else:
            st.info("No hay corridas registradas aún.")

