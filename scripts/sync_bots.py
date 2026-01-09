# scripts/sync_bots.py
# Syncs shared bot assets into Flutter assets directory
# Source of truth: /assets/bots
# Target: flutter_frontend/assets/bots

import shutil
from pathlib import Path

# ─────────────────────────────────────────────
# 🧭 PROJECT ROOT RESOLUTION
# ─────────────────────────────────────────────
#
# Resolve project root dynamically so the script
# can be run from anywhere.

ROOT = Path(__file__).resolve().parents[1]

# ─────────────────────────────────────────────
# 📁 BOT ASSET PATHS
# ─────────────────────────────────────────────
#
# SOURCE = single source of truth (backend-owned)
# TARGET = Flutter-readable asset directory

SOURCE = ROOT / "assets" / "bots"
TARGET = ROOT / "flutter_frontend" / "assets" / "bots"

# ─────────────────────────────────────────────
# 🔄 SYNC LOGIC
# ─────────────────────────────────────────────

def sync_bots():
    # Validate source exists
    if not SOURCE.exists():
        raise FileNotFoundError(f"Source bots folder not found: {SOURCE}")

    # Remove existing target to avoid stale files
    if TARGET.exists():
        shutil.rmtree(TARGET)

    # Copy fresh bot assets
    shutil.copytree(SOURCE, TARGET)

    print("✅ Bots synced successfully.")

# ─────────────────────────────────────────────
# 🚀 SCRIPT ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    sync_bots()
