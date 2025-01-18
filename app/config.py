from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Ambiente (local ou prod)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    
    # Configurações do MongoDB
    MONGODB_URL: str = os.getenv(
        "MONGODB_URL",
        "mongodb://localhost:27017"  # URL padrão para MongoDB local
    )
    DATABASE_NAME: str = "investimentos"
    
    # Configurações de autenticação
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-for-local-dev")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Azure Key Vault (apenas para produção)
    KEY_VAULT_URL: Optional[str] = None
    
    # Configurações de Log
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
