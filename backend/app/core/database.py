from sqlalchemy import create_engine # create_all para crear las tablas en la base de datos, create_engine para crear la conexión a la base de datos
from sqlalchemy.ext.declarative import declarative_base # declarative_base para crear la clase base de los modelos
from sqlalchemy.orm import sessionmaker # sessionmaker para crear la fábrica de sesiones

# 1. Definimos dónde estará el archivo de la base de datos
SQLALCHEMY_DATABASE_URL = "sqlite:///./stocky.db"

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


