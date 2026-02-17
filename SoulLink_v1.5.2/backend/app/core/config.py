# /backend/app/core/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Locate the .env file relative to this script
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "SoulLink"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    DATABASE_URL: str = f"postgresql://postgres:{os.getenv('SOULLINK_DB_PASS')}@localhost:5432/soullink"

settings = Settings()