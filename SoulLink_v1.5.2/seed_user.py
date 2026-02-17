# /seed_user.py
import os
from sqlmodel import Session, create_engine, select
from backend.app.models.user import User
from datetime import datetime

# "I'm not a player. I'm the one who designed the game."
# - Kevin Flynn - TRON

db_password = os.environ.get("SOULLINK_DB_PASS")
DATABASE_URL = f"postgresql://postgres:{db_password}@localhost:5432/soullink"
engine = create_engine(DATABASE_URL)

def create_architect():
    with Session(engine) as session:
        # Checking if the legend already exists
        statement = select(User).where(User.username == "brcgr")
        existing_user = session.exec(statement).first()

        if existing_user:
            print("👤 Architect account already exists. Refilling resources...")
            existing_user.energy = 9999
            existing_user.gems = 1000
            session.add(existing_user)
        else:
            print("✨ Manifesting the Architect...")
            new_user = User(
                user_id="syn_01",
                username="brcgr",
                display_name="The Architect",
                energy=9999,
                gems=1000,
                account_tier="elite",
                is_admin=True
            )
            session.add(new_user)
        
        session.commit()
        print("✅ Account syn_01 is online. Link City recognizes its creator.")

if __name__ == "__main__":
    create_architect()