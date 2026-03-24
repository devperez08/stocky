from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Stocky API"
    DATABASE_URL: str = "sqlite:///./sql_app.db"

    class Config:
        env_file = ".env"

settings = Settings()
