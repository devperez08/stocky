from sqlalchemy import create_engine # create_all para crear las tablas en la base de datos, create_engine para crear la conexión a la base de datos
from sqlalchemy.ext.declarative import declarative_base # declarative_base para crear la clase base de los modelos
from sqlalchemy.orm import sessionmaker # sessionmaker para crear la fábrica de sesiones
from backend.app.core.config import settings # Importamos la configuración global

# 1. Definimos dónde estará el archivo de la base de datos desde la config
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 2. Creamos el motor (Engine)
# 'check_same_thread=False' es solo necesario para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Creamos la fábrica de sesiones (para hacer consultas)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Esta es la clase base de la que heredarán todos nuestros modelos
Base = declarative_base()

#ESTANDAR UNIVERSAL PARA QUE FASTAPI PUEDA CONECTARSE A LA BASE DE DATOS

# 5. Dependencia para obtener la sesión de la base de datos (get_db)
# Esta función es un "generador": abre la conexión, la entrega y la cierra al final.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


