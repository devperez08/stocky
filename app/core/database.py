"""
¿Por qué este archivo?
SQLAlchemy necesita dos cosas para operar:
1. Un *Engine* (la conexión a la DB).
2. Una *Session* (la unidad de trabajo por request).

Separamos esto en `core/database.py` para que cualquier servicio
pueda recibir una sesión via Dependency Injection sin necesitar
saber NADA sobre la configuración de la base de datos.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# El Engine es la "puerta de entrada" a la DB.
# `check_same_thread=False` solo es necesario para SQLite en FastAPI
# porque FastAPI puede usar múltiples threads para manejar requests.
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Solo para SQLite
)

# SessionLocal es la *fábrica* de sesiones. Cada request obtendrá su propia sesión.
# autocommit=False → los cambios no se guardan hasta que llamemos a session.commit()
# autoflush=False  → no se sincronizan cambios a la DB hasta el commit
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base declarativa: todos nuestros modelos ORM heredarán de aquí.
class Base(DeclarativeBase):
    pass


def get_db():
    """
    Generador de sesión de DB para Dependency Injection.

    ¿Por qué un generador con try/finally?
    Para GARANTIZAR que la sesión se cierre al final del request,
    incluso si ocurre una excepción. Evita conexiones abiertas (memory leaks).
    FastAPI detecta automáticamente que es un generador y lo maneja correctamente.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
