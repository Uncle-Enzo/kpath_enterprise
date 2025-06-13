"""
KPATH Enterprise Configuration Module
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = "postgresql://localhost/kpath_enterprise"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # FAISS Configuration
    faiss_index_path: str = "./faiss_indexes"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Development
    debug: bool = False
    reload: bool = False
    
    # Cache Configuration
    cache_ttl_embeddings: int = 86400  # 24 hours
    cache_ttl_results: int = 3600      # 1 hour
    
    # Search Configuration
    search_limit_default: int = 10
    search_limit_max: int = 100
    search_min_score: float = 0.5
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
