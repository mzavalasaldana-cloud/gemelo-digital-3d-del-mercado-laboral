"""
Dashboard Principal: Macro-economic KPIs, Policy Simulation Sliders, Scenarios A/B1/B2/C/D,
Lorenz Curves, Time-Series from ITDTModel (2024-2034), and Empirical Inferences from outputs/.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from streamlit_app.config import t, COLORS
from streamlit_app.data.mock_data import COUNTRY_PROFILES, INITIAL_POLICY_STATE
from streamlit_app.simulation_engine import (
    calculate_structural_metrics,
    load_outputs_data,
    SCENARIO_CONFIGS,
)
from web_demo.simulation import _get_or_run_itdt_model
from streamlit_app.utils.ui_components import (
    render_metric_card, 
    render_section_header, 
    play_holo_sound_js,
    render_explainability_card,
    apply_chart_theme
)


def render_dashboard_view():
    """Renders the comprehensive 2D Executive Dashboard connected to ITDTModel and outputs/."""
    country_code = st.session_state.get("country", "KENYA")
    scenario = st.session_state.get("scenario", "A")
    if scenario in ("BASELINE", "STATUS_QUO"):
        scenario = "A"
    elif scenario not in SCENARIO_CONFIGS:
        scenario = "A"
    st.session_state.scenario = scenario

    month = st.session_state.get("month", 0)
    policy_params = st.session_state.get("policy_params", INITIAL_POLICY_STATE)
    profile = COUNTRY_PROFILES.get(country_code, COUNTRY_PROFILES["KENYA"])

    # Compute live metrics from ITDTModel
    metrics = calculate_structural_metrics(country_code, policy_params, scenario, month)
    outputs_tables = load_outputs_data()

    base_inf = profile.get("baseInformalityRate", metrics["baseInformalityRate"])
    inf_delta = round(metrics["informalityRate"] - base_inf, 1)

    # 1. Top Header Banner
    cur_year = 2024 + month // 12
    scenario_info = SCENARIO_CONFIGS.get(scenario, SCENARIO_CONFIGS["A"])

    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(0,240,255,0.12) 0%, rgba(15,23,42,0.85) 100%);
                padding: 16px 24px; border-radius: 12px; border-left: 4px solid #00f0ff; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <h2 style="margin: 0; font-size: 1.5rem; color: #f8fafc;">
                    {profile['flag']} {profile['name']} &mdash; Gemelo Digital Macroeconómico
                </h2>
                <p style="margin: 4px 0 0 0; font-size: 0.88rem; color: #94a3b8;">
                    {scenario_info['name']} &bull; {scenario_info['description']}
                </p>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
                <span class="glow-badge badge-cyan">Mes {month} / 120 (Año {cur_year})</span>
                <span class="glow-badge badge-emerald">Escenario {scenario} ({scenario_info['tag']})</span>
                <span class="glow-badge badge-purple">Motor: ITDTModel (ABM SMM)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Key Performance Indicators (6 Glassmorphic KPI Cards)
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        render_metric_card(
            label="Informalidad Total",
            value=f"{metrics['informalityRate']}%",
            delta=f"{inf_delta}% vs Base",
            delta_positive=(inf_delta < 0),
            icon="📉",
            badge="ODS 8.3"
        )
    with c2:
        gap = metrics.get("genderGap", 0.0)
        render_metric_card(
            label="Brecha Género (F−M)",
            value=f"{gap:+.1f} p.p.",
            delta=f"F: {metrics.get('informalityFemale', 0)}% | M: {metrics.get('informalityMale', 0)}%",
            delta_positive=(gap <= 3.0),
            icon="🚻",
            badge="Equidad"
        )
    with c3:
        render_metric_card(
            label="Índice de Gini",
            value=f"{metrics['giniIndex']}",
            delta=f"Base: {profile['baseGini']}",
            delta_positive=(metrics['giniIndex'] <= profile['baseGini']),
            icon="⚖️",
            badge="Gini"
        )
    with c4:
        render_metric_card(
            label="Trabajo Decente",
            value=f"{metrics['decentWorkIndex']}/100",
            delta="OIT Target 2030",
            delta_positive=True,
            icon="🛡️",
            badge="ODS 8"
        )
    with c5:
        exit_rate = metrics.get("annualExitRate", 0.0)
        render_metric_card(
            label="Cierres Anuales",
            value=f"{exit_rate:.1f}%",
            delta="Quiebra PYME",
            delta_positive=(exit_rate < 5.0),
            icon="⚠️",
            badge="Fragilidad"
        )
    with c6:
        render_metric_card(
            label="Recaudación Fiscal",
            value=f"${metrics['fiscalRevenueMillionUSD']}M",
            delta="Imp. Soc + Seg. Soc",
            delta_positive=True,
            icon="🏛️",
            badge="Fiscal"
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 3. Main Dashboard Layout: Sliders & Scenarios (Left) + Charts (Right)
    col_left, col_right = st.columns([1.1, 1.4])

    with col_left:
        render_section_header("Escenarios Canónicos del Artículo", icon="🎛️", badge="Sección 3.7")

        # Scenario Presets Quick Selector: STRICTLY A, B1, B2, C, D
        preset_names = {
            "A": "🌱 Escenario A: Status Quo (Inercial / Cobertura Básica)",
            "B1": "⚡ Escenario B1: GovTech Moderado (Auditoría + Facturación)",
            "B2": "⚖️ Escenario B2: GovTech Intensivo (GovTech + Sanciones 3×)",
            "C": "👶 Escenario C: Red de Cuidados (-60% Cuidado Infantil en Mujeres)",
            "D": "🌐 Escenario D: Integrado (GovTech + Cuidados + Subsidio DCC + Protección Social)",
        }
        
        scenario_keys = list(preset_names.keys())
        selected_scenario = st.selectbox(
            "Seleccionar Escenario de Política (Tablas 5, 6 y 7)",
            options=scenario_keys,
            format_func=lambda x: preset_names[x],
            index=scenario_keys.index(scenario) if scenario in scenario_keys else 0,
            key="dashboard_scenario_select"
        )

        if selected_scenario != scenario:
            st.session_state.scenario = selected_scenario
            play_holo_sound_js("wave")
            st.rerun()

        # Month Timeline Slider
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        render_section_header("Línea de Tiempo de Política (0 a 120 Meses)", icon="⏱️", badge="10 Años")
        
        slider_month = st.slider(
            "Mes de Aplicación de Política",
            min_value=0,
            max_value=120,
            value=int(month),
            step=1,
            help="Avanza a lo largo de los 120 meses de horizonte de política post-calentamiento.",
            key="dashboard_month_slider"
        )
        if slider_month != month:
            st.session_state.month = slider_month
            st.rerun()

        # Policy Explanation Card
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(0, 240, 255, 0.2);
                    border-radius: 10px; padding: 14px; margin-top: 10px;">
            <div style="font-weight: 700; color: #00f0ff; margin-bottom: 6px;">
                Efectos Teóricos del {scenario_info['name']}:
            </div>
            <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.5;">
                {scenario_info['description']}
            </div>
            <div style="margin-top: 8px; font-size: 0.78rem; color: #94a3b8;">
                <b>Parámetros activos:</b> κ={2.5 if scenario in ('B1','B2','D') else 1.0}×,
                Sanciones={3.0 if scenario in ('B2','D') else 1.0}×,
                Cuidados={'-60%' if scenario in ('C','D') else 'Base'},
                Subsidio DCC={'80% en L≤10' if scenario == 'D' else 'No'}.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Micro-información de Agentes Simulados
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        render_section_header("Desglose del Equilibrio de Agentes", icon="👥", badge="NumPy ABM")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Empresas Formales", f"{metrics['formalFirmsCount']} / 600")
            st.metric("Vacantes Formales", f"{metrics['formalVacancies']}")
        with col_m2:
            st.metric("Disposición Formal (UF > UI)", f"{metrics['willingWorkersCount']} / 6,000")
            st.metric("Entorno Digital D_sys", f"{metrics.get('digitalCoverage', 0.3):.3f}")

    with col_right:
        # Time Series from ITDTModel (Months 0 to 120 of policy)
        render_section_header("Trayectoria Simulada Auténtica (ITDTModel)", icon="📈", badge="120 Meses Reales")

        # Load genuine 120-month policy trajectory from model
        sim_data = _get_or_run_itdt_model(country_code, scenario)
        series = sim_data["monthly_series"]
        # Policy months are indices 96 to 215
        policy_slice = series[96:216]
        months_x = list(range(len(policy_slice)))
        tot_inf = [m["informality_total"] for m in policy_slice]
        fem_inf = [m["informality_female"] for m in policy_slice]
        male_inf = [m["informality_male"] for m in policy_slice]

        fig_ts = go.Figure()
        
        # Informalidad Total
        fig_ts.add_trace(go.Scatter(
            x=months_x, y=tot_inf,
            mode='lines',
            name=f'Informalidad Total ({scenario})',
            line=dict(color='#00f0ff', width=3)
        ))
        # Informalidad Mujeres
        fig_ts.add_trace(go.Scatter(
            x=months_x, y=fem_inf,
            mode='lines',
            name='Mujeres (s_F)',
            line=dict(color='#f43f5e', width=2, dash='dash')
        ))
        # Informalidad Hombres
        fig_ts.add_trace(go.Scatter(
            x=months_x, y=male_inf,
            mode='lines',
            name='Hombres',
            line=dict(color='#3b82f6', width=2, dash='dot')
        ))

        # Indicador de mes actual
        fig_ts.add_vline(
            x=month,
            line_width=1.5,
            line_dash="dash",
            line_color="#e2e8f0",
            annotation_text=f"Mes {month}",
            annotation_position="top left",
        )

        fig_ts.update_layout(
            title=dict(text=f"Dinámica Macroeconómica por Sexo &mdash; {profile['name']}"),
            xaxis=dict(title="Mes de Política (0 a 120)"),
            yaxis=dict(title="% Informalidad", range=[20, 100]),
            margin=dict(l=30, r=20, t=35, b=50),
            height=260,
        )
        apply_chart_theme(fig_ts)
        st.plotly_chart(fig_ts, use_container_width=True)

        render_explainability_card(
            title=f"Explicabilidad: Trayectoria de Agentes &mdash; Escenario {scenario}",
            what_it_is="Trayectoria mensual exacta generada por ITDTModel (6,000 trabajadores y 600 empresas) bajo dinámica de Metropolis con recocido simulado.",
            how_to_read="La curva cian representa la informalidad agregada. Las curvas rosa y azul muestran la asimetría por sexo derivada de la carga de cuidados no remunerados.",
            policy_impact="Permite contrastar si una reforma genera formalización genuina o si exacerba la brecha de género por falta de infraestructura de cuidados.",
            formula="P_aud = [1 + exp(-κ*(D_syst*Y/Y_bar - θ_th))]^-1 ; T_k = T_0 * d^k ; U_F vs U_I",
        )

        # Baseline vs Simulated Intervention Comparison Bar Chart
        render_section_header("Comparativa: Línea Base vs Estado Actual", icon="⚖️", badge="Equilibrio")

        comp_df = pd.DataFrame({
            "Indicador": ["Informalidad Total (%)", "Informalidad Mujeres (%)", "Informalidad Hombres (%)", "Trabajo Decente (0-100)"],
            "Línea Base (ILOSTAT)": [base_inf, profile.get("baseInformalityFemale", 90.0), profile.get("baseInformalityMale", 83.0), 45],
            f"Simulación (Mes {month})": [metrics["informalityRate"], metrics["informalityFemale"], metrics["informalityMale"], metrics["decentWorkIndex"]]
        })

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=comp_df["Indicador"],
            y=comp_df["Línea Base (ILOSTAT)"],
            name="Línea Base (ILOSTAT)",
            marker_color="#64748b"
        ))
        fig_comp.add_trace(go.Bar(
            x=comp_df["Indicador"],
            y=comp_df[f"Simulación (Mes {month})"],
            name=f"Simulación ({scenario})",
            marker_color="#00f0ff"
        ))

        fig_comp.update_layout(
            barmode='group',
            title=dict(text="Impacto Estructural frente a Línea Base"),
            margin=dict(l=30, r=20, t=35, b=50),
            height=230,
        )
        apply_chart_theme(fig_comp)
        st.plotly_chart(fig_comp, use_container_width=True)

    # 4. Outputs Oficiales del Artículo: Tablas 5, 6 y 7
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    render_section_header("Inferencia Econométrica Oficial (Resultados en outputs/)", icon="📑", badge="Artículo")

    tab_t5, tab_t6, tab_t7, tab_lorenz = st.tabs([
        "📊 Tabla 5: Niveles por Escenario",
        "📈 Tabla 6: Cambios e IC 95% Bootstrap",
        "🎯 Tabla 7: Contrastes Pareados por País",
        "📐 Curva de Lorenz & Gradientes"
    ])

    with tab_t5:
        st.markdown("##### Niveles medios por escenario en meses 109–120 (promedio de los 4 países, R = 40)")
        t5_data = outputs_tables.get("table5_levels", [])
        if t5_data:
            st.dataframe(pd.DataFrame(t5_data), use_container_width=True, hide_index=True)
        else:
            st.info("Outputs de Tabla 5 no encontrados.")

    with tab_t6:
        st.markdown("##### Cambios frente al Escenario A e Intervalos de Confianza del 95% (Cluster Bootstrap, B = 4000)")
        t6_data = outputs_tables.get("table6_changes", [])
        if t6_data:
            st.dataframe(pd.DataFrame(t6_data), use_container_width=True, hide_index=True)
        else:
            st.info("Outputs de Tabla 6 no encontrados.")

    with tab_t7:
        st.markdown(f"##### Contrastes pareados para **{profile['name']}** frente al Escenario A (R = 40 réplicas, gl = 39)")
        t7_data = outputs_tables.get("table7_contrasts", [])
        if t7_data:
            df_t7 = pd.DataFrame(t7_data)
            # Filtrar por país si está disponible
            p_name = profile["name"]
            filtered_t7 = df_t7[df_t7["País"].str.upper() == p_name.upper()] if "País" in df_t7.columns else df_t7
            st.dataframe(filtered_t7 if not filtered_t7.empty else df_t7, use_container_width=True, hide_index=True)
        else:
            st.info("Outputs de Tabla 7 no encontrados.")

    with tab_lorenz:
        c_lor1, c_lor2 = st.columns([1.2, 1.2])
        with c_lor1:
            p_pts = np.linspace(0, 1, 100)
            gini_val = metrics["giniIndex"]
            alpha = (1.0 + gini_val) / max(0.01, (1.0 - gini_val))
            lorenz_actual = p_pts ** alpha
            base_alpha = (1.0 + profile["baseGini"]) / max(0.01, (1.0 - profile["baseGini"]))
            lorenz_baseline = p_pts ** base_alpha

            fig_lorenz = go.Figure()
            fig_lorenz.add_trace(go.Scatter(x=p_pts*100, y=p_pts*100, mode='lines', name='Igualdad Perfecta', line=dict(color='#64748b', dash='dash')))
            fig_lorenz.add_trace(go.Scatter(x=p_pts*100, y=lorenz_baseline*100, mode='lines', name=f'Línea Base (Gini {profile["baseGini"]})', line=dict(color='#f59e0b')))
            fig_lorenz.add_trace(go.Scatter(x=p_pts*100, y=lorenz_actual*100, mode='lines', name=f'Simulado ({scenario} Gini {gini_val})', line=dict(color='#00f0ff', width=3)))

            fig_lorenz.update_layout(
                title=dict(text="Curva de Lorenz"),
                xaxis=dict(title="% Trabajadores"),
                yaxis=dict(title="% Ingreso"),
                margin=dict(l=30, r=20, t=30, b=40),
                height=240,
            )
            apply_chart_theme(fig_lorenz)
            st.plotly_chart(fig_lorenz, use_container_width=True)

        with c_lor2:
            st.markdown("##### Gradientes Distributivos No Calibrados:")
            st.write(f"- **Por Zona:** Rural = {metrics.get('informalityByZone', {}).get('rural', 'N/D')}% | Urbano = {metrics.get('informalityByZone', {}).get('urban', 'N/D')}%")
            edu = metrics.get('informalityByEducation', {})
            st.write(f"- **Por Educación:** Básica = {edu.get(0, edu.get('0', 'N/D'))}% | Media = {edu.get(1, edu.get('1', 'N/D'))}% | Superior = {edu.get(2, edu.get('2', 'N/D'))}%")
            quint = metrics.get('informalityByQuintile', {})
            st.write(f"- **Por Quintiles de Productividad:** Q1 = {quint.get(1, quint.get('1', 'N/D'))}% | Q5 = {quint.get(5, quint.get('5', 'N/D'))}%")
            st.caption("Los gradientes validan el principio de equidad: la informalidad disminuye monótonamente con la educación y la productividad, y es mayor en zonas rurales.")
