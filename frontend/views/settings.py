import streamlit as st
from utils import api_client
from datetime import datetime

def render():
    st.title("⚙️ Configuración y Suscripción")
    
    tab_sub, tab_plans = st.tabs(["📋 Mi Suscripción", "💳 Planes y Pagos"])

    # Obtener datos frescos de la tienda desde el backend
    with st.spinner("Cargando información de tu cuenta..."):
        store_info = api_client.get("/auth/me")

    if not store_info:
        st.error("No se pudo cargar la información de la tienda.")
        return

    plan = store_info.get("plan_status", "trial")
    days = store_info.get("days_remaining", 0)
    expiry = store_info.get("subscription_expiry_date", "Desconocida")
    trial_total = 14

    with tab_sub:
        st.subheader(f"🏪 {store_info['name']}")
        st.caption(f"Registrado con: {store_info['email']}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Estado del Plan", plan.upper())
        col2.metric("Días Restantes", max(days, 0))
        col3.metric("Fecha de Vencimiento", expiry)

        st.divider()
        
        if plan == "trial":
            # Calcular progreso (asumiendo 14 días totales)
            progress = max(0.0, min(1.0, (trial_total - days) / trial_total))
            st.write(f"**Progreso de tu período de prueba:**")
            st.progress(progress, text=f"{max(days, 0)} de {trial_total} días restantes")
            
            if 0 < days <= 3:
                st.warning(f"⚠️ ¡Atención! Tu período de prueba vence en **{days} día(s)**. Activa tu plan profesional para evitar interrupciones.")
            elif days <= 0:
                st.error("🔴 Tu acceso ha expirado. Por favor, activa una suscripción para continuar.")
        
        elif plan == "expired":
            st.error("🔴 Tu suscripción ha expirado.")
            st.info("Tus datos están seguros. Activa el plan profesional para recuperar el acceso completo.")
        
        elif plan == "active":
            st.success(f"✅ Tienes una suscripción profesional activa hasta el {expiry}.")
            st.balloons()

    with tab_plans:
        st.subheader("Elige el plan ideal para escalar tu negocio")
        
        col_trial, col_pro = st.columns(2)
        
        with col_trial:
            st.markdown("""
            ### 🆓 Plan Trial
            **$0 COP — 14 días**
            
            Ideal para explorar las funcionalidades básicas de Stocky sin costo.
            
            - ✅ Hasta 100 productos
            - ✅ Dashboard básico
            - ✅ Reportes en CSV
            - ❌ Sin soporte prioritario
            - ❌ Sin importación masiva
            """)
            if plan == "trial":
                st.button("Plan Actual", disabled=True, use_container_width=True)
            else:
                st.button("No disponible", disabled=True, use_container_width=True)

        with col_pro:
            st.markdown("""
            ### 🚀 Plan Profesional
            **$30.000 COP / mes**
            
            Potencia tu negocio con todas las herramientas de gestión avanzada.
            
            - ✅ **Productos ilimitados**
            - ✅ **Dashboard avanzado** (Entradas vs Salidas)
            - ✅ **Reportes Excel y CSV**
            - ✅ **Historial completo** de movimientos
            - ✅ **Importación masiva** desde Excel
            - ✅ **Soporte prioritario** por WhatsApp
            """)
            
            if plan == "active":
                st.button("Plan Actual", disabled=True, use_container_width=True)
            else:
                if st.button("💳 Activar Plan Profesional", use_container_width=True, type="primary"):
                    st.info("💳 La pasarela de pagos automática (PSE/Tarjetas) estará disponible en la próxima actualización.")
                    st.markdown("---")
                    st.write("**Mientras tanto, puedes activar tu plan manualmente:**")
                    st.write("1. Realiza una transferencia de $30.000 COP.")
                    st.write("2. Envía el comprobante a nuestro WhatsApp de soporte.")
                    st.button("💬 Contactar Soporte por WhatsApp", use_container_width=True)

        st.divider()
        st.subheader("💳 Métodos de Pago (Próximamente)")
        st.markdown("""
        | Método | Estado |
        |---|---|
        | 💳 Tarjeta de Crédito/Débito | 🟡 Integrando (Sprint 10) |
        | 🏦 PSE (Bancos colombianos) | 🟡 Integrando (Sprint 10) |
        | 📱 Nequi / Daviplata | 🟡 Integrando (Sprint 10) |
        """)
