import asyncio
import sys
from pathlib import Path
from sqlalchemy import select, text

# Path setup to import backend modules
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database.session import async_engine
from backend.app.models.location import Location
from sqlmodel.ext.asyncio.session import AsyncSession

# Configuration
ASSETS_DIR = project_root / "assets" / "images" / "locations"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

async def update_location_images():
    print(f"🖼️  Scanning for Location Images in {ASSETS_DIR}...")
    
    if not ASSETS_DIR.exists():
        print(f"❌ Assets directory not found: {ASSETS_DIR}")
        return

    updates = {}
    
    for file_path in ASSETS_DIR.rglob("*"):
        if file_path.suffix.lower() in IMAGE_EXTENSIONS:
            filename = file_path.stem 
            parts = filename.split('_')
            if parts[-1].isdigit() and len(parts[-1]) <= 2:
                location_id = "_".join(parts[:-1])
            else:
                location_id = filename
                
            relative_path = f"/assets/images/locations/{file_path.parent.name}/{file_path.name}"
            updates[location_id] = relative_path

    print(f"Found {len(updates)} potential image mappings.")

    updated_count = 0
    # Use Async Session
    async with AsyncSession(async_engine) as session:
        # We assume schema is fixed by fix_db_schema_async.py now
        
        result = await session.execute(select(Location))
        locations = result.scalars().all()
        
        for loc in locations:
            if loc.location_id in updates:
                loc.image_url = updates[loc.location_id]
                session.add(loc)
                updated_count += 1
                print(f"✅ Linked {loc.location_id} -> {updates[loc.location_id]}")
        
        await session.commit()
        print(f"\n✨ Database updated! {updated_count} locations now have images.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(update_location_images())
