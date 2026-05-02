# =============================================================================
# Configuración de la Base de Datos — Dual SQLite / PostgreSQL
# =============================================================================
# Soporta dos motores:
#   - SQLite  (desarrollo local, legacy): sqlite:///./stocky.db
#   - PostgreSQL / Supabase (producción): postgresql://...
# El motor se selecciona automáticamente según el DATABASE_URL del .env
# =============================================================================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 🔥 FIX: Render/Supabase a veces usan 'postgres://' que es incompatible con SQLAlchemy 2.0+
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ── Motor de base de datos ─────────────────────────────────────────────────
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite: requiere check_same_thread=False para entornos multi-hilo
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL / Supabase: pool de conexiones con pre-ping para reconexión automática
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,        # Verifica la conexión antes de usarla
        pool_size=5,               # Conexiones activas en el pool
        max_overflow=10            # Conexiones extra en picos de carga
    )

# ── Fábrica de sesiones ────────────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Clase base para los modelos ORM ───────────────────────────────────────
Base = declarative_base()

# ── Dependencia FastAPI: obtiene y cierra la sesión de BD ─────────────────
def get_db():
    """
    Generador de sesión de base de datos para inyección de dependencias en FastAPI.
    Abre la sesión antes del request y la cierra automáticamente al finalizar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
