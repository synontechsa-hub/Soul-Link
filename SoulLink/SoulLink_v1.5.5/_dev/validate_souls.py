
import os
import json

# Paths
BASE_DIR = r"d:\Coding\SynonTech\SoulLink_v1.5.5\_dev"
DATA_DIR = os.path.join(BASE_DIR, "data")
SOULS_DIR = os.path.join(DATA_DIR, "souls")
SYSTEM_DIR = os.path.join(DATA_DIR, "system")
LOCATIONS_DIR = os.path.join(DATA_DIR, "locations")

# Load Registries
print("Loading registries...")
try:
    with open(os.path.join(SYSTEM_DIR, "factions.json"), "r") as f:
        FACTIONS = json.load(f)["factions"].keys()
    
    with open(os.path.join(SYSTEM_DIR, "archetypes.json"), "r") as f:
        ARCHETYPES = json.load(f)["archetypes"].keys()
        
    with open(os.path.join(SYSTEM_DIR, "traits_and_flaws", "traits.json"), "r") as f:
        TRAITS = set(json.load(f)["traits"].keys())
        
    with open(os.path.join(SYSTEM_DIR, "traits_and_flaws", "hidden_traits.json"), "r") as f:
        HIDDEN_TRAITS = set(json.load(f)["traits"].keys())

    with open(os.path.join(SYSTEM_DIR, "traits_and_flaws", "flaws.json"), "r") as f:
        FLAWS = set(json.load(f)["traits"].keys())

    # Locations map: filename without .json -> existence
    LOCATIONS = set([f.replace(".json", "") for f in os.listdir(LOCATIONS_DIR) if f.endswith(".json")])

except Exception as e:
    print(f"Error loading system files: {e}")
    exit(1)

def validate_soul(filename):
    filepath = os.path.join(SOULS_DIR, filename)
    errors = []
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            soul = json.load(f)
    except Exception as e:
        return [f"JSON Error: {e}"]

    # 1. Archetype
    arch_id = soul.get("identity", {}).get("archetype_id")
    if arch_id and arch_id not in ARCHETYPES:
        errors.append(f"Invalid Archetype ID: {arch_id}")

    # 2. Faction
    fac_id = soul.get("identity", {}).get("faction_id")
    if fac_id and fac_id not in FACTIONS:
        errors.append(f"Invalid Faction ID: {fac_id}")
        
    # 3. Locations (Routine Preferences)
    prefs = soul.get("routine", {}).get("location_preferences", {})
    for zone, loc_id in prefs.items():
        if loc_id and loc_id not in LOCATIONS:
            errors.append(f"Invalid Preference Location ({zone}): {loc_id}")

    # 4. Traits
    identity = soul.get("identity", {})
    
    for t in identity.get("personality_traits", {}).get("primary", []):
         if t not in TRAITS:
             errors.append(f"Unknown Primary Trait: {t}")
             
    for t in identity.get("personality_traits", {}).get("hidden", []):
         if t not in HIDDEN_TRAITS:
             errors.append(f"Unknown Hidden Trait: {t}")
             
    for t in identity.get("personality_traits", {}).get("flaws", []):
         if t not in FLAWS:
             errors.append(f"Unknown Flaw: {t}")

    return errors

# Validate All Souls
targets = sorted([f for f in os.listdir(SOULS_DIR) if f.endswith(".json") and not f.startswith("_")])

report = []
report.append(f"Validating {len(targets)} souls...")
for t in targets:
    errs = validate_soul(t)
    if errs:
        report.append(f"\n❌ {t} ISSUES:")
        for e in errs:
            report.append(f"  - {e}")
    else:
        report.append(f"✅ {t} PASS")

with open(os.path.join(BASE_DIR, "validation_report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(report))

print(f"Report generated for {len(targets)} souls.")
