import streamlit as st
import pandas as pd
from utils.api_client import get

def render():
    # --- CABECERA ---
    col_t1, col_t2 = st.columns([4, 1])
    with col_t1:
        st.title("📊 Dashboard Principal")
        st.write("Visión general e indicadores clave de tu inventario en tiempo real.")
    with col_t2:
        if st.button("🔄 Actualizar Datos", use_container_width=True):
            st.rerun()
            
    st.divider()

    # --- CARGA DE DATOS DESDE EL BACKEND ---
    # Usamos el endpoint centralizado y sumamente rápido que precalcula los KPIs.
    summary = get("/stats/summary")
    
    if summary is None or isinstance(summary, str):
        st.error("⚠️ No se pudo conectar con el motor de estadísticas. Verifica que el Backend esté online.")
        return

    # --- 1. SECCIÓN DE INDICADORES (KPIs) ---
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Formato de dinero (.2f)
        val = summary.get("total_inventory_value", 0.0)
        st.metric(label="💰 Valor del Inventario", value=f"${val:,.2f}")
        
    with col2:
        active_prods = summary.get("total_active_products", 0)
        st.metric(label="✅ Productos Activos", value=active_prods)
        
    with col3:
        critical_count = summary.get("critical_stock_count", 0)
        # delta_color="inverse": si hay críticos (positivo), lo pinta rojo indicando que es "malo"
        delta_val = f"{critical_count} alertas" if critical_count > 0 else "Normal"
        color = "inverse" if critical_count > 0 else "normal"
        st.metric(
            label="🚨 Stock Crítico", 
            value=critical_count, 
            delta=delta_val, 
            delta_color=color
        )
        
    with col4:
        # Sumamos la actividad de transacciones de hoy (Entradas + Salidas)
        movs = summary.get("movements_last_24h", {})
        total_movs_today = movs.get("entries", 0) + movs.get("exits", 0)
        st.metric(label="🔄 Actividad (24h)", value=f"{total_movs_today} Movs.")

    st.divider()

    # --- 2. SECCIÓN VISUAL Y ALERTAS ---
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.subheader("⚠️ Atención Requerida (Stock Crítico)")
        low_stock = summary.get("low_stock_products", [])
        
        if low_stock:
            # Transformamos el JSON directo de la DB a un Pandas DataFrame
            df_alert = pd.DataFrame(low_stock)
            # Damos formato humano a las columnas
            df_alert.columns = ["ID", "Producto", "Stock Actual", "Mínimo Ideal"]
            # Lo estilizamos
            st.dataframe(df_alert, hide_index=True, use_container_width=True)
            if critical_count > 5:
                 st.caption(f"Mostrando los 5 más críticos (Hay {critical_count} en total al borde).")
        else:
            st.success("🎉 ¡Excelente! No tienes productos por debajo del umbral de alerta.")

    with col_der:
        st.subheader("📈 Balance de Movimientos (24h)")
        mov_data = summary.get("movements_last_24h", {"entries": 0, "exits": 0})
        
        # Streamlit grafica nativamente usando pandas
        chart_data = pd.DataFrame({
            "Tipo": ["📥 Entradas (Compras)", "📤 Salidas (Ventas)"],
            "Transacciones": [mov_data.get("entries", 0), mov_data.get("exits", 0)]
        })
        
        # Ponemos "Tipo" como índice para que st.bar_chart coloree bien las descripciones inferiores
        st.bar_chart(
            chart_data.set_index("Tipo"),
            use_container_width=True
        )