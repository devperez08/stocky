# Frontend Dockerfile - Stocky
FROM python:3.12-slim

WORKDIR /app

# Copiamos requerimientos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto de Streamlit
EXPOSE 8501

# Configuramos variables de entorno para Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Comando para ejecutar la interfaz
CMD ["streamlit", "run", "frontend/app.py"]
