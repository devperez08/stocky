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
        # --- SECCIÓN DE PERFIL (Estilo Red Social) ---
        store_name = st.session_state.get("store_name", "Tu Tienda")
        plan_status = st.session_state.get("plan_status", "trial")
        
        # CSS para el avatar circular y estilo de perfil
        st.markdown("""
            <style>
                .profile-container {
                    display: flex;
                    align-items: center;
                    padding: 10px;
                    background-color: rgba(151, 166, 195, 0.1);
                    border-radius: 15px;
                    margin-bottom: 20px;
                    border: 1px solid rgba(151, 166, 195, 0.2);
                }
                .avatar {
                    width: 45px;
                    height: 45px;
                    background-color: #2e7d32;
                    color: white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    font-size: 20px;
                    margin-right: 12px;
                }
                .profile-info {
                    flex-grow: 1;
                }
                .store-title {
                    margin: 0;
                    font-size: 16px;
                    font-weight: 600;
                }
                .plan-badge {
                    font-size: 11px;
                    background-color: #ffd700;
                    color: black;
                    padding: 1px 6px;
                    border-radius: 10px;
                    font-weight: bold;
                }
            </style>
        """, unsafe_allow_html=True)

        initial = store_name[0].upper() if store_name else "S"
        badge_html = f'<span class="plan-badge">{plan_status.upper()}</span>' if plan_status == "trial" else f'<span class="plan-badge" style="background-color: #4caf50; color: white;">PRO</span>'
        
        st.markdown(f"""
            <div class="profile-container">
                <div class="avatar">{initial}</div>
                <div class="profile-info">
                    <p class="store-title">{store_name}</p>
                    {badge_html}
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("⚙️ Configuración del Perfil", use_container_width=True):
            st.session_state.menu_choice = "Configuración"
            st.rerun()

        st.divider()

        # --- NAVEGACIÓN PRINCIPAL ---
        st.caption("Menú Principal")
        options = ["Dashboard", "Productos", "Categorías", "Movimientos", "Reportes"]
        
        # Si no hay elección inicial, por defecto es Dashboard
        if "menu_choice" not in st.session_state:
            st.session_state.menu_choice = "Dashboard"
        
        # Calcular el índice para el radio si la página actual está en las opciones
        try:
            current_index = options.index(st.session_state.menu_choice)
        except ValueError:
            # Si estamos en "Configuración", no resaltamos ninguna opción del radio (o usamos el Dashboard por defecto)
            current_index = 0
            
        def on_nav_change():
            st.session_state.menu_choice = st.session_state.nav_radio

        st.radio(
            "Navegación",
            options=options,
            index=current_index,
            label_visibility="collapsed",
            key="nav_radio",
            on_change=on_nav_change
        )

        st.divider()

        # --- ESTADO Y CIERRE ---
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            for key in list(st.session_state.keys()):
                st.session_state.pop(key, None)
            st.rerun()

        if health:
            st.success("● Servidor Activo")
        else:
            st.error("● Servidor Offline")

        return st.session_state.menu_choice


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