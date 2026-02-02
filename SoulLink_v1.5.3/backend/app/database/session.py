# /backend/app/database/session.py
# /version.py
# /_dev/

# "I am the box. I am the logic."
# - GLaDOS - Portal

from sqlmodel import Session, create_engine
from backend.app.core.config import settings

# 🔌 The Smart Engine
# We only need check_same_thread for SQLite. 
# If DATABASE_URL starts with 'postgresql', we skip it.

connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url, 
    echo=False, 
    connect_args=connect_args
)

def get_session():
    """Dependency for FastAPI to inject DB sessions."""
    with Session(engine) as session:
        yield session