"""
UI Components and Design Styling Helpers for Streamlit Frontend.
Includes custom CSS injections for Light Mode (default) and Dark Mode,
holographic/clean metric cards, badges, Web Audio effects, and Plotly theme styling.
"""

import streamlit as st
import streamlit.components.v1 as components

def inject_custom_css(theme: str = None):
    """
    Injects high-end design styling into the Streamlit app.
    Defaults to Light Mode with rich slate/white aesthetics, or Dark Mode if selected.
    """
    if theme is None:
        theme = st.session_state.get("theme", "light") if hasattr(st, "session_state") else "light"

    if theme == "light":
        custom_css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        code, kbd, samp, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Main background & container in Light Mode */
        .stApp {
            background-color: #f8fafc !important;
            background-image: 
                radial-gradient(circle at 12% 15%, rgba(2, 132, 199, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 88% 85%, rgba(16, 185, 129, 0.04) 0%, transparent 45%),
                radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.02) 0%, transparent 50%) !important;
            color: #0f172a !important;
        }

        /* Sidebar aesthetics */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0 !important;
        }

        [data-testid="stSidebar"] * {
            color: #1e293b;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] div {
            color: #334155;
        }

        /* Cards in Light Mode */
        .holo-card, .light-card {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
            border-radius: 12px !important;
            padding: 18px 22px;
            margin-bottom: 16px;
            transition: all 0.25s ease;
            color: #0f172a !important;
        }

        .holo-card:hover, .light-card:hover {
            border-color: #0284c7 !important;
            box-shadow: 0 8px 24px -4px rgba(2, 132, 199, 0.16) !important;
            transform: translateY(-1px);
        }

        /* View Banners */
        .view-banner {
            background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%) !important;
            border: 1px solid #bae6fd !important;
            box-shadow: 0 4px 16px rgba(2, 132, 199, 0.08) !important;
            border-radius: 12px !important;
            padding: 16px 24px !important;
            margin-bottom: 20px !important;
        }

        .view-banner h2 {
            color: #0f172a !important;
            font-weight: 800 !important;
        }

        .view-banner p {
            color: #475569 !important;
        }

        /* Override dark inline backgrounds from view templates */
        div[style*="background: rgba(11, 18, 32"],
        div[style*="background: rgba(15, 23, 42"],
        div[style*="background: #0b1220"] {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            color: #0f172a !important;
            box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.05) !important;
        }

        div[style*="background: rgba(11, 18, 32"] h2,
        div[style*="background: rgba(15, 23, 42"] h2,
        div[style*="background: linear-gradient(90deg"] h2 {
            color: #0f172a !important;
        }

        div[style*="background: rgba(11, 18, 32"] p,
        div[style*="background: rgba(15, 23, 42"] p,
        div[style*="background: linear-gradient(90deg"] p {
            color: #475569 !important;
        }

        div[style*="background: linear-gradient(90deg"] {
            background: linear-gradient(90deg, #f0f9ff 0%, #ffffff 100%) !important;
            border-left: 4px solid #0284c7 !important;
            border: 1px solid #bae6fd !important;
        }

        div[style*="background: rgba(8, 14, 26"] {
            background: #f8fafc !important;
            border: 1px solid #e2e8f0 !important;
            color: #1e293b !important;
        }

        div[style*="background: rgba(8, 14, 26"] span {
            color: #334155 !important;
        }

        /* Metric Value Styling */
        .holo-metric-val {
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #0f172a 0%, #0284c7 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            line-height: 1.2;
        }

        .holo-metric-label {
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748b !important;
            margin-bottom: 4px;
        }

        .holo-metric-delta-positive {
            color: #16a34a !important;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .holo-metric-delta-negative {
            color: #dc2626 !important;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* Badges */
        .glow-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .badge-cyan {
            background: #e0f2fe !important;
            color: #0369a1 !important;
            border: 1px solid #7dd3fc !important;
        }

        .badge-emerald {
            background: #dcfce7 !important;
            color: #15803d !important;
            border: 1px solid #86efac !important;
        }

        .badge-amber {
            background: #fef3c7 !important;
            color: #b45309 !important;
            border: 1px solid #fcd34d !important;
        }

        .badge-purple {
            background: #f3e8ff !important;
            color: #7e22ce !important;
            border: 1px solid #d8b4fe !important;
        }

        /* Section Header */
        .section-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #0f172a !important;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 14px;
            border-bottom: 1px solid #e2e8f0 !important;
            padding-bottom: 8px;
        }

        .section-title span {
            color: #0f172a !important;
        }

        /* Buttons in Light Mode */
        .stButton>button {
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }

        .stButton>button[kind="primary"], .stButton>button[type="primary"] {
            background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
            color: #ffffff !important;
            border: 1px solid #0284c7 !important;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25) !important;
        }

        .stButton>button[kind="secondary"], .stButton>button[type="secondary"] {
            background: #ffffff !important;
            color: #334155 !important;
            border: 1px solid #cbd5e1 !important;
        }

        .stButton>button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2) !important;
        }

        /* Chat messages */
        [data-testid="stChatMessage"] {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 10px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
            color: #0f172a !important;
            margin-bottom: 10px;
        }

        /* Dataframe and Tables */
        [data-testid="stDataFrame"] {
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            background: #ffffff !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            color: #0f172a !important;
            font-weight: 600 !important;
        }

        .streamlit-expanderContent {
            border: 1px solid #e2e8f0 !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
            background-color: #ffffff !important;
        }
        </style>
        """
    else:
        # Dark Holographic Theme
        custom_css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        code, kbd, samp, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        .stApp {
            background-color: #05070c;
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(0, 240, 255, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(16, 185, 129, 0.04) 0%, transparent 45%),
                radial-gradient(circle at 50% 50%, rgba(168, 85, 247, 0.03) 0%, transparent 50%);
            color: #f1f5f9;
        }

        .holo-card {
            background: rgba(11, 18, 32, 0.75);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(0, 240, 255, 0.2);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), inset 0 0 12px rgba(0, 240, 255, 0.05);
            border-radius: 12px;
            padding: 18px 22px;
            margin-bottom: 16px;
            transition: all 0.3s ease;
        }

        .holo-card:hover {
            border-color: rgba(0, 240, 255, 0.45);
            box-shadow: 0 12px 40px 0 rgba(0, 240, 255, 0.15);
        }

        .holo-metric-val {
            font-size: 2.1rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #ffffff 0%, #00f0ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.2;
        }

        .holo-metric-label {
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #94a3b8;
            margin-bottom: 4px;
        }

        .holo-metric-delta-positive {
            color: #10b981;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .holo-metric-delta-negative {
            color: #ef4444;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .glow-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .badge-cyan {
            background: rgba(0, 240, 255, 0.15);
            color: #00f0ff;
            border: 1px solid rgba(0, 240, 255, 0.4);
        }

        .badge-emerald {
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }

        .badge-amber {
            background: rgba(245, 158, 11, 0.15);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.4);
        }

        .badge-purple {
            background: rgba(168, 85, 247, 0.15);
            color: #a855f7;
            border: 1px solid rgba(168, 85, 247, 0.4);
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #f8fafc;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 8px;
        }

        .stButton>button {
            background: linear-gradient(135deg, rgba(0, 240, 255, 0.2) 0%, rgba(59, 130, 246, 0.3) 100%) !important;
            color: #00f0ff !important;
            border: 1px solid rgba(0, 240, 255, 0.5) !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }

        .stButton>button:hover {
            background: linear-gradient(135deg, rgba(0, 240, 255, 0.4) 0%, rgba(59, 130, 246, 0.5) 100%) !important;
            border-color: #00f0ff !important;
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.4) !important;
            transform: translateY(-1px) !important;
        }

        [data-testid="stSidebar"] {
            background-color: #070b14 !important;
            border-right: 1px solid rgba(0, 240, 255, 0.15) !important;
        }
        </style>
        """

    st.markdown(custom_css, unsafe_allow_html=True)


def render_metric_card(
    label: str,
    value: str,
    delta: str = None,
    delta_positive: bool = True,
    icon: str = "⚡",
    badge: str = None
):
    """Renders a KPI card styled cleanly according to the active theme."""
    delta_html = ""
    if delta:
        delta_class = "holo-metric-delta-positive" if delta_positive else "holo-metric-delta-negative"
        arrow = "▲" if delta_positive else "▼"
        delta_html = f'<div class="{delta_class}">{arrow} {delta}</div>'

    badge_html = f'<span class="glow-badge badge-cyan">{badge}</span>' if badge else ""

    html = f"""
    <div class="holo-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div class="holo-metric-label">{icon} {label}</div>
                <div class="holo-metric-val">{value}</div>
            </div>
            {badge_html}
        </div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_section_header(title: str, icon: str = "✦", badge: str = None):
    """Renders a styled section header with accent icon."""
    badge_html = f'<span class="glow-badge badge-purple" style="margin-left:auto;">{badge}</span>' if badge else ""
    theme = st.session_state.get("theme", "light") if hasattr(st, "session_state") else "light"
    icon_color = "#0284c7" if theme == "light" else "#00f0ff"
    html = f"""
    <div class="section-title">
        <span style="color:{icon_color};">{icon}</span>
        <span>{title}</span>
        {badge_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_explainability_card(
    title: str = "Interpretabilidad & Explicabilidad Econométrica",
    what_it_is: str = "",
    how_to_read: str = "",
    policy_impact: str = "",
    formula: str = None,
    alerts: str = None,
    expanded: bool = False
):
    """
    Renders an explainability card for Streamlit charts and tables.
    Provides rigorous econometric and public policy guidance for decision makers.
    """
    theme = st.session_state.get("theme", "light") if hasattr(st, "session_state") else "light"
    
    if theme == "light":
        card_bg = "#f8fafc"
        border_col = "#e2e8f0"
        title_col = "#0284c7"
        text_col = "#1e293b"
        formula_box = f'<div style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 12px; margin-top: 8px; font-family: monospace; font-size: 0.8rem; color: #0284c7;"><b>📐 Fórmula/Método:</b> {formula}</div>' if formula else ''
        alert_box = f'<div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 6px; padding: 6px 12px; margin-top: 8px; font-size: 0.8rem; color: #92400e;"><b>⚠️ Umbrales Críticos:</b> {alerts}</div>' if alerts else ''
    else:
        card_bg = "rgba(8, 14, 26, 0.7)"
        border_col = "rgba(0, 240, 255, 0.25)"
        title_col = "#00f0ff"
        text_col = "#f1f5f9"
        formula_box = f'<div style="background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px; padding: 6px 12px; margin-top: 8px; font-family: monospace; font-size: 0.8rem; color: #38bdf8;"><b>📐 Fórmula/Método:</b> {formula}</div>' if formula else ''
        alert_box = f'<div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 6px; padding: 6px 12px; margin-top: 8px; font-size: 0.8rem; color: #fcd34d;"><b>⚠️ Umbrales Críticos:</b> {alerts}</div>' if alerts else ''

    with st.expander(f"💡 {title}", expanded=expanded):
        st.markdown(f"""
        <div style="background: {card_bg}; border: 1px solid {border_col};
                    border-radius: 10px; padding: 14px 18px; margin-bottom: 8px; font-size: 0.88rem; line-height: 1.5; color: {text_col};">
            <div style="margin-bottom: 10px;">
                <b style="color: {title_col}; text-transform: uppercase; font-size: 0.76rem; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px;">
                    🎯 ¿Qué Representa / Objetivo:
                </b>
                <span>{what_it_is}</span>
            </div>
            
            <div style="margin-bottom: 10px;">
                <b style="color: #d97706; text-transform: uppercase; font-size: 0.76rem; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px;">
                    🔍 Lectura Técnica & Cómo Interpretarlo:
                </b>
                <span>{how_to_read}</span>
            </div>
            
            <div style="margin-bottom: {'10px' if (formula or alerts) else '2px'};">
                <b style="color: #16a34a; text-transform: uppercase; font-size: 0.76rem; letter-spacing: 0.05em; display: flex; align-items: center; gap: 6px;">
                    🏛️ Impacto en Políticas Públicas & Decisión:
                </b>
                <span>{policy_impact}</span>
            </div>
            
            {formula_box}
            {alert_box}
        </div>
        """, unsafe_allow_html=True)


def apply_chart_theme(fig, is_3d: bool = False, theme: str = None):
    """
    Applies unified color and styling tokens to any Plotly chart based on current theme.
    Ensures high legibility and cohesive presentation in Light Mode (or Dark Mode).
    """
    if theme is None:
        theme = st.session_state.get("theme", "light") if hasattr(st, "session_state") else "light"

    if theme == "light":
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#ffffff",
            font=dict(color="#1e293b", family="Inter, sans-serif"),
            title_font=dict(color="#0f172a", family="Inter, sans-serif", size=13),
        )
        if not is_3d:
            fig.update_xaxes(
                gridcolor="rgba(0, 0, 0, 0.06)",
                zerolinecolor="rgba(0, 0, 0, 0.1)",
                tickfont=dict(color="#64748b", size=10),
                title_font=dict(color="#334155", size=11)
            )
            fig.update_yaxes(
                gridcolor="rgba(0, 0, 0, 0.06)",
                zerolinecolor="rgba(0, 0, 0, 0.1)",
                tickfont=dict(color="#64748b", size=10),
                title_font=dict(color="#334155", size=11)
            )
            fig.update_layout(
                legend=dict(
                    font=dict(color="#1e293b", size=10),
                    bgcolor="rgba(255, 255, 255, 0.9)",
                    bordercolor="#e2e8f0"
                )
            )
        else:
            fig.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="#f8fafc",
                scene=dict(
                    xaxis=dict(
                        showgrid=True,
                        gridcolor="rgba(2, 132, 199, 0.15)",
                        backgroundcolor="#f8fafc",
                        title_font=dict(color="#0f172a"),
                        tickfont=dict(color="#475569")
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor="rgba(2, 132, 199, 0.15)",
                        backgroundcolor="#f8fafc",
                        title_font=dict(color="#0f172a"),
                        tickfont=dict(color="#475569")
                    ),
                    zaxis=dict(
                        showgrid=True,
                        gridcolor="rgba(2, 132, 199, 0.15)",
                        backgroundcolor="#f8fafc",
                        title_font=dict(color="#0f172a"),
                        tickfont=dict(color="#475569")
                    )
                ),
                legend=dict(
                    font=dict(color="#0f172a", size=10),
                    bgcolor="rgba(255, 255, 255, 0.9)",
                    bordercolor="#cbd5e1"
                )
            )
    else:
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(11, 18, 32, 0.6)",
            font=dict(color="#f8fafc", family="Inter, sans-serif"),
            title_font=dict(color="#f8fafc", family="Inter, sans-serif", size=13),
        )
        if not is_3d:
            fig.update_xaxes(
                gridcolor="rgba(255, 255, 255, 0.06)",
                zerolinecolor="rgba(255, 255, 255, 0.1)",
                tickfont=dict(color="#94a3b8", size=10),
                title_font=dict(color="#cbd5e1", size=11)
            )
            fig.update_yaxes(
                gridcolor="rgba(255, 255, 255, 0.06)",
                zerolinecolor="rgba(255, 255, 255, 0.1)",
                tickfont=dict(color="#94a3b8", size=10),
                title_font=dict(color="#cbd5e1", size=11)
            )
            fig.update_layout(
                legend=dict(
                    font=dict(color="#f8fafc", size=10),
                    bgcolor="rgba(11, 18, 32, 0.7)",
                    bordercolor="rgba(0, 240, 255, 0.2)"
                )
            )
        else:
            fig.update_layout(
                paper_bgcolor="#05070c",
                plot_bgcolor="#05070c",
                scene=dict(
                    xaxis=dict(showgrid=True, gridcolor="rgba(0, 240, 255, 0.1)", backgroundcolor="#05070c"),
                    yaxis=dict(showgrid=True, gridcolor="rgba(0, 240, 255, 0.1)", backgroundcolor="#05070c"),
                    zaxis=dict(showgrid=True, gridcolor="rgba(0, 240, 255, 0.1)", backgroundcolor="#05070c")
                ),
                legend=dict(
                    font=dict(color="#f8fafc", size=10),
                    bgcolor="rgba(11, 18, 32, 0.7)",
                    bordercolor="rgba(0, 240, 255, 0.2)"
                )
            )

    return fig


def play_holo_sound_js(sound_type: str = "click"):
    """Injects a tiny Web Audio API synthesizer for acoustic feedback."""
    js_code = f"""
    <script>
    (function() {{
        try {{
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            
            const now = ctx.currentTime;
            if ("{sound_type}" === "wave") {{
                osc.type = "sine";
                osc.frequency.setValueAtTime(220, now);
                osc.frequency.exponentialRampToValueAtTime(880, now + 0.35);
                gain.gain.setValueAtTime(0.2, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
                osc.start(now);
                osc.stop(now + 0.35);
            }} else {{
                osc.type = "triangle";
                osc.frequency.setValueAtTime(640, now);
                osc.frequency.exponentialRampToValueAtTime(320, now + 0.08);
                gain.gain.setValueAtTime(0.15, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
                osc.start(now);
                osc.stop(now + 0.08);
            }}
        }} catch(e) {{}}
    }})();
    </script>
    """
    components.html(js_code, height=0, width=0)
