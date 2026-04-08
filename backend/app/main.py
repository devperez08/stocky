from fastapi import FastAPI
from backend.app.core.config import settings # Importamos la configuración globales
from fastapi.middleware.cors import CORSMiddleware # Importamos el middleware de CORS, seguridad

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

# Agregamos el middleware de CORS. predeterminado. uando el frontend intente pedirle datos al backend, el navegador lo bloqueará por seguridad, por eso usamos el middleware de CORS, para que pueda acceder. En producción (cuando la app sea real), en lugar de ["*"] (todos), pondremos la dirección exacta de la web por seguridad.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite el acceso desde cualquier origen
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos HTTP
    allow_headers=["*"], # Permite todos los encabezados
)


@app.get("/health")
def health_check():
    return {"status": "ok", "app_name": settings.APP_NAME}

@app.get("/")
def read_root():
    return {"message": f"¡Bienvenido a {settings.APP_NAME}"}
