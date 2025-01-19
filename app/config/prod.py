from pydantic import Field, ConfigDict
from ..config import Settings as BaseSettings

class Settings(BaseSettings):
    """Production settings"""
    ENVIRONMENT: str = Field(default="prod")
    MONGODB_URL: str = Field(default="mongodb://localhost:27017")  # Será sobrescrito pela variável de ambiente MONGODB_URL
    JWT_SECRET: str = Field(default="your-production-secret-key")  # Será sobrescrito pela variável de ambiente JWT_SECRET
    LOG_LEVEL: str = Field(default="INFO")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    DATABASE_NAME: str = Field(default="investimentos")

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"  # Permite campos extras
    )
