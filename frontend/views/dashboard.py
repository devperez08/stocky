import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
        revenue = summary.get("total_sales_revenue_30d", 0.0)
        st.metric(label="📊 Ventas (Últimos 30 días)", value=f"${revenue:,.2f}")
        
    with col2:
        active_prods = summary.get("total_active_products", 0)
        st.metric(label="✅ Productos Activos", value=active_prods)
        
    with col3:
        critical_count = summary.get("critical_stock_count", 0)
        delta_val = f"{critical_count} alertas" if critical_count > 0 else "Normal"
        color = "inverse" if critical_count > 0 else "normal"
        st.metric(
            label="🚨 Stock Crítico", 
            value=critical_count, 
            delta=delta_val, 
            delta_color=color
        )
        
    with col4:
        movs = summary.get("movements_last_24h", {})
        total_movs_today = movs.get("entries", 0) + movs.get("exits", 0)
        st.metric(label="🔄 Movs (24h)", value=f"{total_movs_today}")

    st.divider()

    # --- 2. SECCIÓN VISUAL Y ALERTAS ---
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.subheader("⚠️ Atención Requerida (Stock Crítico)")
        low_stock = summary.get("low_stock_products", [])
        
        if low_stock:
            df_alert = pd.DataFrame(low_stock)
            df_alert.columns = ["ID", "Producto", "Stock Actual", "Mínimo Ideal"]
            st.dataframe(df_alert, hide_index=True, use_container_width=True)
            if critical_count > 5:
                 st.caption(f"Mostrando los 5 más críticos (Hay {critical_count} en total al borde).")
        else:
            st.success("🎉 ¡Excelente! No tienes productos por debajo del umbral de alerta.")

    with col_der:
        st.subheader("📊 Movimientos — Últimas 24h")
        mov_data = summary.get("movements_last_24h", {"entries": 0, "exits": 0})
        total_mov = mov_data["entries"] + mov_data["exits"]

        if total_mov == 0:
            st.info("Sin movimientos registrados en las últimas 24 horas.")
        else:
            fig = go.Figure(data=[
                go.Bar(
                    name="📥 Entradas",
                    x=["Movimientos"],
                    y=[mov_data["entries"]],
                    marker_color="#22c55e",  # Verde
                    text=[mov_data["entries"]],
                    textposition="outside"
                ),
                go.Bar(
                    name="📤 Salidas",
                    x=["Movimientos"],
                    y=[mov_data["exits"]],
                    marker_color="#ef4444",  # Rojo
                    text=[mov_data["exits"]],
                    textposition="outside"
                )
            ])
            fig.update_layout(
                barmode="group",
                yaxis=dict(tickformat="d", title="Cantidad"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=300,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- 3. SECCIÓN DE RENDIMIENTO ---
    st.subheader("📈 Rendimiento de Ventas (Últimos 15 días)")
    chart_data_raw = summary.get("sales_over_time", [])
    
    if chart_data_raw:
        chart_df = pd.DataFrame(chart_data_raw)
        chart_df["date"] = pd.to_datetime(chart_df["date"]).dt.strftime("%d %b")
        chart_df = chart_df.rename(columns={"date": "Fecha", "revenue": "Ingresos ($)"})
        st.line_chart(
            data=chart_df.set_index("Fecha"),
            use_container_width=True
        )
    else:
        st.info("No hay datos de ventas disponibles para los últimos 15 días.")