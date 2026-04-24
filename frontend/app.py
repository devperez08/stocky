import streamlit as st

# 🔥 SIEMPRE PRIMERO la configuración de la página (Vital en Win7/Legacy)
st.set_page_config(
    page_title="Stocky — Gestión de Inventarios",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils import api_client

# --- VERIFICACIÓN DE CONEXIÓN --- 
# Intentamos obtener el estatus del backend
health = api_client.get("/health")

with st.sidebar:
    st.title("📦 Stocky")
    
    # Indicador visual de conexión
    if health:
        st.success("● Backend Conectado")
    else:
        st.error("● Backend Desconectado")
        st.caption("Asegúrate de que la API esté corriendo.")
        
    st.caption("Sistema de Gestión de Inventarios")
    st.markdown("---")
    menu = st.radio(
        "",
        options=["Dashboard", "Productos", "Categorías", "Movimientos", "Reportes"]
    )

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