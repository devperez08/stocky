import os
from dotenv import load_dotenv

# Cargamos las variables del archivo .env si existe
load_dotenv()

class Settings:
    """
    Configuración centralizada de la aplicación.
    Se ha simplificado para evitar dependencias externas como pydantic-settings
    que pueden fallar en entornos legacy como Windows 7.
    """
    APP_NAME: str = os.getenv("APP_NAME", "Stocky - Sistema de Inventarios")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./stocky.db")

# Creamos una instancia única para que toda la app la use
settings = Settings()