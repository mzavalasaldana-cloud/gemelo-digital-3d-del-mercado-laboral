"""
Datasets & Reportes: Microdata Ingestion, Household Survey Catalog, and Multi-format Executive Brief Generator.
"""

import streamlit as st
import json

from streamlit_app.data.mock_data import PRELOADED_DATASETS, COUNTRY_PROFILES
from backend.ml_engine import generate_synthetic_microdata
from streamlit_app.simulation_engine import calculate_structural_metrics
from streamlit_app.utils.report_generator import (
    generate_pdf_report,
    generate_excel_report,
    generate_html_report
)
from streamlit_app.utils.ui_components import (
    render_section_header, 
    render_explainability_card
)

def render_datasets_reports_view():
    """Renders the Datasets Catalog, Profiler, and Executive Reports Generator."""
    country_code = st.session_state.get("country", "KENYA")
    scenario = st.session_state.get("scenario", "A")
    if scenario in ("BASELINE", "STATUS_QUO"):
        scenario = "A"
    st.session_state.scenario = scenario

    month = st.session_state.get("month", 0)
    policy_params = st.session_state.get("policy_params", {})
    profile = COUNTRY_PROFILES.get(country_code, COUNTRY_PROFILES["KENYA"])
    metrics = calculate_structural_metrics(country_code, policy_params, scenario, month)


    # Header
    st.markdown("""
    <div style="background: rgba(11, 18, 32, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(16, 185, 129, 0.35);
                border-radius: 12px; padding: 14px 22px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h2 style="margin: 0; font-size: 1.45rem; color: #f8fafc;">
                    📁 DATASETS DE ENCUESTAS & GENERADOR DE REPORTES EJECUTIVOS
                </h2>
                <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #94a3b8;">
                    Datos sintéticos de demostración; no son microdatos oficiales. El artículo no usa microdatos: usa solo tasas agregadas de ILOSTAT.
                </p>
            </div>
            <div style="display: flex; gap: 8px;">
                <span class="glow-badge badge-emerald">4 Datasets Sintéticos (Demostración)</span>
                <span class="glow-badge badge-cyan">Exportación: PDF / Excel / HTML / JSON</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.warning("⚠️ **Aviso Metodológico:** Datos sintéticos de demostración; no son microdatos oficiales. El modelo y el artículo no usan microdatos, sino únicamente tasas agregadas de ILOSTAT.")

    tab_datasets, tab_reports = st.tabs(["📚 Catálogo & Ingesta de Microdatos", "📑 Generador de Informes Ejecutivos"])

    # -------------------------------------------------------------
    # TAB 1: Datasets Catalog & Uploader
    # -------------------------------------------------------------
    with tab_datasets:
        render_section_header("Catálogo de Encuestas de Hogares y Fuerza de Trabajo", icon="📚", badge="Datos de demostración")

        col_cat1, col_cat2 = st.columns([1.4, 1.0])

        with col_cat1:
            st.markdown("#### Encuestas Preconfiguradas (Datos de demostración):")
            for ds in PRELOADED_DATASETS:
                is_active_country = (ds["country"] == country_code)
                border_style = "border: 1px solid #00f0ff; background: rgba(0, 240, 255, 0.05);" if is_active_country else "border: 1px solid rgba(255, 255, 255, 0.1);"

                st.markdown(f"""
                <div class="holo-card" style="{border_style} padding: 12px 18px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <b style="color: #f8fafc; font-size: 1.0rem;">{ds['name']}</b>
                        <span class="glow-badge {'badge-cyan' if is_active_country else 'badge-emerald'}">
                            {'✓ Activo' if is_active_country else ds['country']}
                        </span>
                    </div>
                    <div style="font-size: 0.84rem; color: #cbd5e1; margin-top: 4px;">
                        <b>Institución:</b> {ds['institution']}<br>
                        <b>Muestra:</b> {ds['records']:,} individuos &bull; <b>Variables:</b> {ds['variables']} &bull; <b>Formato:</b> {ds['fileFormat']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col_cat2:
            st.markdown("#### Cargar Microdatos Propios (CSV / Excel):")
            uploaded_file = st.file_uploader(
                "Arrastra o selecciona un archivo de encuesta",
                type=["csv", "xlsx"],
                help="Sube un archivo de microdatos con variables de edad, salario, educación y sector formal/informal."
            )
            if uploaded_file is not None:
                st.success(f"✓ Archivo `{uploaded_file.name}` cargado correctamente en memoria temporal.")

        # Microdata Sample Profiler & Table
        render_section_header("Explorador y Perfilador de Microdatos Activos", icon="🔍", badge="500 Registros Muestra")
        df_sample = generate_synthetic_microdata(num_records=500, seed=123)

        st.dataframe(
            df_sample,
            use_container_width=True,
            hide_index=True,
            height=280
        )

        st.caption(f"Mostrando 500 registros armonizados del mercado laboral para {profile['name']}.")
        render_explainability_card(
            title="Explicabilidad: Estructura de Variables de Microdatos Armonizados",
            what_it_is="Esquema estandarizado de variables a nivel individual derivado de encuestas nacionales de hogares (edad, salario diario, sector, tamaño de empresa y contribución a seguridad social).",
            how_to_read="La variable objetivo binaria 'es_formal' (1 = empleo con contrato y aportes, 0 = informal sin cobertura) sirve como ground truth para el entrenamiento de los modelos XGBoost y las simulaciones del Gemelo 3D.",
            policy_impact="Garantiza la consistencia metodológica y la comparabilidad internacional entre países del Sur Global."
        )


    # -------------------------------------------------------------
    # TAB 2: Executive Reports Generator
    # -------------------------------------------------------------
    with tab_reports:
        render_section_header("Generador Oficial de Informes y Resúmenes de Política", icon="📑", badge="Multi-Formato")

        rep_scen_keys = ["A", "B1", "B2", "C", "D"]
        rep_labels = {
            "A": "Escenario A: Status Quo (Inercial)",
            "B1": "Escenario B1: GovTech Moderado",
            "B2": "Escenario B2: GovTech Intensivo (Sanciones 3×)",
            "C": "Escenario C: Red de Cuidados (-60% Cuidado)",
            "D": "Escenario D: Integrado (GovTech + Cuidados + Subsidio)",
        }
        report_scenario = st.selectbox(
            "Seleccionar Escenario para el Informe",
            options=rep_scen_keys,
            format_func=lambda s: rep_labels.get(s, s),
            index=rep_scen_keys.index(scenario) if scenario in rep_scen_keys else 0,
            key="report_scenario_select"
        )
        report_metrics = calculate_structural_metrics(country_code, policy_params, report_scenario, month)

        st.markdown(f"""
        <div class="holo-card" style="margin-bottom: 16px;">
            <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin-bottom: 6px;">
                Resumen Ejecutivo: {profile['name']} &mdash; {rep_labels.get(report_scenario, report_scenario)}
            </div>
            <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.6;">
                Informe técnico estructurado con evaluación de impacto macroeconómico, cumplimiento OIT (ODS 8),
                informalidad simulada ({report_metrics['informalityRate']}%) y balance fiscal (${report_metrics['fiscalRevenueMillionUSD']}M USD).
            </div>
        </div>
        """, unsafe_allow_html=True)


        # Generate Report Binaries
        pdf_bytes = generate_pdf_report(profile["name"], scenario, metrics, policy_params)
        excel_bytes = generate_excel_report(profile["name"], metrics, policy_params, df_sample)
        html_str = generate_html_report(profile["name"], scenario, metrics, policy_params)
        json_str = json.dumps({
            "country": profile["name"],
            "scenario": scenario,
            "metrics": metrics,
            "policy_parameters": policy_params,
        }, indent=2)

        col_d1, col_d2, col_d3, col_d4 = st.columns(4)

        with col_d1:
            st.download_button(
                label="📄 Descargar PDF Oficial",
                data=pdf_bytes,
                file_name=f"Informe_Laboral_{country_code}_{scenario}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with col_d2:
            st.download_button(
                label="📊 Descargar Excel (.xlsx)",
                data=excel_bytes,
                file_name=f"Simulacion_Laboral_{country_code}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with col_d3:
            st.download_button(
                label="🌐 Descargar HTML Interactivo",
                data=html_str,
                file_name=f"Reporte_Laboral_{country_code}.html",
                mime="text/html",
                use_container_width=True,
            )
        with col_d4:
            st.download_button(
                label="📋 Descargar JSON API",
                data=json_str,
                file_name=f"Simulacion_Metrics_{country_code}.json",
                mime="application/json",
                use_container_width=True,
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        render_section_header("Vista Previa del Resumen Ejecutivo", icon="👁️", badge="Preview")
        
        st.markdown(f"""
        <div style="background: #0b1220; border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 8px; padding: 18px; color: #cbd5e1; font-size: 0.9rem; line-height: 1.7;">
            <h4 style="color: #00f0ff; margin-top: 0;">Diagnóstico Macroeconómico Preliminar</h4>
            <p>
                La implementación del paquete de políticas para <b>{profile['name']}</b> bajo el escenario <b>{scenario}</b> 
                induce una reducción estimada de la informalidad del <b>{profile['baseInformalityRate']}%</b> al <b>{metrics['informalityRate']}%</b> 
                en un horizonte continuo de 10 años (Mes {month}).
            </p>
            <p>
                El <b>Balance Fiscal Neto</b> se proyecta en <b>${metrics['netFiscalBalanceMillionUSD']} Millones USD</b>, 
                soportado por una recaudación formal de <b>${metrics['fiscalRevenueMillionUSD']}M USD</b> frente a un costo operativo del programa 
                de <b>${metrics['policyCostMillionUSD']}M USD</b>.
            </p>
            <h4 style="color: #10b981;">Alineamiento con Estándares OIT</h4>
            <p>
                El Índice de Trabajo Decente alcanza <b>{metrics['decentWorkIndex']} puntos sobre 100</b>, reflejando mejoras sustanciales 
                en cobertura de seguridad social y reducción de la brecha salarial informal-formal.
            </p>
        </div>
        """, unsafe_allow_html=True)
