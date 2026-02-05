# /_dev/scripts/init_db.py
# /version.py

# "Let there be light."

import sys
import os

# Add the root directory to the path so we can find 'backend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlmodel import SQLModel
from backend.app.database.session import engine
# We MUST import the models here so SQLModel knows they exist
from backend.app.models.soul import Soul
from backend.app.models.location import Location
from backend.app.models.user import User
from backend.app.models.relationship import SoulRelationship
from backend.app.models.conversation import Conversation

def create_db_and_tables():
    print("🏗️  Legion Engine: Constructing the Skeleton...")
    SQLModel.metadata.create_all(engine)
    print("✅  Genesis Complete: Tables created.")

if __name__ == "__main__":
    create_db_and_tables()