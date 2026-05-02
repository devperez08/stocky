import streamlit as st

def render():
    """
    Renderiza una pantalla de bloqueo persuasiva cuando la suscripción ha expirado.
    """
    detail = st.session_state.get("expiry_detail", {})
    expiry_date = detail.get("expiry_date", "Desconocida")
    days_overdue = detail.get("days_overdue", 0)

    # Limpiar el sidebar para enfocar al usuario en el mensaje de bloqueo
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>⏰ Tu acceso ha expirado</h1>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='text-align: center; font-size: 1.2em;'>"
            f"Tu período de prueba terminó el <b>{expiry_date}</b> "
            f"(hace <b>{days_overdue} días</b>).<br><br>"
            "Para continuar gestionando tu inventario con <b>Stocky</b>, activa tu suscripción mensual."
            "</p>",
            unsafe_allow_html=True
        )
        
        st.info("💡 **Dato:** Tus productos y datos siguen seguros, solo el acceso está pausado temporalmente.")
        
        st.markdown("---")
        st.markdown("### 💼 Plan Profesional — **$30.000 COP / mes**")
        st.markdown("""
        ✅ **Inventario ilimitado** de productos  
        ✅ **Dashboard** en tiempo real con KPIs  
        ✅ **Reportes** exportables a Excel y CSV  
        ✅ **Registro de movimientos** con trazabilidad
        """)
        st.markdown("---")
        
        if st.button("🚀 Activar mi suscripción ahora", use_container_width=True, type="primary"):
            # En el futuro esto llevará a la pasarela de pago (PRO-107/PRO-109)
            st.warning("El módulo de pagos estará disponible próximamente. Contacta a soporte.")
            
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            # Limpiar todo el estado y regresar al login
            st.session_state.clear()
            st.rerun()

    st.markdown("---")
