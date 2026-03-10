import json
import os
import sys

DEV_DIR = os.path.dirname(__file__)
if os.path.basename(DEV_DIR) == "scripts":
    DEV_DIR = os.path.dirname(DEV_DIR)

DATA_DIR = os.path.join(DEV_DIR, "data")
SYSTEM_DIR = os.path.join(DATA_DIR, "system")
SOULS_DIR = os.path.join(DATA_DIR, "souls")
PREMIUM_SOULS_DIR = os.path.join(DATA_DIR, "premium_souls")


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# Load System Data
try:
    archetypes_data = load_json(os.path.join(SYSTEM_DIR, "archetypes.json"))
    valid_archetypes = set(archetypes_data.get("archetypes", {}).keys())

    factions_data = load_json(os.path.join(SYSTEM_DIR, "factions.json"))
    valid_factions = set()
    for mf in factions_data.get("meta_factions", []):
        valid_factions.add(mf["id"])
    valid_factions.update(factions_data.get("sub_groups", {}).keys())

    routines_data = load_json(os.path.join(SYSTEM_DIR, "routines.json"))
    valid_routines = set([k for k in routines_data.keys()
                         if k not in ["routines_id", "version"]])

    zones_data = load_json(os.path.join(SYSTEM_DIR, "zones.json"))
    valid_locations = set(["everywhere", "none", "linkside_estate"])
    valid_zones = set(zones_data.get("zones", {}).keys())
    valid_locations.update(valid_zones)
    for zone, info in zones_data.get("zones", {}).items():
        valid_locations.update(info.get("locations", []))

except Exception as e:
    print(f"Error loading system data: {e}")
    sys.exit(1)


def check_souls(directory, soul_type):
    errors = []
    if not os.path.exists(directory):
        return errors

    for filename in sorted(os.listdir(directory)):
        if not filename.endswith(".json") or filename.startswith("_"):
            continue

        filepath = os.path.join(directory, filename)
        try:
            soul = load_json(filepath)
            soul_id = soul.get("soul_id", filename)

            # Check archetype
            archetype_id = soul.get("identity", {}).get("archetype_id")
            if archetype_id and archetype_id not in valid_archetypes:
                errors.append(
                    f"[{soul_type}] {soul_id}: Invalid archetype_id '{archetype_id}'")
            elif not archetype_id:
                errors.append(f"[{soul_type}] {soul_id}: Missing archetype_id")

            # Check faction
            faction_id = soul.get("identity", {}).get("faction_id")
            if faction_id and faction_id not in valid_factions:
                errors.append(
                    f"[{soul_type}] {soul_id}: Invalid faction_id '{faction_id}'")
            elif not faction_id:
                pass  # Not all souls might have a faction, but check anyway
                # errors.append(f"[{soul_type}] {soul_id}: Missing faction_id")

            # Check routine
            template_id = soul.get("routine", {}).get("template_id")
            if template_id and template_id not in valid_routines:
                errors.append(
                    f"[{soul_type}] {soul_id}: Invalid routine template_id '{template_id}'")

            # Check locations
            intimacy_tiers = soul.get(
                "interaction_system", {}).get("intimacy_tiers", {})
            for tier, info in intimacy_tiers.items():
                locations = info.get("location_access", [])
                for loc in locations:
                    if loc not in valid_locations:
                        errors.append(
                            f"[{soul_type}] {soul_id}: Invalid location '{loc}' in tier {tier}")

        except Exception as e:
            errors.append(f"Error checking {filename}: {e}")

    return errors


print("--- Starting Referential Integrity Check ---")
std_errors = check_souls(SOULS_DIR, "Standard")
prem_errors = check_souls(PREMIUM_SOULS_DIR, "Premium")

all_errors = std_errors + prem_errors

if all_errors:
    print(f"Found {len(all_errors)} referential integrity errors:")
    with open("integrity_report_utf8.txt", "w", encoding="utf-8") as f:
        for err in all_errors:
            f.write(err + "\n")
            print(err)
else:
    print("All referential checks passed successfully!")
