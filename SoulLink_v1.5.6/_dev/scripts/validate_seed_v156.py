"""
validate_seed_v156.py
Sanity-checks the DB after seeding. Verifies row counts and spot-checks key fields.

Usage:
    python validate_seed_v156.py
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.session import engine
from sqlmodel import Session, text

EXPECTED_MIN_SOULS = 9       # Fragment souls minimum
EXPECTED_MIN_LOCATIONS = 30  # We have 31 location files

def check(label, result, expected=None):
    ok = "✅" if (expected is None or result >= expected) else "❌"
    suffix = f" (expected >= {expected})" if expected else ""
    print(f"  {ok} {label}: {result}{suffix}")
    return ok == "✅"

def validate():
    print("\n🔍 SoulLink v1.5.6 — Seed Validation\n")
    all_pass = True

    with Session(engine) as session:
        # ── Row Counts ───────────────────────────────────────────────────────
        print("── Row Counts ──")
        souls = session.execute(text("SELECT COUNT(*) FROM souls")).scalar()
        pillars = session.execute(text("SELECT COUNT(*) FROM soul_pillars")).scalar()
        states = session.execute(text("SELECT COUNT(*) FROM soul_states")).scalar()
        locations = session.execute(text("SELECT COUNT(*) FROM locations")).scalar()

        all_pass &= check("souls", souls, EXPECTED_MIN_SOULS)
        all_pass &= check("soul_pillars", pillars, EXPECTED_MIN_SOULS)
        all_pass &= check("soul_states", states, EXPECTED_MIN_SOULS)
        all_pass &= check("locations", locations, EXPECTED_MIN_LOCATIONS)

        # ── Pillar Integrity ─────────────────────────────────────────────────
        print("\n── Pillar Integrity ──")
        missing_ie = session.execute(text(
            "SELECT COUNT(*) FROM soul_pillars WHERE interaction_engine IS NULL OR interaction_engine::text = '{}'"
        )).scalar()
        missing_meta = session.execute(text(
            "SELECT COUNT(*) FROM soul_pillars WHERE meta_data IS NULL OR meta_data::text = '{}'"
        )).scalar()
        all_pass &= check("Souls with interaction_engine populated", souls - missing_ie, souls)
        all_pass &= check("Souls with meta_data populated", souls - missing_meta, souls)

        # ── Location Privacy Gates ────────────────────────────────────────────
        print("\n── Location Privacy Gates ──")
        private_locs = session.execute(text(
            "SELECT COUNT(*) FROM locations WHERE system_modifiers->>'privacy_gate' = 'Private'"
        )).scalar()
        public_locs = session.execute(text(
            "SELECT COUNT(*) FROM locations WHERE system_modifiers->>'privacy_gate' = 'Public'"
        )).scalar()
        no_gate = session.execute(text(
            "SELECT COUNT(*) FROM locations WHERE system_modifiers->>'privacy_gate' IS NULL"
        )).scalar()
        check("Private locations", private_locs)
        check("Public locations", public_locs)
        all_pass &= check("Locations missing privacy_gate", no_gate, 1) if no_gate == 0 else (print(f"  ❌ {no_gate} locations missing privacy_gate!") or False)

        # ── Architect Check ───────────────────────────────────────────────────
        print("\n── Architect Account ──")
        from backend.app.core.config import settings
        arch_uuid = settings.architect_uuid
        if arch_uuid:
            # Use LIKE on text cast to avoid psycopg2 treating '?' as a param placeholder
            arch_in_db = session.execute(text(
                "SELECT COUNT(*) FROM soul_pillars WHERE meta_data::text LIKE :pattern"
            ), {"pattern": f"%{arch_uuid}%"}).scalar()
            all_pass &= check(f"Souls recognising architect ({arch_uuid[:8]}...)", arch_in_db, souls)
        else:
            print("  ⚠️  ARCHITECT_UUID not set in .env — skipping check")

    print(f"\n{'✅ ALL CHECKS PASSED' if all_pass else '❌ SOME CHECKS FAILED — review output above'}\n")

if __name__ == "__main__":
    validate()
