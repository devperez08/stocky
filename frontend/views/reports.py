import streamlit as st
import pandas as pd
import io
from utils.api_client import get

def render():
    st.title("📑 Reportes Inteligentes")
    st.write("Previsualiza y descarga reportes del inventario en formato CSV o Excel.")

    # --- SELECTOR DE TIPO DE REPORTE ---
    report_type = st.selectbox(
        "Tipo de Reporte",
        options=["📦 Inventario Actual", "🔄 Historial de Movimientos"],
        index=0
    )

    st.markdown("---")

    # =========================================================
    # BLOQUE 1: REPORTE DE INVENTARIO
    # =========================================================
    if report_type == "📦 Inventario Actual":
        
        with st.spinner("Cargando datos del inventario..."):
            # Solicitamos el reporte en JSON para poder procesarlo con Pandas en el cliente
            data = get("/reports/inventory", params={"format": "json"})

        if not data or not isinstance(data, list):
            st.error("No se pudo cargar el reporte. Verifica la conexión con el backend.")
            return

        df = pd.DataFrame(data)
        
        # --- ESTADÍSTICAS RESUMIDAS (Pandas en el cliente, PRO-75) ---
        st.subheader("📊 Resumen Estadístico")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            valor_total = df["valor_total"].sum()
            st.metric("💰 Valor Total del Inventario", f"${valor_total:,.2f}")
        with col2:
            # Promedio de stock con 1 decimal
            stock_promedio = df["stock_actual"].mean()
            st.metric("📦 Stock Promedio", f"{stock_promedio:.1f} unidades")
        with col3:
            # Filtramos los productos con estado crítico desde el campo que ya calculó el backend
            critical_count = df[df["estado_stock"].str.contains("Crítico")].shape[0]
            st.metric("🚨 Productos Críticos", critical_count)

        st.subheader("📋 Vista Previa del Reporte")
        # Renombrar las columnas técnicas a nombres legibles para el usuario
        df_display = df.rename(columns={
            "id": "ID", "nombre": "Producto", "sku": "SKU",
            "categoria": "Categoría", "precio_unitario": "Precio",
            "stock_actual": "Stock", "valor_total": "Valor Total ($)",
            "alerta_minima": "Alerta Mínima", "estado_stock": "Estado",
            "creado_en": "Creado En"
        })
        st.dataframe(df_display, use_container_width=True)
        
        # --- BOTONES DE DESCARGA (PRO-75 criterion) ---
        st.subheader("⬇️ Descargar Reporte")
        col_csv, col_excel = st.columns(2)
        
        with col_csv:
            # Generamos el CSV en el cliente con codificación BOM para compatibilidad con Excel
            csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                label="📄 Descargar CSV",
                data=csv_bytes,
                file_name="inventario_stocky.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_excel:
            # Generamos el Excel en memoria con Pandas + openpyxl
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Inventario")
            st.download_button(
                label="📊 Descargar Excel",
                data=buffer.getvalue(),
                file_name="inventario_stocky.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    # =========================================================
    # BLOQUE 2: REPORTE DE MOVIMIENTOS
    # =========================================================
    elif report_type == "🔄 Historial de Movimientos":

        # --- FILTROS DE FECHA (PRO-75) ---
        st.subheader("🗓️ Filtros del Reporte")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            date_from = st.date_input("Desde (fecha inicio)")
        with col_d2:
            date_to = st.date_input("Hasta (fecha fin)")

        params = {
            "format": "json",
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat() + "T23:59:59"  # Incluir todo el día final
        }

        with st.spinner("Cargando historial de movimientos..."):
            data = get("/reports/movements", params=params)

        if data is None or not isinstance(data, list):
            st.error("No se pudo cargar el historial de movimientos.")
            return

        if not data:
            st.info("No hay movimientos registrados en el rango de fechas seleccionado.")
            return

        df = pd.DataFrame(data)

        # Estadísticas del historial filtrado
        st.subheader("📊 Resumen del Período")
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Total Operaciones", len(df))
        with col_s2:
            entradas = df[df["tipo"] == "Entrada"]["cantidad"].sum()
            st.metric("📥 Unidades Ingresadas", int(entradas))
        with col_s3:
            salidas = df[df["tipo"] == "Salida"]["cantidad"].sum()
            st.metric("📤 Unidades Vendidas", int(salidas))
        with col_s4:
            ganancias = df["total_venta"].sum() if "total_venta" in df.columns else 0.0
            st.metric("💰 Total Ventas Generadas", f"${ganancias:,.2f}")

        # --- GRÁFICA DE VENTAS ---
        if "total_venta" in df.columns and ganancias > 0:
            st.subheader("📈 Tendencia de Ventas (Período)")
            # Filtramos solo salidas con ventas, limpiamos fecha para el eje
            df_ventas = df[df["tipo"] == "Salida"].copy()
            df_ventas["Día"] = pd.to_datetime(df_ventas["fecha"]).dt.strftime("%Y-%m-%d")
            # Agrupar por día
            ventas_por_dia = df_ventas.groupby("Día")["total_venta"].sum().reset_index()
            ventas_por_dia.rename(columns={"total_venta": "Ingresos por Ventas ($)"}, inplace=True)
            st.bar_chart(data=ventas_por_dia.set_index("Día"), use_container_width=True)

        st.subheader("📋 Vista Previa del Historial")
        df_display = df.rename(columns={
            "id": "ID", "producto": "Producto", "tipo": "Tipo",
            "cantidad": "Cantidad", "precio_unidad": "Precio Und.", 
            "total_venta": "Venta Total", "motivo": "Motivo", "fecha": "Fecha"
        })
        st.dataframe(df_display, use_container_width=True)

        # --- DESCARGA ---
        st.subheader("⬇️ Descargar Reporte")
        col_csv2, col_excel2 = st.columns(2)
        
        with col_csv2:
            csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="📄 Descargar CSV",
                data=csv_bytes,
                file_name="movimientos_stocky.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_excel2:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Movimientos")
            st.download_button(
                label="📊 Descargar Excel",
                data=buffer.getvalue(),
                file_name="movimientos_stocky.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
