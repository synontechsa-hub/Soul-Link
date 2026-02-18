"""
insert_architect_v156.py
Inserts the Architect god-mode account into the users table.
Safe to re-run — uses INSERT ... ON CONFLICT DO UPDATE.

Usage:
    python insert_architect_v156.py
"""
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.session import engine
from backend.app.models.user import User
from sqlmodel import Session

ARCHITECT_UUID = "14dd612d-744e-487d-b2d5-cc47732183d3"
ARCHITECT_EMAIL = "brc.grdn@gmail.com"

def insert():
    print(f"Inserting Architect account: {ARCHITECT_UUID}")

    with Session(engine) as session:
        existing = session.get(User, ARCHITECT_UUID)

        if existing:
            # Update to ensure full god-mode config
            existing.username = "the_architect"
            existing.display_name = "The Architect"
            existing.account_tier = "architect"
            existing.gems = 99999
            existing.energy = 9999
            existing.subscription_status = "active"
            session.add(existing)
            print("  -> Existing row found. Updated to full god-mode.")
        else:
            architect = User(
                user_id=ARCHITECT_UUID,
                username="the_architect",
                display_name="The Architect",
                account_tier="architect",
                gems=99999,
                energy=9999,
                lifetime_tokens_used=0,
                current_location="linkside_apartment",
                current_time_slot="morning",
                subscription_status="active",
                subscription_start=datetime.utcnow(),
                created_at=datetime.utcnow(),
                last_energy_refill=datetime.utcnow(),
            )
            session.add(architect)
            print("  -> New row inserted.")

        session.commit()
        print(f"\nDone. Architect account ({ARCHITECT_EMAIL}) is live.")
        print(f"  user_id:      {ARCHITECT_UUID}")
        print(f"  account_tier: architect")
        print(f"  gems:         99999")
        print(f"  energy:       9999")

if __name__ == "__main__":
    insert()
