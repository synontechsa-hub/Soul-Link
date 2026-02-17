# /_dev/patch_relationships_v1_5_2.py
import os
import psycopg2
from psycopg2 import sql

# === CONFIGURATION ===
# Using your standard environment-based security
DB_CONFIG = {
    "dbname": "soullink",
    "user": "postgres",
    "password": os.environ.get("SOULLINK_DB_PASS"),
    "host": "localhost",
    "port": "5432"
}

def apply_migration():
    if not DB_CONFIG["password"]:
        print("❌ ERROR: 'SOULLINK_DB_PASS' not set.")
        return

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        print("🔍 Checking 'user_soul_relationships' for missing columns...")
        
        # 1. Add 'current_location' if it doesn't exist
        # Defaulting to 'linkview_cuisine' ensures existing relationships have a valid start point
        cur.execute("""
            ALTER TABLE user_soul_relationships 
            ADD COLUMN IF NOT EXISTS current_location VARCHAR(50) DEFAULT 'linkview_cuisine';
        """)
        
        # 2. Add 'current_tier' if you haven't yet (Doctrine requirement)
        cur.execute("""
            ALTER TABLE user_soul_relationships 
            ADD COLUMN IF NOT EXISTS current_tier VARCHAR(20) DEFAULT 'STRANGER';
        """)

        conn.commit()
        print("✅ MIGRATION SUCCESSFUL: Link City spatial tracking is now online.")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ MIGRATION FAILED: {e}")

if __name__ == "__main__":
    apply_migration()