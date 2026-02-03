# /backend/app/core/config.py
# /version.py v1.5.3-P

import os
from pydantic import Field
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
    
    # --- FLAGS ---
    debug: bool = Field(default=False, validation_alias='SOULLINK_DEBUG')

    # THE FIX: Point to root .env relative to this file's location.
    # backend/app/core/config.py -> ../../../.env reaches root.
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../../.env"),
        env_file_encoding='utf-8',
        extra='ignore'
    )

# Create a singleton instance to be used everywhere
settings = Settings()