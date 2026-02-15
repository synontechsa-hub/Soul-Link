# /_dev/scripts/seed_world.py
# /version.py v1.5.4 Arise

import os
import sys
from pathlib import Path
# Path setup
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

# Path setup

from sqlmodel import Session, select
from backend.app.core.config import settings
from backend.app.database.session import engine
from backend.app.models.location import Location

def seed_link_city():
    print(f"🗺️  Rebuilding Link City for v1.5.4 Arise...")
    
    # [WORLD_MAP Data remains same as before...]
    WORLD_MAP = [
        {"id": "linkside_estate", "name": "Linkside Estate (User Loft)", "category": "residential", "desc": "A modest but well-kept apartment assignd to new residents of Link City.", "privacy": "Private", "mods": {"safety": 1.5, "customization": 1.4}, "image_url": "/assets/images/locations/linkview_estate_01.jpg"},
        {"id": "skylink_tower", "name": "Skylink Tower", "category": "landmark", "desc": "A massive, opulent building in the center of Link City.", "privacy": "Public", "mods": {"authority": 1.5}, "image_url": "/assets/images/locations/skylink_tower_01.jpg"},
        {"id": "circuit_street", "name": "Circuit Street", "category": "commercial", "desc": "Rain-slick pavement, flickering holographic ads.", "privacy": "Public", "mods": {"mood_volatility": 1.2}, "image_url": "/assets/images/locations/circuit_street_01.jpg"},
        {"id": "neon_nights", "name": "Neon Nights Club", "category": "nightlife", "desc": "Violet-crimson neon, pulsing bass.", "privacy": "Public", "mods": {"energy": 1.5}, "image_url": "/assets/images/locations/neon_nights_club_01.jpg"},
        {"id": "rooftop_lounge", "name": "The Rooftop Lounge", "category": "nightlife", "desc": "A quiet escape above the smog.", "privacy": "Semi-Private", "mods": {"openness": 1.4}, "image_url": "/assets/images/locations/the_rooftop_lounge_01.jpg"},
        {"id": "ether_baths", "name": "Ether Baths Spa", "category": "wellness", "desc": "A day spa located near the city plaza.", "privacy": "Private", "mods": {"recovery": 1.2}, "image_url": "/assets/images/locations/ether_baths_spa_01.jpg"},
        {"id": "linkgate_mall", "name": "LinkGate Mall", "category": "commercial", "desc": "The buzzing shopping mall in Link City.", "privacy": "Public", "mods": {"distraction": 1.3}, "image_url": "/assets/images/locations/linkgate_mall_01.jpg"},
        {"id": "dollhouse_dungeon", "name": "The Dollhouse Dungeon", "category": "nightlife", "desc": "A bar located in the basement level of Skylink Tower.", "privacy": "Private", "mods": {"inhibitions": 0.5}, "image_url": "/assets/images/locations/the_dollhouse_dungeon_01.jpg"},
        {"id": "linkview_cuisine", "name": "LinkView Cuisine", "category": "dining", "desc": "A high-tier restaurant on the top floor of Skylink Tower.", "privacy": "Semi-Private", "mods": {"sophistication": 1.5}, "image_url": "/assets/images/locations/linkview_cuisine_01.jpg"},
        {"id": "the_garden", "name": "Link City Botanical Garden", "category": "wellness", "desc": "A bio-dome of engineered tranquility.", "privacy": "Public", "mods": {"calm": 1.5}, "image_url": "/assets/images/locations/the_garden_01.jpg"},
        {"id": "city_planetarium", "name": "City Planetarium", "category": "landmark", "desc": "A massive projection dome simulating the cosmos.", "privacy": "Public", "mods": {"wonder": 1.4}, "image_url": "/assets/images/locations/city_planetarium_01.jpg"},
        {"id": "stop_n_go", "name": "Stop n Go Racetrack", "category": "sports", "desc": "The smell of burning rubber and ozone.", "privacy": "Public", "mods": {"adrenaline": 1.5}, "image_url": "/assets/images/locations/stop_n_go_racetrack_01.jpg"},
        {"id": "soul_plaza", "name": "Soul Plaza", "category": "public_hub", "desc": "The beating heart of the city.", "privacy": "Public", "mods": {"social_density": 1.5}, "image_url": "/assets/images/locations/soul_plaza_01.jpg"},
        {"id": "iron_resolve_gym", "name": "Iron Resolve Gym", "category": "sports", "desc": "A no-nonsense training facility.", "privacy": "Public", "mods": {"discipline": 1.5}, "image_url": "/assets/images/locations/iron_resolve_gym_01.jpg"},
        {"id": "link_city_arena", "name": "Link City Arena", "category": "sports", "desc": "A colossal stadium of steel and light.", "privacy": "Public", "mods": {"confidence": 1.5}, "image_url": "/assets/images/locations/link_city_arena_01.jpg"},
        {"id": "civic_heights", "name": "Civic Heights", "category": "residential", "desc": "A practical residential block near municipal offices.", "privacy": "Public", "mods": {"stability": 1.3}, "image_url": "/assets/images/locations/civic_heights_01.jpg"},
        {"id": "northway_flats", "name": "Northway Flats", "category": "residential", "desc": "Low-rise apartments tucked away.", "privacy": "Semi-Private", "mods": {"calm": 1.4}, "image_url": "/assets/images/locations/northway_flats_01.jpg"},
        {"id": "midline_residences", "name": "Midline Residences", "category": "residential", "desc": "Standard residential housing designed for efficiency.", "privacy": "Public", "mods": {"balance": 1.3}, "image_url": "/assets/images/locations/midline_residences_01.jpg"},
        {"id": "crimson_arms", "name": "Crimson Arms Apartments", "category": "residential", "desc": "A crumbling mid-rise on the edge of the Arts District.", "privacy": "Semi-Private", "mods": {"melancholy": 1.3}, "image_url": "/assets/images/locations/crimson_arms_apartments_01.jpg"},
        {"id": "skylink_apartments", "name": "Skylink Tower Residences", "category": "residential", "desc": "Mid-tier apartments within Skylink Tower.", "privacy": "Semi-Private", "mods": {"isolation": 1.3}, "image_url": "/assets/images/locations/skylink_tower_residences_01.jpg"},
        {"id": "echo_archives", "name": "Echo Archives Public Library", "category": "cultural", "desc": "A three-story library with wooden floors.", "privacy": "Public", "mods": {"calm": 1.6}, "image_url": "/assets/images/locations/echo_archives_01.jpg"},
        {"id": "pixel_den", "name": "The Pixel Den Arcade", "category": "entertainment", "desc": "A sprawling cyberpunk arcade.", "privacy": "Public", "mods": {"energy": 1.6}, "image_url": "/assets/images/locations/pixel_den_arcade_01.jpg"},
        {"id": "umbral_exchange", "name": "The Umbral Exchange", "category": "underground", "desc": "A hidden market.", "privacy": "Private", "mods": {"danger": 1.5}, "image_url": "/assets/images/locations/the_umbral_exchange_01.jpg"},
        {"id": "apex_corporate_plaza", "name": "Apex Corporate Plaza", "category": "commercial", "desc": "A gleaming district of glass towers.", "privacy": "Semi-Private", "mods": {"authority": 1.5}, "image_url": "/assets/images/locations/apex_corporate_plaza_01.jpg"},
        {"id": "obsidian_proving_grounds", "name": "Obsidian Proving Grounds", "category": "combat", "desc": "A brutal training facility.", "privacy": "Semi-Private", "mods": {"intensity": 1.6}, "image_url": "/assets/images/locations/obsidian_proving_grounds_01.jpg"},
        {"id": "circuit_diner", "name": "The Circuit Diner", "category": "dining", "desc": "A 24-hour diner on Circuit Street.", "privacy": "Public", "mods": {"comfort": 1.4}, "image_url": "/assets/images/locations/the_circuit_diner_01.jpg"},
        {"id": "neon_span_bridge", "name": "Neon Span Bridge", "category": "landmark", "desc": "A massive suspension bridge.", "privacy": "Public", "mods": {"isolation": 1.5}, "image_url": "/assets/images/locations/neon_span_bridge_01.jpg"},
        {"id": "twilight_park", "name": "Twilight Park", "category": "wellness", "desc": "A small urban park wedged between residential blocks.", "privacy": "Public", "mods": {"calm": 1.5}, "image_url": "/assets/images/locations/twilight_park_01.jpg"},
        {"id": "zenith_lounge", "name": "The Zenith Rooftop Lounge", "category": "nightlife", "desc": "A sleek rooftop bar.", "privacy": "Semi-Private", "mods": {"sophistication": 1.4}, "image_url": "/assets/images/locations/zenith_rooftop_lounge_01.jpg"},
        {"id": "shadowed_archives", "name": "The Shadowed Archives", "category": "cultural", "desc": "A darker, more gothic wing of the library.", "privacy": "Semi-Private", "mods": {"mystery": 1.5}, "image_url": "/assets/images/locations/the_shadowed_archives_01.jpg"},
    ]

    with Session(engine) as session:
        for loc in WORLD_MAP:
            existing_loc = session.exec(select(Location).where(Location.location_id == loc["id"])).first()
            
            # Note: I'm keeping the description short here for the update, but the logic remains the same.
            loc_data = {
                "display_name": loc["name"],
                "category": loc["category"],
                "description": loc.get("desc", ""),
                "image_url": loc.get("image_url"), # Added image_url support

                "system_modifiers": {
                    "privacy_gate": loc.get("privacy", "Public"),
                    "mood_modifiers": loc.get("mods", {}),
                    "music": "neon_ambient_01.mp3",
                }
            }

            if existing_loc:
                for key, value in loc_data.items(): setattr(existing_loc, key, value)
                print(f"  🔄 Updated: {loc['name']}")
            else:
                new_loc = Location(location_id=loc["id"], **loc_data)
                session.add(new_loc)
                print(f"  ✨ Created: {loc['name']}")
        
        session.commit()
        print(f"\n✅ {len(WORLD_MAP)} locations synchronized. The city is alive.")

if __name__ == "__main__":
    seed_link_city()