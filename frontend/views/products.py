import streamlit as st
import pandas as pd
from utils.api_client import get, post, put, delete

def render():
    st.title("📦 Gestión de Productos")
    st.write("Administra el catálogo: crea nuevos productos, actualiza datos o busca información.")

    # --- 1. FILTROS DE BÚSQUEDA ---
    st.subheader("Búsqueda y Filtros")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_name = st.text_input("Buscar por nombre...", placeholder="Ej: Café, Arroz, Mouse...")
        
    with col2:
        # Cargar categorías para el filtro
        cat_data = get("/categories")
        categories = cat_data if isinstance(cat_data, list) else []
        cat_options = {"Todas": None}
        for c in categories:
            cat_options[c["name"]] = c["id"]
        
        selected_cat_name = st.selectbox("Filtrar por Categoría", options=list(cat_options.keys()))
        selected_cat_id = cat_options[selected_cat_name]

    # --- 2. CARGAR Y MOSTRAR DATOS ---
    params = {}
    if search_name:
        params["name"] = search_name
    if selected_cat_id:
        params["category_id"] = selected_cat_id

    # Oculamos los productos inactivos automáticamente ya que el backend de GET /products ya lo hace
    products_data = get("/products", params=params)
    products = products_data if isinstance(products_data, list) else []

    if products:
        # Transformar a DataFrame para visualización
        df = pd.DataFrame(products)
        
        # Mapear category_id a nombre usando cat_options invertido
        id_to_cat = {v: k for k, v in cat_options.items() if v is not None}
        if "category_id" in df.columns:
            df["Categoría"] = df["category_id"].map(id_to_cat).fillna("Ninguna")
            columns_to_show = ["id", "name", "sku", "Categoría", "price", "stock_quantity", "min_stock_alert", "is_active"]
        else:
            columns_to_show = ["id", "name", "sku", "price", "stock_quantity", "min_stock_alert", "is_active"]
            
        # Filtrar solo columnas que sí devolvió la API (o que agregamos)
        existing_cols = [c for c in columns_to_show if c in df.columns]
        
        view_df = df[existing_cols].copy()
        
        # Renombrar en español para el usuario
        rename_map = {
            "id": "ID", "name": "Nombre", "sku": "SKU", 
            "price": "Precio ($)", "stock_quantity": "Stock Actual", 
            "min_stock_alert": "Alerta", "is_active": "Activo"
        }
        view_df.rename(columns={k: v for k, v in rename_map.items() if k in view_df.columns}, inplace=True)
        
        st.dataframe(view_df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay productos que coincidan con la búsqueda o el inventario está vacío.")

    st.divider()

    # --- 3. ACCIONES CRUD (TABS) ---
    tab_create, tab_edit, tab_delete = st.tabs(["➕ Agregar Producto", "✏️ Editar Producto", "🗑️ Desactivar Producto"])

    # Taba de Creación
    with tab_create:
        with st.form("create_product_form"):
            st.subheader("Nuevo Producto")
            c_name = st.text_input("Nombre *")
            c_desc = st.text_area("Descripción")
            
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                c_price = st.number_input("Precio ($) *", min_value=0.0, step=0.01)
                c_category_name = st.selectbox("Categoría Asociada", options=["Ninguna"] + [c["name"] for c in categories])
            with c_col2:
                c_stock = st.number_input("Stock Inicial", min_value=0, step=1)
                c_alert = st.number_input("Alerta Mínima", min_value=0, value=5, step=1)
            
            submitted_create = st.form_submit_button("Crear Producto", type="primary")
            
            if submitted_create:
                if not c_name:
                    st.error("El Nombre es obligatorio.")
                else:
                    import uuid
                    generated_sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
                    payload = {
                        "name": c_name,
                        "sku": generated_sku,
                        "description": c_desc if c_desc else None,
                        "price": c_price,
                        "stock_quantity": c_stock,
                        "min_stock_alert": c_alert,
                        "category_id": cat_options[c_category_name] if c_category_name != "Ninguna" else None
                    }
                    res = post("/products", payload)
                    if res and "id" in res:
                        st.success(f"Producto '{c_name}' creado exitosamente.")
                        st.rerun()
                    else:
                        st.error("Error al crear el producto.")

    # Tab de Edición
    with tab_edit:
        if products:
            prod_options = {f"{p['name']} (SKU: {p.get('sku', '')})": p for p in products}
            selected_edit_label = st.selectbox("Seleccione el producto a editar", options=list(prod_options.keys()))
            selected_prod = prod_options[selected_edit_label]
            
            with st.form("edit_product_form"):
                e_name = st.text_input("Nombre", value=selected_prod.get("name", ""))
                e_price = st.number_input("Precio ($)", min_value=0.0, value=float(selected_prod.get("price", 0.0)), step=0.01)
                e_alert = st.number_input("Alerta Mínima", min_value=0, value=int(selected_prod.get("min_stock_alert", 5)), step=1)
                
                submitted_edit = st.form_submit_button("Actualizar Producto")
                if submitted_edit:
                    payload_edit = {
                        "name": e_name,
                        "price": e_price,
                        "min_stock_alert": e_alert
                    }
                    res_edit = put(f"/products/{selected_prod['id']}", payload_edit)
                    if res_edit and "id" in res_edit:
                        st.success("Producto modificado correctamente.")
                        st.rerun()
                    else:
                        st.error("Error al actualizar.")
        else:
            st.warning("No hay productos disponibles para editar.")

    # Tab de Eliminación (Soft Delete)
    with tab_delete:
        if products:
            del_prod_options = {f"{p['name']}": p for p in products}
            selected_del_label = st.selectbox("Seleccione el producto a desactivar", options=list(del_prod_options.keys()))
            selected_del_prod = del_prod_options[selected_del_label]
            
            st.error(f"⚠️ Estás a punto de desactivar '{selected_del_prod['name']}'. Ya no aparecerá en ventas.")
            if st.button("Confirmar Desactivación", type="primary"):
                res_del = delete(f"/products/{selected_del_prod['id']}")
                if res_del and "message" in res_del:
                    st.success(res_del["message"])
                    st.rerun()
                else:
                    st.error("No se pudo desactivar el producto.")
        else:
            st.warning("No hay productos disponibles para desactivar.")
