"""
Gemelo Digital 3D: Spatial 3D Multi-Agent Particle Simulation, Camera Presets, 120-Month Timeline & Agent Inspector.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from streamlit_app.data.mock_data import COUNTRY_PROFILES
from web_demo.simulation import get_model_firms
from streamlit_app.simulation_engine import (
    generate_worker_population,
    update_worker_positions_for_month,
    calculate_structural_metrics
)
from streamlit_app.utils.ui_components import (
    render_section_header, 
    play_holo_sound_js,
    apply_chart_theme
)

@st.cache_data(show_spinner=False)
def get_cached_workers(country_code: str):
    """Caches base 2,500 worker particles population per country."""
    return generate_worker_population(country_code, total_workers=2500)

def render_digital_twin_3d_view():
    """Renders the 3D Spatial Agent-Based Simulation View."""
    country_code = st.session_state.get("country", "KENYA")
    scenario = st.session_state.get("scenario", "A")
    if scenario in ("BASELINE", "STATUS_QUO"):
        scenario = "A"
    st.session_state.scenario = scenario

    month = st.session_state.get("month", 0)
    policy_params = st.session_state.get("policy_params", {})
    profile = COUNTRY_PROFILES.get(country_code, COUNTRY_PROFILES["KENYA"])

    # Load and position workers for active month
    base_workers = get_cached_workers(country_code)
    workers = update_worker_positions_for_month(base_workers, month, scenario, policy_params)
    metrics = calculate_structural_metrics(country_code, policy_params, scenario, month)
    model_firms = get_model_firms(country_code=country_code, scenario=scenario, month=month)

    # 1. Top HUD Bar
    month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    cur_year = 2024 + month // 12
    cur_month_name = month_names[month % 12]

    st.markdown(f"""
    <div style="background: rgba(11, 18, 32, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(0, 240, 255, 0.3);
                border-radius: 12px; padding: 12px 20px; margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <span style="font-size: 1.25rem; font-weight: 800; color: #00f0ff;">🌐 ESPACIO 3D GEMELO DIGITAL &mdash; {profile['flag']} {profile['name']}</span>
                <span style="margin-left: 12px; color: #94a3b8; font-size: 0.85rem;">2,500 Partículas Agente | 5 Hubs Productivos</span>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span class="glow-badge badge-cyan">Mes {month}/120 ({cur_month_name} {cur_year})</span>
                <span class="glow-badge badge-emerald">Escenario {scenario}</span>
                <span class="glow-badge badge-amber">Informalidad: {f"{metrics['informalityRate']}%" if metrics.get('informalityRate') is not None else "Sin dato"}</span>
                <span class="glow-badge badge-purple">Brecha F−M: {f"{metrics['genderGap']:+.1f} p.p." if metrics.get('genderGap') is not None else "Sin dato"}</span>
                <span class="glow-badge badge-cyan">{f"Gini: {metrics['giniIndex']:.3f}" if metrics.get('giniIndex') is not None else "Gini: Sin dato"}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Controls Bar: Scenario, Camera View & Sector Filter
    c_scen, c_cam, c_filt, c_speed = st.columns([1.1, 1.1, 1.1, 0.9])

    with c_scen:
        scen_options = ["A", "B1", "B2", "C", "D"]
        scen_labels = {
            "A": "A: Status Quo",
            "B1": "B1: GovTech Moderado",
            "B2": "B2: GovTech Sanciones 3×",
            "C": "C: Red de Cuidados",
            "D": "D: Integrado",
        }
        sel_scen = st.selectbox(
            "Escenario Canónico",
            options=scen_options,
            format_func=lambda s: str(scen_labels.get(str(s), s)),
            index=scen_options.index(scenario) if scenario in scen_options else 0,
            key="3d_scenario_selector"
        )
        if sel_scen != scenario:
            st.session_state.scenario = sel_scen
            play_holo_sound_js("wave")
            st.rerun()

    with c_cam:
        cam_preset = st.radio(
            "Perspectiva de Cámara 3D",
            options=["📐 Isométrica", "🛰️ Satelital", "🚶 Calle"],
            horizontal=True,
            key="cam_preset_radio"
        )
    with c_filt:
        sector_filter = st.selectbox(
            "Filtrar Población",
            options=["Todos (2,500)", "Solo Formales", "Solo Informales"],
            key="sector_filter_select"
        )
    with c_speed:
        st.selectbox(
            "Velocidad",
            options=["1x (Normal)", "2x (Acelerado)", "5x (Rápido)"],
            key="speed_select"
        )


    # Camera settings based on preset
    if "Satelital" in cam_preset:
        cam_eye = dict(x=0.01, y=2.8, z=0.01)
    elif "Calle" in cam_preset:
        cam_eye = dict(x=1.8, y=0.4, z=1.8)
    else:
        cam_eye = dict(x=1.4, y=1.2, z=1.4)

    # Filter workers if needed
    df_w = pd.DataFrame(workers)
    if "Formales" in sector_filter:
        df_w_filtered = df_w[df_w["sector"] == "formal"]
    elif "Informales" in sector_filter:
        df_w_filtered = df_w[df_w["sector"] == "informal"]
    elif "Desempleados" in sector_filter:
        df_w_filtered = df_w[df_w["sector"] == "unemployed"]
    else:
        df_w_filtered = df_w

    # 2. Main 3D Layout: Spatial Canvas (Left) + Timeline & Inspector (Right)
    col_3d, col_hud = st.columns([2.1, 1.1])

    with col_3d:
        fig_3d = go.Figure()

        color_map = {
            "formal": {"color": "#00f0ff", "name": "Formales (Órbita Hubs)", "size": 3.8},
            "informal": {"color": "#f59e0b", "name": "Informales (Valles)", "size": 3.2},
            "unemployed": {"color": "#64748b", "name": "Desempleados (Periferia)", "size": 2.8},
        }

        # Terrain Wireframe / Surface Grid
        gx = np.linspace(-25, 25, 25)
        gz = np.linspace(-25, 25, 25)
        GX, GZ = np.meshgrid(gx, gz)
        GY = np.sin(GX * 0.15) * np.cos(GZ * 0.15) * 0.4 - 0.2

        fig_3d.add_trace(go.Surface(
            x=GX, y=GY, z=GZ,
            colorscale=[[0, "#070c18"], [0.5, "#0b162a"], [1, "#0d203f"]],
            showscale=False,
            opacity=0.35,
            hoverinfo='none',
            name='Topografía del Mercado'
        ))

        for sector_key, meta in color_map.items():
            sub = df_w_filtered[df_w_filtered["sector"] == sector_key]
            if not sub.empty:
                fig_3d.add_trace(go.Scatter3d(
                    x=sub["x"],
                    y=sub["y"],
                    z=sub["z"],
                    mode="markers",
                    name=meta["name"],
                    marker=dict(
                        size=meta["size"],
                        color=meta["color"],
                        opacity=0.88,
                    ),
                    text=sub.apply(
                        lambda r: f"<b>Agente:</b> {r.get('code', '')}<br>"
                                  f"<b>Estado Laboral:</b> {r.get('display_sector', r.get('sector', '').title())}<br>"
                                  f"<b>Sexo:</b> {r.get('gender') or 'Sin dato'}<br>"
                                  f"<b>Zona:</b> {r.get('rural_zone') or 'Sin dato'}<br>"
                                  f"<b>Nivel Educativo:</b> {r.get('education') or 'Sin dato'}<br>"
                                  f"<b>Productividad (h_i):</b> {f'{float(r[\"productivity_h\"]):.3f}' if r.get('productivity_h') is not None else 'Sin dato'}<br>"
                                  f"<b>Cuidado Semanal:</b> {f'{float(r[\"care_hours\"]):.1f} hrs/sem' if r.get('care_hours') is not None else 'Sin dato'}<br>"
                                  f"<b>Alf. Digital (K_dig):</b> {f'{float(r[\"digital_lit\"])*100:.1f}%' if r.get('digital_lit') is not None else 'Sin dato'}",
                        axis=1
                    ),
                    hoverinfo="text",
                ))

        # Add Firm Hubs from Model
        for firm in model_firms:
            is_formal = firm["type"] == "formal"
            f_color = "#00f0ff" if is_formal else "#f59e0b"
            f_symbol = "diamond" if is_formal else "square"
            tipo_label = "Formal" if is_formal else "Informal"
            l_val = firm.get("L_j", 0.0)
            y_val = firm.get("Y_j", 0.0)
            a_val = firm.get("A_j", 0.0)
            
            fig_3d.add_trace(go.Scatter3d(
                x=[firm["x"]],
                y=[firm["height"] / 2.0],
                z=[firm["z"]],
                mode="markers+text",
                name=firm["id"],
                text=[firm["id"]],
                textposition="top center",
                textfont=dict(color=f_color, size=10),
                marker=dict(
                    size=12 if is_formal else 9,
                    color=f_color,
                    symbol=f_symbol,
                    opacity=0.95,
                    line=dict(color="#ffffff", width=1.5)
                ),
                hovertext=(
                    f"<b>Unidad Productiva:</b> {firm['id']}<br>"
                    f"<b>Estado:</b> {tipo_label}<br>"
                    f"<b>Empleo (L_j):</b> {l_val:.2f}<br>"
                    f"<b>Producción (Y_j):</b> {y_val:.2f}<br>"
                    f"<b>Productividad (A_j):</b> {a_val:.2f}"
                ),
                hoverinfo="text",
                showlegend=False
            ))

        theme = st.session_state.get("theme", "light")
        bg_col = "#ffffff" if theme == "light" else "#05070c"
        scene_bg = "#f8fafc" if theme == "light" else "#05070c"
        grid_col = "rgba(2, 132, 199, 0.15)" if theme == "light" else "rgba(0, 240, 255, 0.1)"
        leg_bg = "rgba(255, 255, 255, 0.9)" if theme == "light" else "rgba(11, 18, 32, 0.7)"
        leg_text = "#0f172a" if theme == "light" else "#f8fafc"

        fig_3d.update_layout(
            paper_bgcolor=bg_col,
            plot_bgcolor=bg_col,
            scene=dict(
                xaxis=dict(title="Eje X (Valle Informal -> Meseta Formal)", showgrid=True, gridcolor=grid_col, backgroundcolor=scene_bg, range=[-26, 26]),
                yaxis=dict(title="Altitud / Productividad (Y)", showgrid=True, gridcolor=grid_col, backgroundcolor=scene_bg, range=[-1, 9]),
                zaxis=dict(title="Eje Z (Sector Productivo)", showgrid=True, gridcolor=grid_col, backgroundcolor=scene_bg, range=[-26, 26]),
                camera=dict(eye=cam_eye),
                aspectmode="manual",
                aspectratio=dict(x=1.8, y=0.8, z=1.8),
            ),
            legend=dict(font=dict(color=leg_text, size=10), orientation="h", y=-0.05, x=0.05, bgcolor=leg_bg),
            margin=dict(l=0, r=0, t=0, b=10),
            height=580,
        )
        apply_chart_theme(fig_3d, is_3d=True)

        st.plotly_chart(fig_3d, use_container_width=True)

    with col_hud:
        # Timeline Controller Card
        st.markdown("""
        <div class="holo-card">
            <div class="holo-metric-label">⏱️ CONTROLADOR DE LÍNEA DE TIEMPO (2024 - 2034)</div>
        </div>
        """, unsafe_allow_html=True)

        new_month = st.slider(
            "Mes de Simulación (0 a 120 meses)",
            min_value=0,
            max_value=120,
            value=int(month),
            step=1,
            key="timeline_month_slider"
        )
        if new_month != month:
            st.session_state.month = new_month
            st.rerun()

        # Playback Controls
        btn_c1, btn_c2, btn_c3 = st.columns(3)
        with btn_c1:
            if st.button("▶ +6 Meses", use_container_width=True):
                st.session_state.month = min(120, st.session_state.month + 6)
                play_holo_sound_js("click")
                st.rerun()
        with btn_c2:
            if st.button("⏪ Reset T0", use_container_width=True):
                st.session_state.month = 0
                play_holo_sound_js("click")
                st.rerun()
        with btn_c3:
            if st.button("🌊 Onda Shock", use_container_width=True):
                st.session_state.policy_wave_trigger += 1
                play_holo_sound_js("wave")
                st.success("¡Onda de choque emitida!")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Micro-Agent Inspector
        render_section_header("Inspector de Micro-Agentes", icon="🔬", badge="Microdatos")

        agent_ids = [w["code"] for w in workers[:50]]
        selected_code = st.selectbox("Seleccionar Trabajador Muestra", options=agent_ids, index=0)
        selected_worker = next((w for w in workers if w["code"] == selected_code), workers[0])

        status_color = "#00f0ff" if selected_worker["sector"] == "formal" else ("#f59e0b" if selected_worker["sector"] == "informal" else "#94a3b8")

        st.markdown(f"""
        <div class="holo-card" style="border-left: 4px solid {status_color}; font-size: 0.85rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <b style="color: #f8fafc; font-size: 1.05rem;">{selected_worker.get('code', '')}</b>
                <span class="glow-badge badge-cyan">{selected_worker.get('display_sector', selected_worker.get('sector', '').title())}</span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; color: #cbd5e1;">
                <div><b>Sexo (OIT):</b> {selected_worker.get('gender') or 'Sin dato'}</div>
                <div><b>Zona Geográfica:</b> {selected_worker.get('rural_zone') or 'Sin dato'}</div>
                <div><b>Nivel Educativo:</b> <span style="color:#818cf8;">{selected_worker.get('education') or 'Sin dato'}</span></div>
                <div><b>Productividad Relativa (h_i):</b> <span style="color:#00f0ff;">{f"{float(selected_worker['productivity_h']):.3f}" if selected_worker.get('productivity_h') is not None else "Sin dato"}</span></div>
                <div><b>Cuidado Semanal (H_care,i):</b> <span style="color:#f59e0b;">{f"{float(selected_worker['care_hours']):.1f} hrs/sem" if selected_worker.get('care_hours') is not None else "Sin dato"}</span></div>
                <div><b>Alfabetización Digital (K_dig):</b> <span style="color:#10b981;">{f"{float(selected_worker['digital_lit'])*100:.1f}%" if selected_worker.get('digital_lit') is not None else "Sin dato"}</span></div>
                <div><b>Estado Laboral ITDT:</b> <span style="color:{status_color}; font-weight:700;">{selected_worker.get('display_sector', selected_worker.get('sector', '').title())}</span></div>
            </div>
            <div style="margin-top: 8px; font-size: 0.72rem; color: #94a3b8; border-top: 1px dashed rgba(148, 163, 184, 0.3); padding-top: 6px;">
                <b>Nota metodológica:</b> El modelo canónico ITDT calcula trayectorias macroeconómicas agregadas; la animación visual de partículas es puramente ilustrativa de las tasas del modelo.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Firm Inspector
        render_section_header("Inspector de Unidades Productivas", icon="🏢", badge="Modelo ITDT")
        firm_ids = [f["id"] for f in model_firms] if model_firms else ["UP-F-01"]
        sel_firm_id = st.selectbox("Seleccionar Unidad Productiva", options=firm_ids, index=0)
        sel_firm = next((f for f in model_firms if f["id"] == sel_firm_id), model_firms[0] if model_firms else {"id": "UP-F-01", "type": "formal", "L_j": 0.0, "Y_j": 0.0, "A_j": 0.0})
        is_sel_formal = sel_firm.get("type") == "formal"
        firm_border = "#00f0ff" if is_sel_formal else "#f59e0b"
        tipo_sel_label = "Formal" if is_sel_formal else "Informal"

        st.markdown(f"""
        <div class="holo-card" style="border-left: 4px solid {firm_border}; font-size: 0.85rem;">
            <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem; margin-bottom: 6px;">{sel_firm['id']}</div>
            <div style="color: #94a3b8; margin-bottom: 6px;">Estado: <b style="color: {firm_border};">{tipo_sel_label}</b></div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; color: #cbd5e1;">
                <div><b>Empleo (L_j):</b> {sel_firm.get('L_j', 0.0):.2f}</div>
                <div><b>Producción (Y_j):</b> {sel_firm.get('Y_j', 0.0):.2f}</div>
                <div><b>Productividad (A_j):</b> {sel_firm.get('A_j', 0.0):.2f}</div>
                <div><b>Tipo:</b> {sel_firm.get('type', '')}</div>
            </div>
            <div style="margin-top: 8px; font-size: 0.72rem; color: #94a3b8; border-top: 1px dashed rgba(148, 163, 184, 0.3); padding-top: 6px;">
                <b>Nota metodológica:</b> atributos de una réplica al final de la simulación (mes 120); la proporción de unidades productivas formales/informales refleja el mes seleccionado.
            </div>
        </div>
        """, unsafe_allow_html=True)
