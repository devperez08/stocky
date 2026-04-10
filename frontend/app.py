import streamlit as st
from utils import api_client

#importante siempre primero la configuracion de la pagina
st.set_page_config(
    page_title="Stocky — Gestión de Inventarios",
    page_icon="📦",
    layout="wide", # Esto hace que la app use todo el ancho de la pantalla
    initial_sidebar_state="expanded" # Esto hace que la barra lateral se muestre expandida al iniciar
)

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
    st.divider()
    menu = st.radio(
        "Navegación",
        options=["Dashboard", "Productos", "Movimientos", "Reportes"],
        label_visibility="collapsed"
    )

# Ruteo de páginas (usa 'views' para evitar conflicto con el sistema nativo de Streamlit)
if menu == "Dashboard":
    from views import dashboard; dashboard.render()
elif menu == "Productos":
    from views import products; products.render()
elif menu == "Movimientos":
    from views import movements; movements.render()
elif menu == "Reportes":
    from views import reports; reports.render()