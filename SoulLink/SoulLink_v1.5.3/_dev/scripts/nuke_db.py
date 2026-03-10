# /_dev/scripts/nuke_db.py
import sys
import os
from pathlib import Path

# Path setup
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import SQLModel
from backend.app.database.session import engine
# Import all models so SQLModel knows what to drop
from backend.app.models.soul import Soul
from backend.app.models.location import Location
from backend.app.models.user import User
from backend.app.models.relationship import SoulRelationship
from backend.app.models.conversation import Conversation

def nuke():
    print("RAZING THE CITY...")
    SQLModel.metadata.drop_all(engine)
    print("The old world is gone. The slate is clean.")

if __name__ == "__main__":
    nuke()