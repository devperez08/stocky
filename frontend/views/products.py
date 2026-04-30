import streamlit as st
import pandas as pd
import uuid
import io
from utils.api_client import get, post, put, delete, post_file

def render():
    st.title("📦 Gestión de Productos")
    st.write("Administra el catálogo: crea nuevos productos, actualiza datos o importa masivamente.")

    # --- 1. CARGA DE DATOS INICIAL ---
    # Necesitamos las categorías para los formularios
    cat_data = get("/categories")
    categories = cat_data if isinstance(cat_data, list) else []
    cat_options = {"Todas": None}
    for c in categories:
        cat_options[c["name"]] = c["id"]

    # --- 2. ACCIONES CRUD Y OPERACIONES (TOP) ---
    tab_create, tab_edit, tab_delete = st.tabs(["➕ Agregar Producto", "✏️ Editar Producto", "🗑️ Desactivar Producto"])

    # Tab de Creación
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
                    auto_sku = f"PROD-{uuid.uuid4().hex[:8].upper()}"
                    payload = {
                        "name": c_name, "sku": auto_sku,
                        "description": c_desc if c_desc else None,
                        "price": c_price, "stock_quantity": c_stock,
                        "min_stock_alert": c_alert,
                        "category_id": cat_options[c_category_name] if c_category_name != "Ninguna" else None
                    }
                    res = post("/products", payload)
                    if res and "id" in res:
                        st.success(f"Producto '{c_name}' creado exitosamente.")
                        st.rerun()

    # Tab de Edición
    # Cargamos productos para los selectboxes
    products_all = get("/products") or []
    with tab_edit:
        if products_all:
            prod_options = {f"{p['name']} (SKU: {p.get('sku', '')})": p for p in products_all}
            selected_edit_label = st.selectbox("Seleccione el producto a editar", options=list(prod_options.keys()))
            selected_prod = prod_options[selected_edit_label]
            
            with st.form("edit_product_form"):
                e_name = st.text_input("Nombre", value=selected_prod.get("name", ""))
                e_sku = selected_prod.get("sku", "")
                e_price = st.number_input("Precio ($)", min_value=0.0, value=float(selected_prod.get("price", 0.0)), step=0.01)
                e_alert = st.number_input("Alerta Mínima", min_value=0, value=int(selected_prod.get("min_stock_alert", 5)), step=1)
                
                submitted_edit = st.form_submit_button("Actualizar Producto")
                if submitted_edit:
                    payload_edit = {"name": e_name, "sku": e_sku, "price": e_price, "min_stock_alert": e_alert}
                    res_edit = put(f"/products/{selected_prod['id']}", payload_edit)
                    if res_edit and "id" in res_edit:
                        st.success("Producto modificado correctamente.")
                        st.rerun()
        else:
            st.warning("No hay productos disponibles para editar.")

    with tab_delete:
        if products_all:
            del_prod_options = {f"{p['name']} (SKU: {p.get('sku', '')})": p for p in products_all}
            selected_del_label = st.selectbox("Seleccione el producto a desactivar", options=list(del_prod_options.keys()))
            selected_del_prod = del_prod_options[selected_del_label]
            
            st.error(f"⚠️ Estás a punto de desactivar '{selected_del_prod['name']}'.")
            if st.button("Confirmar Desactivación", type="primary"):
                res_del = delete(f"/products/{selected_del_prod['id']}")
                if res_del:
                    st.success("Producto desactivado.")
                    st.rerun()
        else:
            st.warning("No hay productos para desactivar.")

    # --- 3. IMPORTACIÓN (TOP) ---
    with st.expander("📂 Importar Productos desde Excel"):
        st.info("Sube un archivo Excel para crear o actualizar productos masivamente.")
        template_df = pd.DataFrame(columns=["sku", "name", "price", "description", "stock_quantity", "min_stock_alert", "category"])
        template_bytes = io.BytesIO()
        template_df.to_excel(template_bytes, index=False)
        st.download_button("📥 Descargar Plantilla", data=template_bytes.getvalue(), file_name="plantilla_stocky.xlsx")

        uploaded_file = st.file_uploader("Archivo Excel", type=["xlsx", "xls"])
        if uploaded_file and st.button("🚀 Iniciar Importación"):
            result = post_file("/products/import", file=uploaded_file)
            if result:
                st.success("Importación finalizada.")
                st.rerun()

    st.divider()

    # --- 4. TABLA DE PRODUCTOS Y FILTROS (BOTTOM) ---
    st.subheader("📋 Catálogo de Productos")
    f_col1, f_col2 = st.columns([3, 1])
    with f_col1:
        search_name = st.text_input("Buscar por nombre...", placeholder="Ej: Café...")
    with f_col2:
        selected_cat_name = st.selectbox("Filtrar por Categoría", options=list(cat_options.keys()))
        selected_cat_id = cat_options[selected_cat_name]

    params = {}
    if search_name: params["name"] = search_name
    if selected_cat_id: params["category_id"] = selected_cat_id

    products_view = get("/products", params=params) or []
    if products_view:
        df = pd.DataFrame(products_view)
        id_to_cat = {v: k for k, v in cat_options.items() if v is not None}
        if "category_id" in df.columns:
            df["Categoría"] = df["category_id"].map(id_to_cat).fillna("Ninguna")
            cols = ["id", "name", "sku", "Categoría", "price", "stock_quantity", "min_stock_alert"]
        else:
            cols = ["id", "name", "sku", "price", "stock_quantity", "min_stock_alert"]
        
        view_df = df[[c for c in cols if c in df.columns]].copy()
        view_df.rename(columns={
            "id": "ID", "name": "Nombre", "price": "Precio ($)", 
            "stock_quantity": "Stock", "min_stock_alert": "Alerta"
        }, inplace=True)
        if "sku" in view_df.columns: view_df.drop(columns=["sku"], inplace=True)
        st.dataframe(view_df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay productos que mostrar.")
