#capa intermedia entre el frontend y el backend

import os
import httpx # Importamos httpx para hacer peticiones al backend
import streamlit as st # Importamos streamlit para usar st.secrets

# Prioridad: Variable de Entorno (Docker) > secrets.toml (Local) > Localhost default
try:
    _secret_url = st.secrets.get("API_URL") if hasattr(st, "secrets") else None
except Exception:
    _secret_url = None

def get_api_base_url():
    return os.environ.get("API_URL") or _secret_url or "http://127.0.0.1:8000"

API_BASE_URL = get_api_base_url()

#funcion para obtener datos del backend (estandar)
def get(endpoint: str, params: dict = None):
    try:
        response = httpx.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=10, follow_redirects=True)
        response.raise_for_status()
        return response.json()
    except (httpx.ConnectError, httpx.ConnectTimeout):
        st.error("No se puede conectar con el servidor. ¿Está el backend corriendo?")
        return None
    except httpx.ReadTimeout:
        st.error("El servidor tardó demasiado en responder (Timeout).")
        return None
    except httpx.HTTPStatusError as e:
        st.error(f"Error del servidor: {e.response.status_code}")
        return None
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
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
