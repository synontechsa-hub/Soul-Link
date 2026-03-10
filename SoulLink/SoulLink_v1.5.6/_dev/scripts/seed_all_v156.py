"""
seed_all_v156.py
Master seeder — runs all seeders in correct dependency order.

Execution order:
  1. seed_system_v156.py     → system_config (10 keys)
  2. seed_locations_v156.py  → locations (31 rows)
  3. seed_souls_v156.py      → souls + soul_pillars + soul_states (45 rows)
  4. seed_lore_v156.py       → lore_items (4+ rows)

Usage:
    python seed_all_v156.py           # Live run
    python seed_all_v156.py --dry-run # Preview all, no DB writes
"""
import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(r"d:\Coding\SynonTech\SoulLink\SoulLink_v1.5.6\_dev\scripts")
DRY_RUN = "--dry-run" in sys.argv
ARGS = ["--dry-run"] if DRY_RUN else []

SEEDERS = [
    ("System Config",  SCRIPT_DIR / "seed_system_v156.py"),
    ("Locations",      SCRIPT_DIR / "seed_locations_v156.py"),
    ("Souls",          SCRIPT_DIR / "seed_souls_v156.py"),
    ("Lore Items",     SCRIPT_DIR / "seed_lore_v156.py"),
]

print(f"\n{'=' * 55}")
print(f"  SoulLink v1.5.6  —  Master Seeder")
print(f"  Mode: {'DRY RUN (no DB writes)' if DRY_RUN else 'LIVE'}")
print(f"{'=' * 55}\n")

for name, script in SEEDERS:
    print(f"\n▶  {name}")
    print("-" * 40)
    result = subprocess.run(
        [sys.executable, str(script)] + ARGS,
        capture_output=False
    )
    if result.returncode != 0:
        print(f"\n❌  {name} failed with exit code {result.returncode}")
        print("Stopping. Fix the error above and re-run.")
        sys.exit(result.returncode)

print(f"\n{'=' * 55}")
print(f"  ✅  All seeders complete")
print(f"{'=' * 55}\n")
