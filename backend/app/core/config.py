from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str
    MONGO_URL: str
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Control de creación de admin
    ALLOW_ADMIN_CREATION: bool = False

    # Cloudinary (Image Upload)
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # CORS origins (separados por comas)
    CORS_ORIGINS: str = "http://localhost:5173"

    # URLs
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"

    # Environment
    ENVIRONMENT: str = "development"

    # Wompi Payment Gateway
    WOMPI_PUBLIC_KEY: str = ""
    WOMPI_PRIVATE_KEY: str = ""
    WOMPI_EVENTS_SECRET: str = ""
    WOMPI_ENV: str = "sandbox"  # sandbox o production

    # SendGrid (Email Service)
    SENDGRID_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@calero.com"
    EMAIL_FROM_NAME: str = "CALERO"

    class Config:
        env_file = ".env"

settings = Settings()