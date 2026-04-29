import os
# Додаємо SettingsConfigDict в імпорт з pydantic_settings
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.security import OAuth2PasswordBearer

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-ipz-33-at-least-32-chars-long")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://user:password@library_db:5432/library_db"
    )
    
    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    # Тепер NameError зникне
    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings()