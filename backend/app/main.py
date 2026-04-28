from fastapi import FastAPI
from backend.app.core.config import settings # Importamos la configuración globales
from fastapi.middleware.cors import CORSMiddleware # Importamos el middleware de CORS, seguridad
# --- IMPORTACIONES DE BD ---
from backend.app.core.database import Base, engine
# Importante: Importar los modelos para que Base.metadata los reconozca
from backend.app.models import store, user, supplier, category, product, movement

# --- IMPORTACIONES DE ROUTERS ---
from backend.app.routers import product, category, movement, stats, reports

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

# 🔥 Registro de Routers
app.include_router(product.router)
app.include_router(category.router)
app.include_router(movement.router)
app.include_router(stats.router)
app.include_router(reports.router)

# 🔥 Crear las tablas automáticamente al arrancar
@app.on_event("startup")
def startup_db():
    # 1. Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    # 2. Migración manual para unit_price (PRO-71)
    # Útil para sistemas legacy donde no hay Alembic configurado aún.
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            # Verificamos si la columna existe en SQLite
            result = conn.execute(text("PRAGMA table_info(movements)"))
            columns = [row[1] for row in result]
            
            if "unit_price" not in columns:
                print("🔧 Migrando: Agregando columna 'unit_price' a la tabla 'movements'...")
                conn.execute(text("ALTER TABLE movements ADD COLUMN unit_price FLOAT DEFAULT 0.0"))
                conn.commit()
                print("✅ Columna 'unit_price' añadida exitosamente.")
            else:
                print("✔️ La columna 'unit_price' ya existe en 'movements'.")
        except Exception as e:
            print(f"⚠️ Error en migración automática: {e}")

# Agregamos el middleware de CORS (predeterminado).
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
