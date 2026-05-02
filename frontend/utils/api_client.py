import os
import httpx
import streamlit as st

# Prioridad: Variable de Entorno (Docker) > secrets.toml (Local) > Localhost default
try:
    _secret_url = st.secrets.get("API_URL") if hasattr(st, "secrets") else None
except Exception:
    _secret_url = None

def get_api_base_url():
    return os.environ.get("API_URL") or _secret_url or "http://127.0.0.1:8000"

API_BASE_URL = get_api_base_url()

def _build_headers() -> dict:
    headers = {"Accept": "application/json"}
    token = st.session_state.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _clear_auth_session() -> None:
    for key in ("token", "store_name", "days_remaining", "plan_status"):
        st.session_state.pop(key, None)


def _handle_http_error(error: httpx.HTTPStatusError, endpoint: str, show_error: bool) -> None:
    status_code = error.response.status_code
    if status_code == 401:
        _clear_auth_session()
        if show_error:
            st.warning("Tu sesion expiro o es invalida. Inicia sesion nuevamente.")
        st.rerun()
    
    # Interceptar bloqueo por suscripción expirada
    if status_code == 403:
        try:
            detail = error.response.json().get("detail", {})
            if isinstance(detail, dict) and detail.get("error") == "subscription_expired":
                st.session_state["subscription_expired"] = True
                st.session_state["expiry_detail"] = detail
                st.rerun()
        except Exception:
            pass

    if show_error:
        st.error(f"Error {status_code} en {endpoint}: {error.response.text}")


def _request(method: str, endpoint: str, timeout: int = 10, show_error: bool = True, **kwargs):
    try:
        response = httpx.request(
            method=method,
            url=f"{API_BASE_URL}{endpoint}",
            timeout=timeout,
            follow_redirects=True,
            headers={**_build_headers(), **kwargs.pop("headers", {})},
            **kwargs,
        )
        response.raise_for_status()
        return response.json() if response.content else {}
    except (httpx.ConnectError, httpx.ConnectTimeout):
        if show_error:
            st.error("No se puede conectar con el servidor. ¿Esta el backend corriendo?")
    except httpx.ReadTimeout:
        if show_error:
            st.error("El servidor tardo demasiado en responder (timeout).")
    except httpx.HTTPStatusError as error:
        _handle_http_error(error, endpoint, show_error)
    except Exception as error:
        if show_error:
            st.error(f"Error inesperado en {endpoint}: {error}")
    return None


def get(endpoint: str, params: dict = None, show_error: bool = True):
    return _request("GET", endpoint, params=params, show_error=show_error)


def post(endpoint: str, data: dict = None, show_error: bool = True):
    return _request("POST", endpoint, json=data, show_error=show_error)


def post_form(endpoint: str, data: dict = None, show_error: bool = True):
    return _request(
        "POST",
        endpoint,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        show_error=show_error,
    )


def put(endpoint: str, data: dict = None, show_error: bool = True):
    return _request("PUT", endpoint, json=data, show_error=show_error)


def delete(endpoint: str, show_error: bool = True):
    return _request("DELETE", endpoint, show_error=show_error)


def post_file(endpoint: str, file, show_error: bool = True):
    files = {"file": (file.name, file.getvalue(), file.type)}
    return _request("POST", endpoint, files=files, timeout=30, show_error=show_error)
