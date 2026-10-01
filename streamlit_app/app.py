"""
Punto de Entrada Principal de la Aplicación en Streamlit:
Gemelo Digital 3D del Mercado Laboral y Transición a la Formalidad.
"""

import sys
import os
from pathlib import Path

# Ensure root workspace directory is in python path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import streamlit as st
from streamlit_app.config import init_session_state, t, COLORS
from streamlit_app.data.mock_data import COUNTRY_PROFILES
from streamlit_app.utils.ui_components import inject_custom_css, play_holo_sound_js

# View Modules
from streamlit_app.views.dashboard_view import render_dashboard_view
from streamlit_app.views.digital_twin_3d_view import render_digital_twin_3d_view
from streamlit_app.views.ai_engine_view import render_ai_engine_view
from streamlit_app.views.datasets_reports_view import render_datasets_reports_view
from streamlit_app.views.copilot_chat_view import render_copilot_chat_view
from streamlit_app.views.ilo_decent_work_view import render_ilo_decent_work_view
from streamlit_app.views.user_management_view import render_user_management_view

# 1. Streamlit Global Page Configuration
st.set_page_config(
    page_title="Gemelo Digital 3D | Mercado Laboral & Formalización",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Init State & Inject Custom Styles (Light Mode default)
init_session_state()
inject_custom_css(st.session_state.get("theme", "light"))

def main():
    # -------------------------------------------------------------
    # Sidebar Navigation & Context Controls
    # -------------------------------------------------------------
    with st.sidebar:
        theme = st.session_state.get("theme", "light")
        brand_color = "#0284c7" if theme == "light" else "#00f0ff"
        sub_color = "#64748b" if theme == "light" else "#94a3b8"
        border_color = "rgba(2, 132, 199, 0.2)" if theme == "light" else "rgba(0, 240, 255, 0.2)"

        # App Branding Header
        st.markdown(f"""
        <div style="text-align: center; padding: 8px 0 16px 0; border-bottom: 1px solid {border_color}; margin-bottom: 14px;">
            <div style="font-size: 2.2rem; margin-bottom: 4px;">🌐</div>
            <div style="font-size: 1.05rem; font-weight: 800; letter-spacing: -0.01em; color: {brand_color};">
                GEMELO DIGITAL 3D
            </div>
            <div style="font-size: 0.72rem; font-weight: 600; text-transform: uppercase; color: {sub_color}; letter-spacing: 0.08em;">
                Mercado Laboral & Formalización
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Theme Switcher (Modo Claro / Modo Oscuro)
        st.markdown("<div style='font-size: 0.76rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;'>Tema Visual</div>", unsafe_allow_html=True)
        col_th1, col_th2 = st.columns(2)
        with col_th1:
            if st.button("☀️ Claro", key="theme_light_btn", use_container_width=True, type="primary" if theme == "light" else "secondary"):
                if theme != "light":
                    st.session_state.theme = "light"
                    play_holo_sound_js("click")
                    st.rerun()
        with col_th2:
            if st.button("🌙 Oscuro", key="theme_dark_btn", use_container_width=True, type="primary" if theme == "dark" else "secondary"):
                if theme != "dark":
                    st.session_state.theme = "dark"
                    play_holo_sound_js("click")
                    st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # 1. Target Country Selector
        country_keys = list(COUNTRY_PROFILES.keys())
        country_display = {k: f"{COUNTRY_PROFILES[k]['flag']} {COUNTRY_PROFILES[k]['name']}" for k in country_keys}
        
        current_country = st.session_state.get("country", "KENYA")
        selected_country = st.selectbox(
            "📍 País Objetivo de Simulación",
            options=country_keys,
            format_func=lambda k: country_display[k],
            index=country_keys.index(current_country) if current_country in country_keys else 0,
            key="sidebar_country_selector"
        )
        if selected_country != current_country:
            st.session_state.country = selected_country
            st.session_state.scenario = "BASELINE"
            st.session_state.month = 0
            play_holo_sound_js("wave")
            st.rerun()

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # 2. Module Navigation Menu
        st.markdown("<div style='font-size: 0.78rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px;'>Módulos del Sistema</div>", unsafe_allow_html=True)

        nav_options = [
            ("dashboard", "📊 Dashboard Principal"),
            ("digital_twin_3d", "🌐 Gemelo Digital 3D"),
            ("ai_engine", "🧠 Motor IA & Explicabilidad"),
            ("datasets_reports", "📁 Datasets & Reportes"),
            ("copilot_chat", "🤖 Copiloto IA Laboral"),
            ("ilo_decent_work", "⚖️ Trabajo Decente OIT"),
            ("user_management", "👥 Gestión de Usuarios"),
        ]

        active_view = st.session_state.get("current_view", "dashboard")
        
        for view_key, label in nav_options:
            is_selected = (active_view == view_key)
            btn_style = "primary" if is_selected else "secondary"
            if st.button(label, key=f"nav_btn_{view_key}", use_container_width=True, type=btn_style):
                if active_view != view_key:
                    st.session_state.current_view = view_key
                    play_holo_sound_js("click")
                    st.rerun()

        st.markdown(f"<hr style='border: none; border-top: 1px solid {border_color}; margin: 18px 0;'>", unsafe_allow_html=True)

        # 3. Active User / Session Info
        user_role = st.session_state.get("role", "ADMIN")
        lang = st.session_state.get("language", "es")
        user_box_bg = "#f8fafc" if theme == "light" else "rgba(15, 23, 42, 0.6)"
        user_box_border = "#e2e8f0" if theme == "light" else "rgba(255,255,255,0.08)"
        user_box_text = "#0f172a" if theme == "light" else "#f8fafc"
        user_box_muted = "#64748b" if theme == "light" else "#94a3b8"

        st.markdown(f"""
        <div style="background: {user_box_bg}; border: 1px solid {user_box_border}; border-radius: 8px; padding: 10px 14px; font-size: 0.8rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: {user_box_muted};">Usuario Activo:</span>
                <span style="color: {user_box_text}; font-weight: 600;">Dra. E. Rostova</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: {user_box_muted};">Rol Asignado:</span>
                <span class="glow-badge badge-cyan">{user_role}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: {user_box_muted};">Versión:</span>
                <span style="color: {brand_color}; font-weight: 600;">v2.4.0 Streamlit</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Language Selector
        col_lang1, col_lang2 = st.columns(2)
        with col_lang1:
            if st.button("🇪🇸 Español", use_container_width=True, type="primary" if lang == "es" else "secondary"):
                st.session_state.language = "es"
                st.rerun()
        with col_lang2:
            if st.button("🇬🇧 English", use_container_width=True, type="primary" if lang == "en" else "secondary"):
                st.session_state.language = "en"
                st.rerun()

    # -------------------------------------------------------------
    # Main Dynamic View Router
    # -------------------------------------------------------------
    view = st.session_state.get("current_view", "dashboard")

    if view == "dashboard":
        render_dashboard_view()
    elif view == "digital_twin_3d":
        render_digital_twin_3d_view()
    elif view == "ai_engine":
        render_ai_engine_view()
    elif view == "datasets_reports":
        render_datasets_reports_view()
    elif view == "copilot_chat":
        render_copilot_chat_view()
    elif view == "ilo_decent_work":
        render_ilo_decent_work_view()
    elif view == "user_management":
        render_user_management_view()
    else:
        render_dashboard_view()

if __name__ == "__main__":
    main()
