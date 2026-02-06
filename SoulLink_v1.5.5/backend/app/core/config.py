# /backend/app/core/config.py
# /version.py v1.5.4 Arise

import os
from typing import Optional
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Identity
    app_name: str = "SoulLink"
    
    # --- SECRETS & CONFIG ---
    # We use validation_alias to map root .env keys to our internal fields.
    
    groq_api_key: str = Field(validation_alias='GROQ_API_KEY')
    database_url: str = Field(validation_alias='SUPABASE_DB_URL')
    supabase_url: str = Field(validation_alias='SUPABASE_URL')
    supabase_anon_key: str = Field(validation_alias='SUPABASE_ANON_KEY')
    
    # User Configuration
    architect_uuid: Optional[str] = Field(default=None, validation_alias='ARCHITECT_UUID')
    
    # --- REDIS / CACHING ---
    redis_url: Optional[str] = Field(
        default=None, 
        validation_alias=AliasChoices('REDIS_URL', 'UPSTASH_REDIS_URL')
    )
    upstash_redis_rest_url: Optional[str] = Field(default=None, validation_alias='UPSTASH_REDIS_REST_URL')
    upstash_redis_rest_token: Optional[str] = Field(default=None, validation_alias='UPSTASH_REDIS_REST_TOKEN')
    
    enable_redis_cache: bool = Field(default=False, validation_alias='ENABLE_REDIS_CACHE')
    
    # --- RATE LIMITING ---
    enable_rate_limiting: bool = Field(default=True, validation_alias='ENABLE_RATE_LIMITING')
    rate_limit_storage: str = Field(default="memory://", validation_alias='RATE_LIMIT_STORAGE')
    
    # --- FLAGS ---
    debug: bool = Field(default=False, validation_alias='SOULLINK_DEBUG')
    environment: str = Field(default="development", validation_alias='ENVIRONMENT')  # development, staging, production
    
    # Sentry (Error Monitoring)
    sentry_dsn: Optional[str] = Field(default=None, validation_alias='SENTRY_DSN')

    # THE FIX: Point to root .env relative to this file's location.
    # backend/app/core/config.py -> ../../../.env reaches root.
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../../.env"),
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

# Create a singleton instance to be used everywhere
Settings.model_rebuild()
settings = Settings()