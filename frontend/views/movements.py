import streamlit as st
import pandas as pd
from utils.api_client import get, post
from datetime import datetime

def render():
    st.title("🔄 Registro de Movimientos")
    st.write("Gestiona las entradas y salidas de mercancía para mantener tu inventario al día.")

    # --- 1. CARGA DE DATOS ---
    # Obtenemos productos para el selector (necesitamos stock actual y nombre)
    products_data = get("/products")
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

        # Inicializar estado
        if "mov_type" not in st.session_state:
            st.session_state.mov_type = "entry"

        # Selector visual con dos columnas (botones grandes)
        st.write("**Tipo de Movimiento:**")
        col_entry, col_exit = st.columns(2)
        with col_entry:
            if st.button("📥 ENTRADA", use_container_width=True,
                         type="primary" if st.session_state.mov_type == "entry" else "secondary"):
                st.session_state.mov_type = "entry"
                st.rerun()
        with col_exit:
            if st.button("📤 SALIDA", use_container_width=True,
                         type="primary" if st.session_state.mov_type == "exit" else "secondary"):
                st.session_state.mov_type = "exit"
                st.rerun()

        mov_type = st.session_state.mov_type

        # Banner contextual según el tipo activo
        if mov_type == "entry":
            st.success("🟢 **MODO ACTIVO: ENTRADA DE STOCK** — Se incrementará el inventario del producto seleccionado.")
        else:
            st.error("🔴 **MODO ACTIVO: SALIDA DE STOCK** — Se descontará del inventario del producto seleccionado.")

        with st.form("movement_submission"):
            # Cantidad y Razón
            quantity = st.number_input("Cantidad", min_value=1, step=1, value=1)
            
            # Lógica de precio automatizada
            unit_value = None
            if mov_type == "entry":
                unit_value = st.number_input(
                    "💲 Valor Unitario *",
                    min_value=0.01, step=0.01, format="%.2f",
                    value=None, placeholder="Ej: 15.50",
                    help="Precio de compra por unidad. Campo obligatorio para entradas."
                )
            
            reason = st.text_input("Razón / Motivo", placeholder="Ej: Venta #101, Reabastecimiento...")

            # --- ALERTA VISUAL DE STOCK INSUFICIENTE ---
            if mov_type == "exit" and quantity > current_stock:
                st.error(f"⚠️ ¡Atención! No tienes suficiente stock. Faltan {quantity - current_stock} unidades.")
            
            # Resumen de la operación a realizar
            st.divider()
            action_verb = "Ingresarán" if mov_type == "entry" else "Saldrán"
            st.caption(f"📋 **Resumen:** {action_verb} **{quantity} unidades** de **{selected_name}**. "
                       f"Stock actual: {current_stock} → Nuevo stock estimado: "
                       f"{current_stock + quantity if mov_type == 'entry' else current_stock - quantity}")

            # Botón de confirmación con texto dinámico
            confirm_label = "✅ Confirmar Entrada de Stock" if mov_type == "entry" else "⚠️ Confirmar Salida de Stock"
            submitted = st.form_submit_button(confirm_label, type="primary", use_container_width=True)

            if submitted:
                # El backend ya valida, pero mejor validar también aquí para feedback rápido
                if mov_type == "entry" and (unit_value is None or unit_value <= 0):
                    st.error("⚠️ El Valor Unitario es obligatorio y debe ser mayor a cero para registrar una entrada.")
                    st.stop()
                elif mov_type == "exit" and quantity > current_stock:
                    st.error("No se puede registrar una salida superior al stock disponible.")
                else:
                    payload = {
                        "product_id": selected_product["id"],
                        "movement_type": mov_type,
                        "quantity": quantity,
                        "unit_value": unit_value,
                        "reason": reason if reason else "Sin motivo especificado"
                    }
                    result = post("/movements", payload)
                    if result:
                        st.success(f"Movimiento registrado correctamente para '{selected_name}'.")
                        st.rerun()

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
            
            st.write("---")
            from utils.api_client import delete
            
            # Mostrar botón "Anular" solo en movimientos no anulados
            for _, row in df.iterrows():
                col_data, col_action = st.columns([5, 1])
                with col_data:
                    style = "~~" if row.get("is_voided") else ""
                    anulado_tag = " **[ANULADO]**" if row.get("is_voided") else ""
                    st.markdown(f"{style}**{row['product_name']}** | {row['Tipo']} | {row['quantity']} uds | {row['Total ($)']} | {row['Fecha']}{style}{anulado_tag}")
                    st.caption(f"Motivo: {row['reason']}")
                with col_action:
                    if not row.get("is_voided"):
                        if st.button("🗑️ Anular", key=f"void_{row['id']}"):
                            result = delete(f"/movements/{row['id']}")
                            if result:
                                st.success(result["message"])
                                st.rerun()
                st.divider()
        else:
            st.info("No se han registrado movimientos aún.")
