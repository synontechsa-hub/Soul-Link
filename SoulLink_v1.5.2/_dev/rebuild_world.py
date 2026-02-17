# /rebuild_world.py
# /version.py
# /_dev/

import json
import os
import psycopg2
from psycopg2.extras import Json

# === CONFIGURATION ===
DB_CONFIG = {
    "dbname": "soullink",
    "user": "postgres",
    "password": os.environ.get("SOULLINK_DB_PASS"),
    "host": "localhost",
    "port": "5432"
}

# Recovered data from your v1.5.1 Snapshot
ALYS_DNA = {
    "soul_id": "alyssa",
    "display_name": "Alyssa",
    "archetype": "Tsundere",
    "personality_matrix": {
        "traits": ["Intelligent", "Playful", "Flirty"],
        "voice": "staccato",
        "narrative_bias": "tech-focused"
    }
}

def seed_database():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 1. Insert Alyssa
        print("💉 Injecting Alyssa's DNA...")
        cur.execute(
            """
            INSERT INTO souls (soul_id, display_name, archetype, personality_matrix)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (soul_id) DO UPDATE SET personality_matrix = EXCLUDED.personality_matrix;
            """,
            (ALYS_DNA["soul_id"], ALYS_DNA["display_name"], ALYS_DNA["archetype"], Json(ALYS_DNA["personality_matrix"]))
        )

        # 2. Insert Circuit Street (The Forge)
        print("🏗️ Rebuilding Circuit Street...")
        cur.execute(
            """
            INSERT INTO locations (location_id, display_name, description, system_modifiers)
            VALUES ('circuit_street', 'Circuit Street', 'Rain-slick pavement and neon lights.', %s)
            ON CONFLICT (location_id) DO NOTHING;
            """,
            [Json({"judge": {"mood_volatility": 1.2}, "narrator": {"pacing": "fast"}})]
        )

        conn.commit()
        print("✅ Database Rebirth Complete! Alyssa is back online.")
        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error during rebirth: {e}")

if __name__ == "__main__":
    seed_database()