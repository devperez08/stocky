import streamlit as st

from utils import api_client


def _save_auth_session(payload: dict, default_plan_status: str | None = None) -> None:
    st.session_state["token"] = payload.get("access_token")
    st.session_state["store_name"] = payload.get("store_name", "Tu Tienda")
    st.session_state["days_remaining"] = payload.get("days_remaining", 0)
    st.session_state["plan_status"] = payload.get("plan_status") or default_plan_status or "trial"


def render() -> None:
    st.title("Stocky - Sistema de Inventarios")
    st.caption("Inicia sesion o crea tu cuenta para administrar tu inventario.")

    tab_login, tab_signup = st.tabs(["Iniciar Sesion", "Crear Cuenta"])

    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Correo electronico")
            password = st.text_input("Contrasena", type="password")
            submitted = st.form_submit_button("Iniciar Sesion", use_container_width=True)

            if submitted:
                result = api_client.post_form(
                    "/auth/login",
                    data={"username": email, "password": password},
                    show_error=False,
                )
                if result and result.get("access_token"):
                    _save_auth_session(result)
                    st.success(f"Bienvenido, {result.get('store_name', 'Tu Tienda')}!")
                    st.rerun()
                st.error("Credenciales incorrectas.")

    with tab_signup:
        with st.form("signup_form", clear_on_submit=False):
            store_name = st.text_input("Nombre de tu tienda")
            email = st.text_input("Correo electronico", key="signup_email")
            password = st.text_input(
                "Contrasena (minimo 8 caracteres)",
                type="password",
                key="signup_password",
            )
            submitted = st.form_submit_button(
                "Crear cuenta gratis",
                use_container_width=True,
            )

            if submitted:
                result = api_client.post(
                    "/auth/signup",
                    data={"store_name": store_name, "email": email, "password": password},
                    show_error=False,
                )
                if result and result.get("access_token"):
                    _save_auth_session(result, default_plan_status="trial")
                    st.balloons()
                    st.success(f"Cuenta creada. Bienvenido, {result.get('store_name', 'Tu Tienda')}!")
                    st.rerun()
                st.error("No se pudo crear la cuenta. Verifica los datos e intenta de nuevo.")
