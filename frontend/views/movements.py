import streamlit as st
import pandas as pd
from utils.api_client import get, post
from datetime import datetime

def render():
    st.title("🔄 Registro de Movimientos")
    st.write("Gestiona las entradas y salidas de mercancía para mantener tu inventario al día.")

    # --- 1. CARGA DE DATOS ---
    # Obtenemos productos para el selector (necesitamos stock actual y nombre)
    # Aumentamos el límite para asegurar que aparezcan todos en tiendas grandes
    products_data = get("/products", params={"limit": 1000})
    products = products_data if isinstance(products_data, list) else []
    
    # Creamos un mapa: Nombre -> Datos completos de producto
    product_map = {p["name"]: p for p in products if p.get("is_active")}

    if not product_map:
        st.warning("No hay productos activos registrados. Crea un producto antes de registrar movimientos.")
        return

    # --- 2. LAYOUT: FORMULARIO + HISTORIAL ---
    col_form, col_hist = st.columns([1, 1.2])

    with col_form:
        st.subheader("📦 Nuevo Registro")
        
        # SELECTOR Y TIPO FUERA DEL FORM para interactividad inmediata
        selected_name = st.selectbox("Seleccione Producto", options=list(product_map.keys()))
        selected_product = product_map.get(selected_name)
        
        # --- MÉTRICA DE STOCK EN VIVO ---
        current_stock = selected_product.get("stock_quantity", 0)
        st.metric(
            label="Stock Disponible", 
            value=current_stock,
            delta="Crítico" if current_stock <= selected_product.get("min_stock_alert", 5) else None,
            delta_color="inverse"
        )

        mov_type = st.radio(
            "Tipo de Operación", 
            options=["entry", "exit"],
            format_func=lambda x: "📥 Entrada (Compra de Mercancía)" if x == "entry" else "📤 Salida (Venta/Baja)"
        )

        with st.form("movement_submission"):
            # Cantidad y Razón
            quantity = st.number_input("Cantidad", min_value=1, step=1, value=1)
            
            # Lógica de precio automatizada
            if mov_type == "entry":
                default_cost = selected_product.get("cost_price", 0.0)
                unit_price_val = st.number_input(
                    "Costo Unitario de Compra ($)", 
                    min_value=0.0, step=0.01, value=float(default_cost),
                    help="Ingresa cuánto te costó cada unidad en esta compra."
                )
            else:
                unit_price_val = float(selected_product.get("price", 0.0))
                st.info(f"💰 Precio de venta: **${unit_price_val:,.2f}** (Valor del catálogo)")
            
            reason = st.text_input("Razón / Motivo", placeholder="Ej: Venta #101, Reabastecimiento...")

            # --- ALERTA VISUAL DE STOCK INSUFICIENTE ---
            if mov_type == "exit" and quantity > current_stock:
                st.error(f"⚠️ ¡Atención! No tienes suficiente stock. Faltan {quantity - current_stock} unidades.")
            
            submitted = st.form_submit_button("✅ Confirmar y Registrar")

            if submitted:
                # El backend ya valida, pero mejor validar también aquí para feedback rápido
                if mov_type == "exit" and quantity > current_stock:
                    st.error("No se puede registrar una salida superior al stock disponible.")
                else:
                    payload = {
                        "product_id": selected_product["id"],
                        "movement_type": mov_type,
                        "quantity": quantity,
                        "unit_price": unit_price_val,
                        "reason": reason if reason else "Sin motivo especificado"
                    }
                    result = post("/movements", payload)
                    if result:
                        st.success(f"Movimiento registrado correctamente para '{selected_name}'.")
                        st.experimental_rerun()

    with col_hist:
        st.subheader("📜 Historial de Operaciones")
        
        # Filtro rápido de historial
        filter_type = st.selectbox(
            "Filtrar historial por:", 
            options=["Todos", "📥 Entradas", "📤 Salidas"],
            index=0
        )
        
        # Mapeo de filtro para la API
        type_api_map = {"📥 Entradas": "entry", "📤 Salidas": "exit", "Todos": None}
        selected_api_type = type_api_map[filter_type]
        
        # Consultar últimos 50 movimientos
        params = {"limit": 50}
        if selected_api_type:
            params["movement_type"] = selected_api_type
            
        movements_list = get("/movements", params=params)
        movements = movements_list if isinstance(movements_list, list) else []

        if movements:
            df = pd.DataFrame(movements)
            
            # Limpieza de datos con Pandas para visualización
            df["Fecha"] = pd.to_datetime(df["created_at"], errors='coerce', utc=True).dt.strftime("%d/%m/%Y %H:%M")
            df["Tipo"] = df["movement_type"].apply(lambda x: "📥 ENTRADA" if x == "entry" else "📤 SALIDA")
            
            # Formatear valores monetarios
            df["Total ($)"] = df.apply(lambda row: f"-${row['total_value']:,.2f}" if row['movement_type'] == 'entry' else f"+${row['total_value']:,.2f}", axis=1)
            
            # Seleccionar y renombrar columnas
            view_df = df[["product_name", "Tipo", "quantity", "unit_price", "Total ($)", "reason", "Fecha"]].copy()
            view_df.columns = ["Producto", "Tipo", "Cantidad", "Precio U.", "Total ($)", "Motivo", "Fecha"]
            
            st.dataframe(view_df)
        else:
            st.info("No se han registrado movimientos aún.")
