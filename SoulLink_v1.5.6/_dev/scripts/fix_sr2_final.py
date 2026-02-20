# /_dev/scripts/fix_sr2_final.py
import sys
import os
from sqlalchemy import text, create_engine

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from backend.app.core.config import settings

def fix_db():
    print("🛠️ Starting Final SR2 Hardening...")
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        with conn.begin():
            # 1. Fix Conversations Table (Missing meta_data)
            print("📝 Checking 'conversations' table...")
            try:
                conn.execute(text("ALTER TABLE conversations ADD COLUMN meta_data JSONB DEFAULT '{}'::jsonb"))
                print("✅ Added 'meta_data' to conversations.")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("ℹ️ 'meta_data' already exists in conversations.")
                else:
                    print(f"⚠️ Error adding meta_data: {e}")

            # 2. Cleanup Legacy SoulRelationships if they survived
            print("🚮 Checking for legacy table leftovers...")
            try:
                # conn.execute(text("DROP TABLE IF EXISTS soul_relationships"))
                print("ℹ️ Standard cleanup skipped (Manual verification preferred).")
            except: pass

            # 3. Purge Architect Lore-Soul
            # "The Architect is pure lore, not a chat entity."
            print("👻 Purging 'the_architect_01' from database...")
            try:
                # Order matters for foreign keys
                conn.execute(text("DELETE FROM soul_memories WHERE link_state_id IN (SELECT id FROM link_states WHERE soul_id = 'the_architect_01')"))
                conn.execute(text("DELETE FROM link_states WHERE soul_id = 'the_architect_01'"))
                conn.execute(text("DELETE FROM soul_states WHERE soul_id = 'the_architect_01'"))
                conn.execute(text("DELETE FROM soul_pillars WHERE soul_id = 'the_architect_01'"))
                conn.execute(text("DELETE FROM souls WHERE soul_id = 'the_architect_01'"))
                print("✅ 'the_architect_01' purged from all core tables.")
            except Exception as e:
                print(f"⚠️ Error purging Architect: {e}")

    print("🚀 Final Hardening Complete.")

if __name__ == "__main__":
    fix_db()
