# /rebuild_locations.py
# /version.py
# /_dev/

# Launch version plans:
# SoulLink launches with 30 basic souls + characters + users can create characters.
# Characters do not populate the maps. They are NPCs basically.
# “Characters are chatbots. Souls are citizens.”
# Character integration to placate more casual users and only can be found in explore screen and searches.
# Similar to the basic flat style of c.ai/emochi but with a bit more logic behind them

# PS: The flagship souls will be much richer than even Alyssa is in her current form.
# Yes, this isnt her final form yet... ;)
# The current layout of Alyssa will be the basic schema for all basic souls at launch.

# Lore teases for Launch v1.0.0 - A higher set of powers ruling the city.

# Lore teases for Launch v1.0.1 - Secret societies and sects among the souls.
# Lore reveal for Launch v1.0.1 - Number 1 (Heh Heh Heh)

# Lore teases for Launch v1.0.2 - "The Seven" - Minds will be blown
# Lore reveal for Launch v1.0.2 - Number 2 (The plot thickens)

# Lore teases for Launch v1.0.3 - Numbers 5
# Lore reveal for Launch v1.0.3 - Number 3 & 4 - They're together for a reason ;)

# Lore teases for Launch v1.0.4 - Number 6
# Lore reveal for Launch v1.0.4 - Number 5

# Lore teases for Launch v1.0.5 - The dynamics of the seven expanded
# Lore reveal for Launch v1.0.5 - Number 6

# Lore teases for Launch v1.0.6 - The history of the seven
# Lore reveal for Launch v1.0.6 - Not number 7 yet... Ehe! Wait and see

# Lore teases for Launch v1.0.7 - Deeper dive into the first six
# Lore reveal for Launch v1.0.7 - NUMBER 7 - Queue dramatic music

# Lore teases for Launch v1.0.8 - Alyssa teased (Yes, shes not a launch soul actually)
# Lore reveal for Launch v1.0.8 - The truth about number 7

# Lore teases for Launch v1.0.9 - Alyssa's link to the seven
# Lore reveal for Launch v1.0.9 - Alyssa can finally be seen in the city (Refuses to talk to any users)

# NB: The Seven wont be in the game at all... just teased, info reveals, lore drops.
# The seven will only be added post Alyssa launch (even then, one at a time, also flagship_souls)

# Launch v1.1.0 - Alyssa unlocked (flagship_soul_0)
# Launch v1.1.0 - Soul hybrid system (Ehe... this is another game changer)
# Launch v1.1.0 - More basic souls and locations added

# The seven follows in later patches - My lips are sealed :x

import os
from sqlmodel import Session, create_engine, select
from backend.app.models.location import Location

# 🛡️ Secure Credential Fetch
# “Night City. The City of Dreams. And if you’re not careful, the city will chew you up and spit you out.”
# - Cyberpunk 2077
# Can't you just see Link City being a spectacle to behold like Night City?
# Obviously souls dont have cybernic implants here unless they are Cyberpunk themed souls.
db_password = os.environ.get("SOULLINK_DB_PASS")
if not db_password:
    print("❌ ERROR: SOULLINK_DB_PASS not set. Run your password batch file first!")
    exit(1)

DATABASE_URL = f"postgresql://postgres:{db_password}@localhost:5432/soullink"
engine = create_engine(DATABASE_URL)

# ────────────────────────────────────────────────────────────────
#                           THE CITY
# ────────────────────────────────────────────────────────────────
# "The right man in the wrong place can make all the difference in the world."
# - G-man - Half-Life 2

# Launch v1.0.0 will not have any lore connected to it.
# General lore tease for overall city map in Launch v1.0.1
WORLD_MAP = [
    {
        # Every user apartment has the same base layout… but no two end up looking the same.
        "id": "user_apartment",
        "name": "Linkside Estate",
        "desc": "A modest but well-kept apartment assigned to new residents of Link City. Clean lines, adjustable lighting, and a layout designed for personal customization. It’s quiet enough to think, close enough to everything that the city always feels within reach.",
        "mods": {"judge": {"safety": 1.5, "customization": 1.4, "intimacy": 1.3},
            "narrator": {"pacing": "adaptive", "style": "personal", "focus": "player_space"}}
    },
    {   
        # Lots of apartments in this building. Many souls will probably stay here (not all).
        # Tower must be there as there are 3 locations currently attached to it (Elevator for UI to select sub-locations)
        # Overall lore connection to the entire building to be teased with the seven
        "id": "skylink_tower",
        "name": "Skylink Tower",
        "desc": "A massive, and opulent, building in the center of Link City. It towers over the skyline of the rest of the city's tall buildings. The glass reflects the sky perfectly, hiding everything inside.",
        "mods": {"judge": {"authority": 1.5, "surveillance_feeling": "high"}, 
                 "narrator": {"tone": "majestic", "perspective": "dwarfed"}}
    },
    {   
        # Maybe something like Akihabara but in cyberpunk neon styles.
        "id": "circuit_street",
        "name": "Circuit Street",
        "desc": "Rain-slick pavement, flickering holographic ads, and the smell of ozone. The Forge is here.",
        "mods": {"judge": {"mood_volatility": 1.2}, 
                 "narrator": {"pacing": "fast", "style": "noir"}}
    },
    {
        # Very vibey and loud. Packed dance floors, etc.
        # “Chaos is a ladder.”
        # - Littlefinger - Game of Thrones: A Telltale Series
        "id": "neon_nights",
        "name": "Neon Nights Club",
        "desc": "Violet-crimson neon, pulsing bass, and VIP levels overlooking a sea of glowing tech.",
        "mods": {"judge": {"energy": 1.5, "guard_drop_rate": 0.8}, 
                 "narrator": {"style": "vibrant"}}
    },
    {
        # A more chilled and relaxed evening and nighttime atmosphere than Neon Nights
        "id": "rooftop_lounge",
        "name": "The Rooftop Lounge",
        "desc": "A quiet escape above the smog. Intimate booths and city lights that look like a circuit board.",
        "mods": {"judge": {"openness": 1.4}, 
                 "narrator": {"pacing": "slow", "focus": "atmosphere"}}
    },
    {   
        # User needs high intimacy with soul to bring them here.
        # Date location only perhaps? Could a soul or 2 work here?
        "id": "ether_baths",
        "name": "Ether Baths Spa",
        "desc": "A day spa located near the city plaza. Steamy saunas and a variety of indoor and outdoor baths filled with mineral-rich synth-water.",
        "mods": {"judge": {"recovery": 1.2, "closeness": 1.5}, 
                 "narrator": {"style": "intimate", "sensory": "humid"}}
    },
    {
        # Purely hangout experience and meeting place of certain souls
        "id": "linkgate_mall",
        "name": "LinkGate Mall",
        "desc": "The buzzing shopping mall in Link City. Stores of all varieties and sizes litter the huge complex, bombarding visitors with targeted holographic ads.",
        "mods": {"judge": {"distraction": 1.3, "materialism": 1.1}, 
                 "narrator": {"pacing": "bustling"}}
    },
    {
        # Pretty low-key place where souls with certain... tastes, spend their time.
        # "In the end, we will all become one. Flesh, mind, and soul — merged into perfection."
        # - The Many - System Shock 2
        "id": "dollhouse_dungeon",
        "name": "The Dollhouse Dungeon",
        "desc": "A bar located in the basement level of the Sky Link Tower. Low red lighting, velvet curtains, and hushed conversations cater to the city's darker desires.",
        "mods": {"judge": {"inhibitions": 0.5, "mystery": 1.4}, 
                 "narrator": {"style": "sultry_dark"}}
    },
    {
        # The best fine dining in Link City
        # “Order is the foundation of civilization. Without it, we fall to ruin.”
        # - Civilization VI
        "id": "linkview_cuisine",
        "name": "LinkView Cuisine",
        "desc": "A high tier restaurant on the top floor of the Sky Link Tower. Serves the best food in the city and hosts all the more elegant souls. The dress code is unspoken but strict.",
        "mods": {"judge": {"sophistication": 1.5, "formality": 1.2}, 
                 "narrator": {"pacing": "deliberate", "sensory": "taste"}}
    },
    {
        # “Every story is a seed. It grows when shared.”
        # - Dragon Age: Inquisition
        "id": "the_garden",
        "name": "Link City Botanical Garden",
        "desc": "A bio-dome of engineered tranquility. Neon-veined ivy and holographic butterflies mix with real flora, creating a synthetic Eden.",
        "mods": {"judge": {"calm": 1.5, "vulnerability": 1.2}, 
                 "narrator": {"style": "serene"}}
    },
    {
        # “The universe is a dark place. But it’s filled with stars, and each one is a story.”
        # - Mass Effect
        "id": "city_planetarium",
        "name": "City Planetarium",
        "desc": "A massive projection dome simulating the cosmos. In the pitch black, the stars feel close enough to touch, prompting deep existential talks.",
        "mods": {"judge": {"wonder": 1.4, "existentialism": 1.3}, 
                 "narrator": {"scale": "cosmic"}}
    },
    {
        # “Time is an unforgiving thing. Once it’s broken, it cannot be fixed.”
        # - Quantum Break
        "id": "stop_n_go",
        "name": "Stop n Go Racetrack",
        "desc": "The smell of burning rubber and ozone. High-speed hover-karts tear through a neon-lit circuit where adrenaline junkies congregate.",
        "mods": {"judge": {"adrenaline": 1.5, "patience": 0.2}, 
                 "narrator": {"pacing": "frantic"}}
    },
    {
        # “I gave you all I had. I tried to be a good man.”
        # - Red Dead Redemption 2
        "id": "soul_plaza",
        "name": "Soul Plaza",
        "desc": "The beating heart of the city. A massive open space where holograms, humans, and souls collide under the watchful digital eye of Skylink Tower.",
        "mods": {"judge": {"social_density": 1.5, "anonymity": 1.2}, 
                 "narrator": {"focus": "crowd_dynamics"}}
    },
    {
        # “Push through the pain. Giving up hurts more.”
        # - Shounen Law
        "id": "iron_resolve_gym",
        "name": "Iron Resolve Gym",
        "desc": "A no-nonsense training facility filled with the clang of iron and the smell of sweat. Holographic trainers bark encouragement while souls chase personal bests beneath harsh white lights.",
        "mods": {"judge": {"discipline": 1.5, "adrenaline": 1.2, "guard_drop_rate": 0.4, "self_improvement": 1.4},
                "narrator": {"pacing": "driven", "sensory": "physical", "focus": "effort_and_progress"}}
    },
    {
        # “A real warrior never fights for himself alone.”
        # - Definitely-an-anime
        "id": "link_city_arena",
        "name": "Link City Arena",
        "desc": "A colossal stadium of steel and light. Roaring crowds, towering holo-screens, and an electric atmosphere where victories are immortalized and failures remembered.",
        "mods": {"judge": {"confidence": 1.5, "pressure": 1.4, "guard_drop_rate": 0.7, "reputation_weight": 1.5},
            "narrator": {"pacing": "cinematic", "scale": "grand", "focus": "spectacle_and_emotion"}}
    },
    {
        "id": "civic_heights",
        "name": "Civic Heights",
        "desc": "A practical residential block near municipal offices and transit hubs. Well-maintained corridors, steady foot traffic, and neighbors who nod but don’t pry. Life here is orderly, predictable, and quietly comfortable.",
        "mods": {"judge": {"stability": 1.3, "social_norms": 1.2, "privacy": 1.1},
            "narrator": {"pacing": "steady", "style": "grounded", "focus": "daily_life"}}
    },
    {
        "id": "northway_flats",
        "name": "Northway Flats",
        "desc": "Low-rise apartments tucked away from the city’s louder arteries. Tree-lined walkways, older architecture, and a slower rhythm make this area feel detached from the constant pulse of Link City.",
        "mods": {"judge": {"calm": 1.4, "routine": 1.2, "openness": 1.1},
            "narrator": {"pacing": "slow", "style": "quiet_reflective", "focus": "stillness"}}
    },
    {
        "id": "midline_residences",
        "name": "Midline Residences",
        "desc": "Standard residential housing designed for efficiency and comfort. Neutral interiors, sound insulation, and sensible layouts make this a common choice for long-term residents who value balance over luxury.",
        "mods": {"judge": {"balance": 1.3, "comfort": 1.3, "predictability": 1.2},
            "narrator": {"pacing": "neutral", "style": "unembellished", "focus": "home_life"}}
    },
    {
        # The lower income apartments for souls that are struggling financially.
        "id": "crimson_arms",
        "name": "Crimson Arms Apartments",
        "desc": "A crumbling mid-rise on the edge of the Arts District. Flickering hallway lights, peeling crimson wallpaper, and the smell of old incense. Once elegant, now forgotten—much like its residents.",
        "mods": {"judge": {"melancholy": 1.3, "nostalgia": 1.2, "isolation": 1.4}, 
                 "narrator": {"style": "faded_grandeur", "pacing": "slow", "focus": "decay_and_beauty"}}
    },
]
# “Liberty City is a land of opportunity… if you survive long enough to see it.”
# - Grand Theft Auto IV
def rebuild_world():
    print("🏗️  REBUILDING LINK CITY ARCHIVE...")
    
    with Session(engine) as session:
        for loc_data in WORLD_MAP:
            # "You want a piece of me, boy?" - Marine - Starcraft
            statement = select(Location).where(Location.location_id == loc_data["id"])
            existing = session.exec(statement).first()
            
            # Logic to determine category based on ID or Name
            category = "residential" if "apartment" in loc_data["id"] or "residence" in loc_data["id"] else "public_hub"
            if "cuisine" in loc_data["id"]: category = "fine_dining"
            if "club" in loc_data["id"] or "lounge" in loc_data["id"]: category = "nightlife"

            if existing:
                print(f"🔄 Updating: {loc_data['name']}")
                target = existing
            else:
                # “We do what we must because we can.” - GLaDOS - Portal
                print(f"✨ Creating: {loc_data['name']}")
                target = Location(location_id=loc_data["id"]) # type: ignore[call-arg]

            # Map the Architect Schema Fields
            target.display_name = loc_data["name"]
            target.description = loc_data["desc"]
            target.category = category
            
            # Split 'mods' into the Architect Pillars
            # Environmental Prompts are for the Narrator/Mood
            target.environmental_prompts = loc_data["mods"].get("narrator", {})
            
            # System Modifiers are for the Judge/Logic
            target.system_modifiers = loc_data["mods"].get("judge", {})
            
            # Default music if not specified
            target.music_track = "ambient_city_loop.mp3"
            if "club" in loc_data["id"]: target.music_track = "neon_pulse_techno.mp3"

            session.add(target)
        
        # “Welcome to Midgar...” - Final Fantasy VII
        session.commit()
        print("\n✅ LINK CITY REBIRTH COMPLETE. All nodes active.")

if __name__ == "__main__":
    rebuild_world()