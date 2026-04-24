from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Stocky - Sistema de Inventarios"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./stocky.db"

    class Config:
        env_file = ".env"

# Creamos una instancia única para que toda la app la use
settings = Settings()