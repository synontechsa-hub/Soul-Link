# /_dev/scripts/migrate_v156_monetization.py
# Migration script to add subscription and ad tracking fields
# Run this ONCE before deploying v1.5.5 features

import os
import sys
from pathlib import Path
# Path setup
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import text
from backend.app.core.config import settings
from backend.app.database.session import engine

# Constants are now pulled from settings

def run_migration():
    """
    Add monetization fields to users table for v1.5.5 framework.
    These fields support the hybrid Link Stability / Ad / Subscription system.
    """
    print("🔄 Running v1.5.6 Monetization Migration...")
    print("📊 Adding subscription, ad tracking, and stability overdrive fields...")
    
    with engine.connect() as conn:
        try:
            # Add new columns to users table
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(20),
                ADD COLUMN IF NOT EXISTS subscription_start TIMESTAMP,
                ADD COLUMN IF NOT EXISTS subscription_end TIMESTAMP,
                ADD COLUMN IF NOT EXISTS total_ads_watched INTEGER DEFAULT 0,
                ADD COLUMN IF NOT EXISTS ad_cooldown_until TIMESTAMP,
                ADD COLUMN IF NOT EXISTS stability_overdrive_until TIMESTAMP,
                ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(100),
                ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(100);
            """))
            
            conn.commit()
            print("✅ Migration complete!")
            print("\n📋 Added fields:")
            print("   - subscription_status (VARCHAR)")
            print("   - subscription_start (TIMESTAMP)")
            print("   - subscription_end (TIMESTAMP)")
            print("   - total_ads_watched (INTEGER)")
            print("   - ad_cooldown_until (TIMESTAMP)")
            print("   - stability_overdrive_until (TIMESTAMP)")
            print("   - stripe_customer_id (VARCHAR)")
            print("   - stripe_subscription_id (VARCHAR)")
            print("\n🎯 Ready for v1.5.5 monetization features!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("  SOULLINK v1.5.6 MONETIZATION MIGRATION")
    print("  Adding Link Stability & Subscription Framework")
    print("=" * 60)
    print()
    
    # Confirm before running
    response = input("⚠️  This will modify the users table. Continue? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Migration cancelled.")
        sys.exit(0)
    
    run_migration()
    print("\n" + "=" * 60)
    print("  MIGRATION COMPLETE - Database Ready for v1.5.6")
    print("=" * 60)
