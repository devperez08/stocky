import streamlit as st

def render():
    st.title("📊 Dashboard Principal")
    st.write("Resumen ejecutivo de tu inventario en tiempo real.")
    st.divider()

    # 1. Sección de Métricas (KPIs)
    st.subheader("Indicadores Clave")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total Productos", value="156", delta="12 este mes")
    with col2:
        st.metric(label="Categorías Activas", value="8", delta="1 nueva")
    with col3:
        st.metric(label="Valor Inventario", value="$45,230", delta="-$1,200")
    with col4:
        # delta_color="inverse" hace que si sube el valor sea rojo (malo) y si baja sea verde (bueno)
        st.metric(label="Alertas de Stock Mínimo", value="5", delta="2 nuevas", delta_color="inverse")

    st.divider()

    # 2. Sección de Gráficos y Tablas
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.subheader("📈 Movimientos (Últimos 5 días)")
        # Gráfico de barras simulado
        datos_grafico = {
            "Entradas": [10, 20, 15, 25, 30], 
            "Salidas": [5, 10, 8, 12, 15]
        }
        st.bar_chart(datos_grafico)
        
    with col_der:
        st.subheader("⚠️ Atención Requeria (Bajo Stock)")
        # Tabla de datos simulada
        datos_tabla = {
            "Producto": ["Zapatos Deportivos", "Camisa Polo", "Pantalón Jean", "Gorra Básica"],
            "Stock Actual": [2, 5, 1, 3],
            "Mínimo Ideal": [10, 10, 5, 5]
        }
        st.dataframe(datos_tabla, hide_index=True, use_container_width=True)

    st.info("💡 En los próximos sprints conectaremos estos gráficos a los datos reales de FastAPI.")