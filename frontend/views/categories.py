import streamlit as st
import pandas as pd
from utils.api_client import get, post

def render():
    st.title("📂 Categorías de Productos")
    st.write("Gestiona la clasificación de tu inventario. Crea nuevas familias o rubros para tus productos.")

    # --- CARGA DE DATOS ---
    with st.spinner("Cargando categorías..."):
        categories = get("/categories")
    
    # --- LAYOUT PRINCIPAL ---
    col1, col2 = st.columns([1, 1.5])
    
    # SECCIÓN: CREAR CATEGORÍA
    with col1:
        st.subheader("➕ Nueva Categoría")
        with st.form("category_form"):
            name = st.text_input("Nombre de la Categoría (*)", placeholder="Ej: Herramientas, Mascotas...")
            description = st.text_area("Descripción", placeholder="Breve descripción opcional", max_chars=200)
            
            submitted = st.form_submit_button("Guardar Categoría", type="primary")
            
            if submitted:
                if not name.strip():
                    st.error("El nombre es obligatorio.")
                else:
                    payload = {
                        "name": name.strip(),
                        "description": description.strip() if description else None
                    }
                    result = post("/categories", payload)
                    if result:
                        st.success(f"¡Categoría '{name}' creada con éxito!")
                        st.experimental_rerun()  # Recarga la página para mostrar la nueva categoría
    
    # SECCIÓN: LISTADO DE CATEGORÍAS
    with col2:
        st.subheader("📋 Categorías Registradas")
        
        if categories and isinstance(categories, list) and len(categories) > 0:
            # Convertimos la lista de JSON a DataFrame para usar st.dataframe
            df = pd.DataFrame(categories)
            
            # Limpieza y filtrado para mostrar solo en UI (PRO-66 compliance)
            df_display = df.copy()
            
            # Filtramos solo activos (opcional, si hay soporte para desactivar en un futuro)
            if "is_active" in df_display.columns:
                df_display = df_display[df_display["is_active"] == True]
            
            # Renombramos columnas a nombres amigables
            rename_map = {
                "id": "ID",
                "name": "Nombre",
                "description": "Descripción"
            }
            # Solo renombramos si la columna existe
            columns_to_keep = [col for col in ["id", "name", "description"] if col in df_display.columns]
            df_display = df_display[columns_to_keep].rename(columns=rename_map)
            
            # Llenar huecos vacíos
            df_display.fillna("", inplace=True)
            
            st.dataframe(
                df_display, 
                 
                use_container_width=True
            )
            st.caption(f"Total: {len(df_display)}")
            
        else:
            st.info("No hay categorías registradas aún. ¡Añade una en el formulario!")
