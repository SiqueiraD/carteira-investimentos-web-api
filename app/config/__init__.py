import os
from functools import lru_cache
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Base settings"""
    ENVIRONMENT: str = Field(default="local")
    MONGODB_URL: str = Field(default="mongodb://localhost:27017")
    JWT_SECRET: str = Field(default="your-secret-key")
    LOG_LEVEL: str = Field(default="INFO")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    DATABASE_NAME: str = Field(default="investimentos")

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"  # Permite campos extras
    )

@lru_cache()
def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "local")
    if env == "prod":
        from .prod import Settings as ProdSettings
        return ProdSettings()
    return Settings()
