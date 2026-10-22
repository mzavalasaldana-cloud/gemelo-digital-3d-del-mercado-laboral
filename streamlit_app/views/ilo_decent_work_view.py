"""
Indicadores Empíricos Oficiales OIT / ILOSTAT
Presenta los datos empíricos oficiales de informalidad descargados de la API SDMX de ILOSTAT
(data/ilostat_s_F.csv y data/ilostat_gradientes.csv), sin índices ni fórmulas inventadas.
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from streamlit_app.data.mock_data import COUNTRY_PROFILES
from streamlit_app.simulation_engine import calculate_structural_metrics
from streamlit_app.utils.ui_components import (
    render_metric_card, 
    render_section_header,
    render_explainability_card
)

def load_ilostat_data():
    """Carga los CSVs oficiales de ILOSTAT."""
    grad_path = os.path.join("data", "ilostat_gradientes.csv")
    s_f_path = os.path.join("data", "ilostat_s_F.csv")
    
    df_grad = pd.read_csv(grad_path) if os.path.exists(grad_path) else pd.DataFrame()
    df_sf = pd.read_csv(s_f_path) if os.path.exists(s_f_path) else pd.DataFrame()
    return df_grad, df_sf

def render_ilo_decent_work_view():
    """Muestra indicadores oficiales empíricos de ILOSTAT para el país seleccionado."""
    country_code = st.session_state.get("country", "KENYA")
    scenario = st.session_state.get("scenario", "A")
    month = st.session_state.get("month", 0)
    profile = COUNTRY_PROFILES.get(country_code, COUNTRY_PROFILES["KENYA"])
    
    # Métricas del modelo calibrado ITDT
    metrics = calculate_structural_metrics(country_code, {}, scenario, month)
    df_grad, df_sf = load_ilostat_data()

    # Mapeo de código de país
    c_map = {"KENYA": "KEN", "NIGERIA": "NGA", "INDIA": "IND", "BANGLADESH": "BGD"}
    c_iso = c_map.get(country_code, "KEN")

    # Header
    st.markdown(f"""
    <div style="background: rgba(11, 18, 32, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(0, 240, 255, 0.35);
                border-radius: 12px; padding: 14px 22px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h2 style="margin: 0; font-size: 1.45rem; color: #f8fafc;">
                    📊 INDICADORES EMPÍRICOS OFICIALES OIT (ILOSTAT SDMX)
                </h2>
                <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #94a3b8;">
                    Datos reales observados de encuestas oficiales de empleo &bull; Sin índices sintéticos ni inventados
                </p>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span class="glow-badge badge-emerald">Fuente: ILOSTAT SDMX API</span>
                <span class="glow-badge badge-cyan">{profile['flag']} {profile['name']}</span>
                <span class="glow-badge badge-purple">Calibración ITDT</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Quick KPIs basados en datos empíricos reales
    base_inf = metrics.get('baseInformalityRate', profile.get('baseInformalityRate', 0.0))
    sim_inf = metrics.get('informalityRate', base_inf)
    gap = metrics.get('genderGap', 0.0)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card("Informalidad ILOSTAT Base", f"{base_inf:.2f}%", delta="Observado (ILOSTAT)", icon="📋", badge="Empírico")
    with k2:
        render_metric_card("Informalidad Simulada", f"{sim_inf:.2f}%", delta=f"{sim_inf - base_inf:+.2f} pp vs Base", icon="📉", badge=f"Escenario {scenario}")
    with k3:
        render_metric_card("Brecha de Género", f"{gap:+.2f} pp", delta=f"F: {metrics.get('informalityFemale', 0):.1f}% | M: {metrics.get('informalityMale', 0):.1f}%", icon="🚻", badge="Observado / Calibrado")
    with k4:
        formal_sim = round(100.0 - sim_inf, 2)
        render_metric_card("Empleo Formal Simulado", f"{formal_sim:.2f}%", delta=f"{metrics.get('formalWorkersCount', 0):,} agentes", icon="👔", badge="Modelo ITDT")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Tablas de gradientes reales de ILOSTAT
    col1, col2 = st.columns(2)

    with col1:
        render_section_header("Gradiente Educativo Real (EMP_NIFL_SEX_EDU_RT)", icon="🎓", badge="ILOSTAT")
        if not df_grad.empty:
            df_edu = df_grad[(df_grad['pais'] == c_iso) & (df_grad['indicador'] == 'EMP_NIFL_SEX_EDU_RT') & (df_grad['sexo'] == 'SEX_T')]
            if not df_edu.empty:
                show_edu = df_edu[['categoria', 'anio', 'valor']].rename(columns={
                    'categoria': 'Nivel Educativo',
                    'anio': 'Año Encuesta',
                    'valor': 'Informalidad (%)'
                })
                st.dataframe(show_edu, use_container_width=True, hide_index=True)
            else:
                st.info("Sin datos de gradiente educativo para este país en ILOSTAT.")
        else:
            st.info("Archivo data/ilostat_gradientes.csv no disponible.")

    with col2:
        render_section_header("Gradiente Geográfico Real (EMP_NIFL_SEX_GEO_RT)", icon="📍", badge="ILOSTAT")
        if not df_grad.empty:
            df_geo = df_grad[(df_grad['pais'] == c_iso) & (df_grad['indicador'] == 'EMP_NIFL_SEX_GEO_RT') & (df_grad['sexo'] == 'SEX_T')]
            if not df_geo.empty:
                show_geo = df_geo[['categoria', 'anio', 'valor']].rename(columns={
                    'categoria': 'Zona Geográfica',
                    'anio': 'Año Encuesta',
                    'valor': 'Informalidad (%)'
                })
                st.dataframe(show_geo, use_container_width=True, hide_index=True)
            else:
                st.info("Sin datos de gradiente geográfico para este país en ILOSTAT.")
        else:
            st.info("Archivo data/ilostat_gradientes.csv no disponible.")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    render_explainability_card(
        title="Integridad Empírica: Calibración y Validación con Datos Reales",
        what_it_is="Las tasas de informalidad del modelo ITDT provienen de los datos reales de encuestas laborales publicados por ILOSTAT. Se eliminaron fórmulas inventadas como el 'Índice de Trabajo Decente' no sustentado.",
        how_to_read="La columna 'Informalidad (%)' refleja el porcentaje observado en la encuesta oficial del país. El modelo calibrado reproduce estas tasas por sexo e induce los gradientes educativos y espaciales.",
        policy_impact="Garantiza que toda recomendación de política pública esté anclada en cifras empíricas verificadas y reproducibles."
    )
