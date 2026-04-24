#capa intermedia entre el frontend y el backend

import os
import httpx # Importamos httpx para hacer peticiones al backend
import streamlit as st # Importamos streamlit para usar st.secrets

# Fallback para versiones antiguas de Streamlit en Win7
try:
    _secret_url = st.secrets.get("API_URL")
except Exception:
    _secret_url = None

API_BASE_URL = os.environ.get("API_URL") or _secret_url or "http://localhost:8000"

#funcion para obtener datos del backend (estandar)
def get(endpoint: str, params: dict = None):
    try:
        response = httpx.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=10, follow_redirects=True)
        response.raise_for_status()
        return response.json()
    except httpx.ConnectError:
        st.error("No se puede conectar con el servidor. ¿Está el backend corriendo?")
        return None
    except httpx.HTTPStatusError as e:
        st.error(f"Error del servidor: {e.response.status_code}")
        return None

def post(endpoint: str, data: dict = None):
    """Para ENVIAR datos nuevos (Crear)"""
    try:
        response = httpx.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=10, follow_redirects=True)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error al crear en {endpoint}: {str(e)}")
        return None

def put(endpoint: str, data: dict = None):
    """Para ACTUALIZAR datos existentes (Editar)"""
    try:
        response = httpx.put(f"{API_BASE_URL}{endpoint}", json=data, timeout=10, follow_redirects=True)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error al actualizar en {endpoint}: {str(e)}")
        return None

def delete(endpoint: str):
    """Para BORRAR datos"""
    try:
        response = httpx.delete(f"{API_BASE_URL}{endpoint}", timeout=10, follow_redirects=True)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error al eliminar en {endpoint}: {str(e)}")
        return None
# NOTA TÉCNICA: Este módulo es un estándar en el desarrollo profesional (Capa de Servicio/Cliente).
# Se utiliza para centralizar la comunicación entre el Frontend y el Backend, permitiendo 
# realizar operaciones CRUD (Create, Read, Update, Delete) de forma segura y organizada.
