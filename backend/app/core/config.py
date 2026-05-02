from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Definimos qué variables queremos. Si no están en el .env, usarán estos valores por defecto.
    APP_NAME: str = "Stocky - Sistema de Inventarios"
    API_V1_STR: str = "/api/v1"
    
    # Base de Datos
    DATABASE_URL: str = "sqlite:///./stocky.db"

    # Seguridad y JWT
    SECRET_KEY: str = "8sWNn3WWVHVrnNwK_CHANGE_ME_IN_PRODUCTION" # Placeholder seguro
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas

    # Esto le dice a Pydantic que busque un archivo llamado ".env" en la raíz
    model_config = SettingsConfigDict(env_file=".env")

# Creamos una instancia única para que toda la app la use
settings = Settings()