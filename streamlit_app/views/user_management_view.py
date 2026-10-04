"""
Gestión de Usuarios & RBAC: User Directory, Register New User, Role Switching, Permissions Matrix, and Activity Audit Log.
"""

import streamlit as st
import pandas as pd

from streamlit_app.data.mock_data import DEMO_USERS
from streamlit_app.utils.ui_components import render_section_header, play_holo_sound_js

def render_user_management_view():
    """Renders the Role-Based Access Control and User Administration Module."""
    users = st.session_state.get("users", DEMO_USERS)
    current_role = st.session_state.get("role", "ADMIN")

    # Header
    st.markdown(f"""
    <div style="background: rgba(11, 18, 32, 0.85); backdrop-filter: blur(12px); border: 1px solid rgba(168, 85, 247, 0.35);
                border-radius: 12px; padding: 14px 22px; margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h2 style="margin: 0; font-size: 1.45rem; color: #f8fafc;">
                    👥 GESTIÓN DE USUARIOS & CONTROL DE ACCESO (RBAC)
                </h2>
                <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #94a3b8;">
                    Administración de Cuentas Institucionales &bull; Matriz de Permisos &bull; Registro de Auditoría
                </p>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span class="glow-badge badge-amber">Datos de demostración</span>
                <span class="glow-badge badge-purple">Tu Rol Activo: {current_role}</span>
                <span class="glow-badge badge-cyan">{len(users)} Cuentas Registradas</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_users, col_perm = st.columns([1.3, 1.1])

    with col_users:
        render_section_header("Directorio de Cuentas Institucionales", icon="👤", badge="Directorio")

        for u in users:
            is_active_user = (u["role"] == current_role)
            st.markdown(f"""
            <div class="holo-card" style="padding: 12px 16px; margin-bottom: 10px; border-left: 4px solid {'#00f0ff' if is_active_user else '#334155'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.5rem;">{u['avatar']}</span>
                        <div>
                            <b style="color: #f8fafc; font-size: 1.0rem;">{u['name']}</b>
                            <div style="color: #94a3b8; font-size: 0.8rem;">{u['email']} &bull; {u['department']}</div>
                        </div>
                    </div>
                    <span class="glow-badge badge-cyan">{u['role']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Form to register new user
        with st.expander("➕ Registrar / Invitar Nuevo Usuario Institucional"):
            with st.form("new_user_form", clear_on_submit=True):
                nu_name = st.text_input("Nombre y Apellido:", placeholder="Ej: Dr. Martín Vizcarra")
                nu_email = st.text_input("Correo Electrónico:", placeholder="usuario@gobierno.org")
                nu_dept = st.text_input("Departamento / Ministerio:", placeholder="Dirección de Estadística Laboral")
                nu_role = st.selectbox("Rol Asignado:", options=["POLICY_ANALYST", "RESEARCHER", "AUDITOR", "ADMIN"])
                
                submitted = st.form_submit_button("Crear Cuenta de Usuario")
                if submitted:
                    if nu_name and nu_email:
                        new_u = {
                            "id": f"usr-{len(users)+1:03d}",
                            "name": nu_name,
                            "email": nu_email,
                            "role": nu_role,
                            "department": nu_dept or "Ministerio de Trabajo",
                            "lastActive": "Recién creado",
                            "avatar": "🧑‍💼",
                            "permissions": {
                                "editPolicies": nu_role in ["ADMIN", "POLICY_ANALYST"],
                                "retrainAI": nu_role in ["ADMIN", "RESEARCHER"],
                                "manageDatasets": nu_role in ["ADMIN", "POLICY_ANALYST", "RESEARCHER"],
                                "manageUsers": nu_role == "ADMIN",
                                "exportReports": True,
                            }
                        }
                        st.session_state.users.append(new_u)
                        play_holo_sound_js("wave")
                        st.success(f"✓ Usuario {nu_name} creado con rol {nu_role}.")
                        st.rerun()
                    else:
                        st.error("Por favor completa nombre y correo.")

    with col_perm:
        render_section_header("Matriz de Permisos por Rol", icon="🛡️", badge="Seguridad")

        perm_data = [
            {"Acción / Capacidad": "Modificar Políticas Públicas", "ADMIN": "✓ Total", "POLICY_ANALYST": "✓ Total", "RESEARCHER": "✗ Solo Lectura", "AUDITOR": "✗ Solo Lectura"},
            {"Acción / Capacidad": "Reentrenar Motor IA (XGBoost)", "ADMIN": "✓ Total", "POLICY_ANALYST": "✗ Bloqueado", "RESEARCHER": "✓ Total", "AUDITOR": "✗ Bloqueado"},
            {"Acción / Capacidad": "Cargar & Ingestar Datasets", "ADMIN": "✓ Total", "POLICY_ANALYST": "✓ Total", "RESEARCHER": "✓ Total", "AUDITOR": "✗ Bloqueado"},
            {"Acción / Capacidad": "Administrar Usuarios y Roles", "ADMIN": "✓ Total", "POLICY_ANALYST": "✗ Bloqueado", "RESEARCHER": "✗ Bloqueado", "AUDITOR": "✗ Bloqueado"},
            {"Acción / Capacidad": "Exportar Reportes Oficiales", "ADMIN": "✓ Total", "POLICY_ANALYST": "✓ Total", "RESEARCHER": "✓ Total", "AUDITOR": "✓ Total"},
        ]
        st.dataframe(pd.DataFrame(perm_data), use_container_width=True, hide_index=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        render_section_header("Cambiar Rol Activo de Sesión", icon="🔄", badge="Simulación")
        
        role_options = ["ADMIN", "POLICY_ANALYST", "RESEARCHER", "AUDITOR"]
        new_role = st.selectbox(
            "Selecciona el rol con el que deseas interactuar en la plataforma:",
            options=role_options,
            index=role_options.index(current_role)
        )
        if new_role != current_role:
            st.session_state.role = new_role
            play_holo_sound_js("click")
            st.success(f"✓ Rol actualizado a: **{new_role}**")
            st.rerun()

    # Activity Audit Log
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    render_section_header("Registro de Auditoría y Trazabilidad (Audit Trail)", icon="📜", badge="Inmutable")

    audit_logs = [
        {"timestamp": "2026-09-21 15:18:22", "user": "Dra. Elena Rostova", "action": "Ajuste de subsidio PYME a $50 USD/mes", "ip": "192.168.1.42", "status": "SUCCESS"},
        {"timestamp": "2026-09-21 14:45:10", "user": "Dr. Kwame Achebe", "action": "Reentrenamiento de modelo XGBoost v3.4", "ip": "10.0.4.12", "status": "SUCCESS"},
        {"timestamp": "2026-09-21 13:20:05", "user": "Carlos Mendoza", "action": "Exportación de informe ejecutivo PDF (Kenia)", "ip": "192.168.1.88", "status": "SUCCESS"},
        {"timestamp": "2026-09-21 11:05:33", "user": "Sofia Lindqvist", "action": "Auditoría de consistencia de microdatos PLFS", "ip": "172.16.0.5", "status": "SUCCESS"},
    ]
    st.dataframe(pd.DataFrame(audit_logs), use_container_width=True, hide_index=True)
