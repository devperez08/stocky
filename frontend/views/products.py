import streamlit as st
import pandas as pd
import uuid
import io
from utils.api_client import get, post, put, delete, post_file

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
            "id": "ID", "name": "Nombre",
            "price": "Precio ($)", "stock_quantity": "Stock Actual", 
            "min_stock_alert": "Alerta", "is_active": "Activo"
        }
        # Nota: SKU está oculto momentáneamente (PRO-77)
        view_df.rename(columns={k: v for k, v in rename_map.items() if k in view_df.columns}, inplace=True)
        
        # Quitamos el SKU de la vista
        if "sku" in view_df.columns:
            view_df = view_df.drop(columns=["sku"])
        
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
            # SKU removido momentáneamente (AUTO-generado)
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
                    # Autogeneramos SKU único para el backend
                    auto_sku = f"PROD-{uuid.uuid4().hex[:8].upper()}"
                    payload = {
                        "name": c_name,
                        "sku": auto_sku,
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
                        st.error("Error al crear el producto. ¿SKU duplicado?")

    # Tab de Edición
    with tab_edit:
        if products:
            prod_options = {f"{p['name']} (SKU: {p.get('sku', '')})": p for p in products}
            selected_edit_label = st.selectbox("Seleccione el producto a editar", options=list(prod_options.keys()))
            selected_prod = prod_options[selected_edit_label]
            
            with st.form("edit_product_form"):
                e_name = st.text_input("Nombre", value=selected_prod.get("name", ""))
                # SKU Oculto (Mantenemos el valor original)
                e_sku = selected_prod.get("sku", "")
                e_price = st.number_input("Precio ($)", min_value=0.0, value=float(selected_prod.get("price", 0.0)), step=0.01)
                e_alert = st.number_input("Alerta Mínima", min_value=0, value=int(selected_prod.get("min_stock_alert", 5)), step=1)
                
                submitted_edit = st.form_submit_button("Actualizar Producto")
                if submitted_edit:
                    payload_edit = {
                        "name": e_name,
                        "sku": e_sku,
                        "price": e_price,
                        "min_stock_alert": e_alert
                    }
                    res_edit = put(f"/products/{selected_prod['id']}", payload_edit)
                    if res_edit and "id" in res_edit:
                        st.success("Producto modificado correctamente.")
                        st.rerun()
                    else:
                        st.error("Error al actualizar. Verifica que el SKU no choque con otro.")
        else:
            st.warning("No hay productos disponibles para editar.")

    # Tab de Eliminación (Soft Delete)
    with tab_delete:
        if products:
            del_prod_options = {f"{p['name']} (SKU: {p.get('sku', '')})": p for p in products}
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

    st.divider()

    # --- 4. IMPORTAR DESDE EXCEL ---
    with st.expander("📂 Importar Productos desde Excel"):
        st.info("El archivo debe tener las columnas: **sku**, **name**, **price** (mínimo). "
                "Los productos existentes (mismo SKU) se actualizarán. Los nuevos se crearán. "
                "Ningún producto será eliminado.")

        # Botón de descarga de plantilla
        template_df = pd.DataFrame(columns=["sku", "name", "price", "description", "stock_quantity", "min_stock_alert", "category"])
        template_bytes = io.BytesIO()
        template_df.to_excel(template_bytes, index=False)
        st.download_button("📥 Descargar Plantilla Excel", data=template_bytes.getvalue(),
                           file_name="plantilla_importacion_stocky.xlsx")

        uploaded_file = st.file_uploader("Selecciona el archivo Excel", type=["xlsx", "xls"])
        if uploaded_file and st.button("🚀 Iniciar Importación"):
            result = post_file("/products/import", file=uploaded_file)
            if result:
                import_col1, import_col2, import_col3 = st.columns(3)
                import_col1.metric("✅ Creados", result.get("created", 0))
                import_col2.metric("🔄 Actualizados", result.get("updated", 0))
                import_col3.metric("⚠️ Omitidos", result.get("skipped", 0))
                if result.get("errors"):
                    st.warning("Filas con errores:")
                    for err in result["errors"]:
                        st.caption(f"Fila {err['row']}: {err['error']}")
