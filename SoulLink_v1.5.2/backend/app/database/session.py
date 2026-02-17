# /backend/app/database/session.py
# /version.py
# /_dev/

# “Even in dark times, we must shine our light.”
# - Dragon Age: Inquisition

import os
from sqlmodel import SQLModel, create_engine, Session

# Import the Architects of the Soul
# This ensures SQLModel knows to create these tables!
from ..models.soul import Soul
from ..models.location import Location
from ..models.user import User
from ..models.relationship import SoulRelationship
from ..models.conversation import Conversation

# 🛡️ Get the password from your environment variable
db_password = os.environ.get("SOULLINK_DB_PASS")

if not db_password:
    print("❌ ERROR: Database password not found in environment variables!")
    DATABASE_URL = "postgresql://postgres@localhost:5432/soullink" 
else:
    DATABASE_URL = f"postgresql://postgres:{db_password}@localhost:5432/soullink"
    # Oh yeah! That's locked up tighter than Diddy is at the moment!

# “I know what you’re thinking, and it’s crazy…
# Unfortunately for us both, I like crazy.”
# - Cortana
engine = create_engine(DATABASE_URL, echo=False)

# “The cake is a lie.”
# - Portal
def create_db_and_tables():
    """Initializes the database schema."""
    # This is the big red button that builds the city
    SQLModel.metadata.create_all(engine)

# "Stay awhile and listen."
# - Deckard Cain - Diablo
def get_session():
    with Session(engine) as session:
        yield session