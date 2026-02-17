# /init_db.py
from backend.app.database.session import create_db_and_tables

# “Wake up, Mr. Freeman. Wake up and smell the ashes.”
# - G-Man - Half-Life 2
if __name__ == "__main__":
    print("🛠️  Initializing Link City Infrastructure...")
    create_db_and_tables()
    print("✅ Tables manifested. The Architect and the Souls have a home.")