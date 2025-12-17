from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str
    MONGO_URL: str
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()