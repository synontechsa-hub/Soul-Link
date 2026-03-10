# /_dev/scripts/inspect_db.py
import sys
import os
from sqlalchemy import text, create_engine

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from backend.app.core.config import settings

def inspect():
    print("🔍 Inspecting DB Schema...")
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        for table in ["conversations", "link_states"]:
            print(f"\nTable: {table}")
            try:
                res = conn.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'"))
                for row in res:
                    print(f"  - {row[0]}: {row[1]}")
            except Exception as e:
                print(f"  Error: {e}")

if __name__ == "__main__":
    inspect()
