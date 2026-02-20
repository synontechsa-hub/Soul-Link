# /_dev/scripts/diag_chat.py
import sys
import os
import uuid
from datetime import datetime
from sqlalchemy import text, create_engine, inspect

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from backend.app.core.config import settings

def diag():
    print("💎 SoulLink Chat Diagnostic")
    engine = create_engine(settings.database_url)
    
    # 1. Inspect Columns
    inspector = inspect(engine)
    columns = inspector.get_columns('conversations')
    print("\n[SCHEMA] 'conversations' table columns:")
    for col in columns:
        print(f"  - {col['name']} ({col['type']})")
    
    col_names = [c['name'] for c in columns]
    if 'meta_data' not in col_names:
        print("\n❌ CRITICAL: 'meta_data' column is MISSING!")
        print("  Attempting emergency repair...")
        try:
            with engine.connect() as conn:
                with conn.begin():
                    conn.execute(text("ALTER TABLE conversations ADD COLUMN meta_data JSONB DEFAULT '{}'::jsonb"))
            print("  ✅ Repair successful: meta_data added.")
        except Exception as e:
            print(f"  ❌ Repair failed: {e}")
    else:
        print("\n✅ 'meta_data' column exists.")

    # 2. Test Insert
    print("\n[TEST] Attempting test insert...")
    try:
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(text("""
                    INSERT INTO conversations (msg_id, user_id, soul_id, role, content, meta_data, created_at)
                    VALUES (:msg_id, :user_id, :soul_id, :role, :content, :meta_data, :created_at)
                """), {
                    "msg_id": str(uuid.uuid4()),
                    "user_id": "diag_user",
                    "soul_id": "diag_soul",
                    "role": "system",
                    "content": "Diagnostic Message",
                    "meta_data": '{"test": true}',
                    "created_at": datetime.utcnow()
                })
        print("✅ Test insert successful.")
    except Exception as e:
        print(f"❌ Test insert failed: {e}")

if __name__ == "__main__":
    diag()
