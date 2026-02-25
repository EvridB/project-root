from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://repair:repairpass@db/repair"

    class Config:
        env_file = ".env"

settings = Settings()