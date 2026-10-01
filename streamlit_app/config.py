"""
Configuration, Theme tokens, and Session State management for Streamlit Frontend.
"""

import streamlit as st
from typing import Dict, Any
from streamlit_app.data.mock_data import INITIAL_POLICY_STATE, COUNTRY_PROFILES, MOCK_SIM_RUNS, MOCK_USERS

# Color Palette Design Tokens
LIGHT_COLORS = {
    "bg_main": "#f8fafc",
    "bg_surface": "#ffffff",
    "bg_card": "#ffffff",
    "border_glow": "rgba(2, 132, 199, 0.2)",
    "primary": "#0284c7",
    "primary_gradient": "linear-gradient(135deg, #0284c7 0%, #2563eb 100%)",
    "secondary": "#10b981",
    "warning": "#d97706",
    "danger": "#ef4444",
    "purple": "#8b5cf6",
    "text_primary": "#0f172a",
    "text_secondary": "#475569",
    "text_muted": "#64748b",
}

DARK_COLORS = {
    "bg_main": "#05070c",
    "bg_surface": "#0b1220",
    "bg_card": "rgba(15, 23, 42, 0.75)",
    "border_glow": "rgba(0, 240, 255, 0.25)",
    "primary": "#00f0ff",
    "primary_gradient": "linear-gradient(135deg, #00f0ff 0%, #3b82f6 100%)",
    "secondary": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "purple": "#a855f7",
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
}

COLORS = LIGHT_COLORS

def get_theme_colors(theme: str = None) -> Dict[str, str]:
    """Returns the color dictionary for the active or specified theme."""
    if theme is None:
        theme = st.session_state.get("theme", "light") if hasattr(st, "session_state") else "light"
    return LIGHT_COLORS if theme == "light" else DARK_COLORS


# i18n Text Translations
TRANSLATIONS = {
    "es": {
        "app_title": "GEMELO DIGITAL 3D DEL MERCADO LABORAL",
        "app_subtitle": "Simulador Micro-Económico de Transición a la Formalidad con Inteligencia Artificial",
        "nav_dashboard": "📊 Dashboard Principal",
        "nav_3d_twin": "🌐 Gemelo Digital 3D",
        "nav_ai_engine": "🧠 Motor IA & Explicabilidad",
        "nav_datasets": "📁 Datasets & Reportes",
        "nav_copilot": "🤖 Copiloto IA Laboral",
        "nav_ilo": "⚖️ Trabajo Decente OIT",
        "nav_users": "👥 Gestión de Usuarios",
        "country": "País Objetivo",
        "scenario": "Escenario",
        "user_role": "Rol Activo",
        "month": "Mes de Simulación",
        "year": "Año Proyectado",
        "run_simulation": "▶ Ejecutar Nueva Simulación",
        "informality_rate": "Tasa de Informalidad",
        "gini_index": "Índice de Gini",
        "decent_work_index": "Índice Trabajo Decente",
        "avg_formal_wage": "Salario Formal Promedio",
        "avg_informal_wage": "Salario Informal Promedio",
        "fiscal_balance": "Balance Fiscal Neto",
        "formal_workers": "Trabajadores Formales",
        "informal_workers": "Trabajadores Informales",
        "unemployed": "Desempleados",
        "scenario_baseline": "Línea Base (Inercial)",
        "scenario_registration": "Ventanilla Única Digital (-80% Costo)",
        "scenario_subsidy": "Subsidio Directo a PYMEs ($75/mes)",
        "scenario_shock": "Shock de Automatización Sectorial",
        "scenario_custom": "Personalizado / Híbrido",
    },
    "en": {
        "app_title": "LABOR MARKET 3D DIGITAL TWIN",
        "app_subtitle": "AI-Powered Micro-Economic Simulation for Formalization Transition",
        "nav_dashboard": "📊 Main Dashboard",
        "nav_3d_twin": "🌐 3D Digital Twin",
        "nav_ai_engine": "🧠 AI Engine & Explainability",
        "nav_datasets": "📁 Datasets & Reports",
        "nav_copilot": "🤖 Labor AI Copilot",
        "nav_ilo": "⚖️ ILO Decent Work",
        "nav_users": "👥 User Management",
        "country": "Target Country",
        "scenario": "Scenario",
        "user_role": "Active Role",
        "month": "Simulation Month",
        "year": "Projected Year",
        "run_simulation": "▶ Run New Simulation",
        "informality_rate": "Informality Rate",
        "gini_index": "Gini Index",
        "decent_work_index": "Decent Work Index",
        "avg_formal_wage": "Avg Formal Wage",
        "avg_informal_wage": "Avg Informal Wage",
        "fiscal_balance": "Net Fiscal Balance",
        "formal_workers": "Formal Workers",
        "informal_workers": "Informal Workers",
        "unemployed": "Unemployed",
        "scenario_baseline": "Baseline (Status Quo)",
        "scenario_registration": "Digital One-Stop Shop (-80% Cost)",
        "scenario_subsidy": "Direct SME Wage Subsidy ($75/mo)",
        "scenario_shock": "Sectoral Automation Shock",
        "scenario_custom": "Custom / Hybrid Policy",
    },
}

def init_session_state():
    """Initializes global reactive state in Streamlit's session_state."""
    if "current_view" not in st.session_state:
        st.session_state.current_view = "dashboard"

    if "theme" not in st.session_state:
        st.session_state.theme = "light"

    if "country" not in st.session_state:
        st.session_state.country = "KENYA"

    if "month" not in st.session_state:
        st.session_state.month = 0

    if "role" not in st.session_state:
        st.session_state.role = "ADMIN"

    if "scenario" not in st.session_state:
        st.session_state.scenario = "BASELINE"

    if "policy_params" not in st.session_state:
        st.session_state.policy_params = dict(INITIAL_POLICY_STATE)

    if "language" not in st.session_state:
        st.session_state.language = "es"

    if "sim_runs" not in st.session_state:
        st.session_state.sim_runs = list(MOCK_SIM_RUNS)

    if "users" not in st.session_state:
        st.session_state.users = list(MOCK_USERS)

    if "is_playing" not in st.session_state:
        st.session_state.is_playing = False

    if "playback_speed" not in st.session_state:
        st.session_state.playback_speed = 1.0

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "¡Hola! Soy tu Copiloto de Inteligencia Artificial en Economía Laboral y Políticas Públicas. Puedo ayudarte a evaluar el impacto fiscal, modelar elasticidades de formalización bajo directrices de la OIT o proyectar escenarios contrafactuales. ¿Qué aspecto del mercado laboral deseas analizar hoy?",
            }
        ]

    if "selected_worker_id" not in st.session_state:
        st.session_state.selected_worker_id = 0

    if "selected_firm_id" not in st.session_state:
        st.session_state.selected_firm_id = "firm-f-01"

    if "policy_wave_trigger" not in st.session_state:
        st.session_state.policy_wave_trigger = 0

def t(key: str) -> str:
    """Helper for translated strings based on active language."""
    lang = st.session_state.get("language", "es")
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"]).get(key, key)
