# /_dev/scripts/full_seed.py
# /version.py v1.5.4 Arise

import sys
import os
from pathlib import Path

# Path setup to ensure imports work from the scripts folder
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

# Import the main execution functions from your scripts
from seed_db import init_db, ensure_architect_exists, seed_souls
from seed_world import seed_link_city
from migrate_v155_monetization import run_migration
from backup_db import run_backup

def Arise_Full_Sequence():
    print("=" * 60)
    print("🚀 SOULLINK: FULL NEURAL INITIALIZATION")
    print("=" * 60)

    try:
        # STEP 0: Safety Backup
        print("\n--- PHASE 0: SAFETY BACKUP ---")
        run_backup()
        print("✅ Phase 0 Complete.")

        # STEP 1: Core Database & Souls
        print("\n--- PHASE 1: SOUL INITIALIZATION ---")
        init_db()
        arch_id = ensure_architect_exists()
        seed_souls(arch_id)
        print("✅ Phase 1 Complete.")

        # STEP 2: World Map & Locations
        print("\n--- PHASE 2: WORLD RECONSTRUCTION ---")
        seed_link_city()
        print("✅ Phase 2 Complete.")

        # STEP 3: Monetization & v1.5.5 Infrastructure
        print("\n--- PHASE 3: MONETIZATION MIGRATION ---")
        # We call the function directly. 
        # Note: This script might still trigger your "yes/no" input 
        # because of the logic inside migrate_v155_monetization.py
        run_migration()
        print("✅ Phase 3 Complete.")

        print("\n" + "=" * 60)
        print("✨ LINK CITY IS ONLINE: All systems green.")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ CRITICAL FAILURE DURING SEEDING: {e}")
        sys.exit(1)

if __name__ == "__main__":
    Arise_Full_Sequence()