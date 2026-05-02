import streamlit as st
from utils import api_client
from views import auth

#importante siempre primero la configuracion de la pagina
st.set_page_config(
    page_title="Stocky — Gestión de Inventarios",
    page_icon="📦",
    layout="wide", # Esto hace que la app use todo el ancho de la pantalla
    initial_sidebar_state="expanded" # Esto hace que la barra lateral se muestre expandida al iniciar
)

def _is_authenticated() -> bool:
    return bool(st.session_state.get("token"))


def _render_sidebar(health: dict | None) -> str:
    with st.sidebar:
        st.title("📦 Stocky")
        store_name = st.session_state.get("store_name", "Tu Tienda")
        days_left = st.session_state.get("days_remaining", 0)
        plan_status = st.session_state.get("plan_status", "trial")

        st.caption(f"🏪 {store_name}")
        if plan_status == "trial":
            st.info(f"⏳ Trial: {days_left} días restantes")
        elif plan_status == "active":
            st.success(f"✅ Suscripción activa - {days_left} días restantes")
        else:
            st.warning(f"⚠️ Plan {plan_status} - {days_left} días restantes")

        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            for key in ("token", "store_name", "days_remaining", "plan_status"):
                st.session_state.pop(key, None)
            st.rerun()

        st.divider()
        if health:
            st.success("● Backend Conectado")
        else:
            st.error("● Backend Desconectado")
            st.caption("Asegúrate de que la API esté corriendo.")

        st.caption("Sistema de Gestión de Inventarios")
        st.divider()
        return st.radio(
            "Navegación",
            options=["Dashboard", "Productos", "Categorías", "Movimientos", "Reportes", "Configuración"],
            label_visibility="collapsed"
        )


if not _is_authenticated():
    auth.render()
    st.stop()

# --- GUARD DE SUSCRIPCIÓN ---
if st.session_state.get("subscription_expired"):
    from views import subscription_expired
    subscription_expired.render()
    st.stop()
# ----------------------------

health = api_client.get("/health", show_error=False)

menu = _render_sidebar(health)

# Ruteo de páginas (usa 'views' para evitar conflicto con el sistema nativo de Streamlit)
if menu == "Dashboard":
    from views import dashboard; dashboard.render()
elif menu == "Productos":
    from views import products; products.render()
elif menu == "Categorías":
    from views import categories; categories.render()
elif menu == "Movimientos":
    from views import movements; movements.render()
elif menu == "Reportes":
    from views import reports; reports.render()
elif menu == "Configuración":
    from views import settings; settings.render()