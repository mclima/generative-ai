from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # API Keys
    openai_api_key: str = ""
    
    # MCP
    mcp_stock_data_url: str = ""
    mcp_news_url: str = ""
    mcp_market_data_url: str = ""
    
    # Logging
    log_level: str = "INFO"
    
    # Monitoring
    environment: str = "development"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
