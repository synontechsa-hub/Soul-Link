# /backend/app/core/config.py

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Identity (Linked to your version.py)
    app_name: str = "SoulLink"
    
    # Secrets
    groq_api_key: str
    database_url: str
    
    # Flags
    debug: bool = False

    # Tell Pydantic to look for a .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore' # Ignores extra variables in .env
    )

# Create a singleton instance to be used everywhere
settings = Settings()