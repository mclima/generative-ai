from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    openai_api_key: str = ""
    rapidapi_key: str = ""
    database_url: str = "postgresql://user:password@localhost:5432/techjobboard"
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
