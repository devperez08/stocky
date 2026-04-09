from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Definimos qué variables queremos. Si no están en el .env, usarán estos valores por defecto.
    APP_NAME: str = "Stocky - Sistema de Inventarios"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./stocky.db"

    # Esto le dice a Pydantic que busque un archivo llamado ".env" en la raíz
    model_config = SettingsConfigDict(env_file=".env")
# Creamos una instancia única para que toda la app la use
settings = Settings()