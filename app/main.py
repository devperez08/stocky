"""
¿Por qué usamos `lifespan` en lugar de @app.on_event("startup")?
`@app.on_event` está deprecado desde FastAPI 0.93.
`lifespan` es el patrón moderno: un context manager que maneja startup y shutdown
en un solo lugar, con soporte nativo para async y limpieza de recursos garantizada.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.routers import products


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: crea todas las tablas definidas en los modelos ORM si no existen.
    En producción, esto se reemplazaría por migraciones con Alembic.
    Shutdown: aquí iría el cierre de conexiones, colas, etc.
    """
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup al apagar (por ahora no necesitamos nada extra)


app = FastAPI(
    title="Stocky API",
    version="1.0.0",
    description="Sistema de gestión de inventario",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Restringir a dominios específicos en producción
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(products.router)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}