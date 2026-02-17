"""
Soul Data Consistency Audit Script
Validates all soul JSON files against baseline schema and system data.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set

# Paths
SOULS_DIR = Path(r"d:\Coding\SynonTech\SoulLink_v1.5.6\_dev\data\souls")
SYSTEM_DIR = Path(r"d:\Coding\SynonTech\SoulLink_v1.5.6\_dev\data\system")
LOCATIONS_FILE = Path(r"d:\Coding\SynonTech\SoulLink_v1.5.6\_dev\data\locations\_known_locations.json")

# Load reference data
with open(SYSTEM_DIR / "archetypes.json", "r", encoding="utf-8") as f:
    archetypes_data = json.load(f)
    VALID_ARCHETYPES = set(archetypes_data["archetypes"].keys())

with open(SYSTEM_DIR / "routines.json", "r", encoding="utf-8") as f:
    routines_data = json.load(f)
    VALID_ROUTINES = {k for k in routines_data.keys() if k not in ["routines_id", "version"]}

with open(SYSTEM_DIR / "zones.json", "r", encoding="utf-8") as f:
    zones_data = json.load(f)
    VALID_ZONES = set(zones_data["zones"].keys())
    VALID_LOCATIONS = set()
    for zone_data in zones_data["zones"].values():
        VALID_LOCATIONS.update(zone_data["locations"])

with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
    locations_list = json.load(f)
    KNOWN_LOCATION_IDS = {loc["id"] for loc in locations_list}

# Load baseline schema from adrian_01.json
with open(SOULS_DIR / "adrian_01.json", "r", encoding="utf-8") as f:
    BASELINE = json.load(f)

# Required top-level fields
REQUIRED_FIELDS = [
    "soul_id", "version", "author_id", "identity", "aesthetic", 
    "systems_config", "routine", "inventory", "relationships",
    "lore_associations", "interaction_system", "prompts"
]

REQUIRED_IDENTITY_FIELDS = [
    "name", "age", "gender", "archetype_id", "faction_id", 
    "occupation", "summary", "bio", "personality_traits"
]

REQUIRED_ROUTINE_FIELDS = ["template_id", "location_preferences", "schedule_overrides"]

REQUIRED_LOCATION_PREFS = [
    "home_zone", "work_zone", "entertainment_zone", "relaxation_zone",
    "dining_zone", "nightlife_zone", "cultural_zone", "sports_zone",
    "underground_zone", "public_square_zone"
]

# Audit results
errors = []
warnings = []
soul_ids = set()
relationship_map = {}

def audit_soul(filepath: Path):
    """Audit a single soul JSON file."""
    soul_name = filepath.stem
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"{soul_name}: JSON PARSE ERROR - {e}")
        return
    except Exception as e:
        errors.append(f"{soul_name}: FILE READ ERROR - {e}")
        return
    
    # 1. Check required top-level fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"{soul_name}: MISSING FIELD '{field}'")
    
    # 2. Check version consistency
    if data.get("version") != "1.5.5":
        warnings.append(f"{soul_name}: VERSION MISMATCH (expected '1.5.5', got '{data.get('version')}')")
    
    # 3. Check soul_id matches filename
    if data.get("soul_id") != soul_name:
        errors.append(f"{soul_name}: SOUL_ID MISMATCH (filename: {soul_name}, soul_id: {data.get('soul_id')})")
    
    soul_ids.add(data.get("soul_id"))
    
    # 4. Check identity fields
    identity = data.get("identity", {})
    for field in REQUIRED_IDENTITY_FIELDS:
        if field not in identity:
            errors.append(f"{soul_name}: MISSING IDENTITY FIELD '{field}'")
    
    # 5. Validate archetype_id
    archetype_id = identity.get("archetype_id")
    if archetype_id and archetype_id not in VALID_ARCHETYPES:
        errors.append(f"{soul_name}: INVALID ARCHETYPE '{archetype_id}'")
    
    # 6. Check routine structure
    routine = data.get("routine", {})
    for field in REQUIRED_ROUTINE_FIELDS:
        if field not in routine:
            errors.append(f"{soul_name}: MISSING ROUTINE FIELD '{field}'")
    
    # 7. Validate routine template_id
    template_id = routine.get("template_id")
    if template_id and template_id not in VALID_ROUTINES:
        errors.append(f"{soul_name}: INVALID ROUTINE TEMPLATE '{template_id}'")
    
    # 8. Validate location preferences
    location_prefs = routine.get("location_preferences", {})
    for zone in REQUIRED_LOCATION_PREFS:
        if zone not in location_prefs:
            errors.append(f"{soul_name}: MISSING LOCATION PREFERENCE '{zone}'")
        else:
            location_id = location_prefs[zone]
            if location_id not in KNOWN_LOCATION_IDS:
                errors.append(f"{soul_name}: INVALID LOCATION '{location_id}' in '{zone}'")
    
    # 9. Check portrait path format
    portrait_path = data.get("aesthetic", {}).get("portrait_path", "")
    expected_portrait = f"/assets/images/souls/{soul_name}.png"
    if portrait_path != expected_portrait:
        warnings.append(f"{soul_name}: PORTRAIT PATH MISMATCH (expected '{expected_portrait}', got '{portrait_path}')")
    
    # 10. Store relationships for cross-reference check
    relationships = data.get("relationships", {})
    relationship_map[soul_name] = set(relationships.keys())
    
    # 11. Check intimacy tiers structure
    interaction_system = data.get("interaction_system", {})
    intimacy_tiers = interaction_system.get("intimacy_tiers", {})
    required_tiers = ["STRANGER", "TRUSTED", "SOUL_LINKED"]
    for tier in required_tiers:
        if tier not in intimacy_tiers:
            errors.append(f"{soul_name}: MISSING INTIMACY TIER '{tier}'")

def check_reciprocal_relationships():
    """Check that all relationships have reciprocal entries."""
    for soul_a, relationships in relationship_map.items():
        for soul_b in relationships:
            if soul_b not in soul_ids:
                warnings.append(f"{soul_a}: RELATIONSHIP REFERENCES NON-EXISTENT SOUL '{soul_b}'")
            elif soul_b in relationship_map and soul_a not in relationship_map[soul_b]:
                warnings.append(f"{soul_a} -> {soul_b}: MISSING RECIPROCAL RELATIONSHIP")

# Run audit on all soul files
soul_files = sorted(SOULS_DIR.glob("*_01.json"))
print(f"Auditing {len(soul_files)} soul files...\n")

for soul_file in soul_files:
    audit_soul(soul_file)

# Check reciprocal relationships
check_reciprocal_relationships()

# Write results to file
output_file = Path(r"d:\Coding\SynonTech\SoulLink_v1.5.6\_dev\scripts\soul_audit_report.txt")
with open(output_file, "w", encoding="utf-8") as f:
    f.write("=" * 80 + "\n")
    f.write("SOUL DATA CONSISTENCY AUDIT REPORT\n")
    f.write("=" * 80 + "\n")
    f.write(f"\nTotal Souls Audited: {len(soul_files)}\n")
    f.write(f"Total Errors: {len(errors)}\n")
    f.write(f"Total Warnings: {len(warnings)}\n")

    if errors:
        f.write("\n" + "=" * 80 + "\n")
        f.write("ERRORS (MUST FIX)\n")
        f.write("=" * 80 + "\n")
        for error in errors:
            f.write(f"  ❌ {error}\n")

    if warnings:
        f.write("\n" + "=" * 80 + "\n")
        f.write("WARNINGS (SHOULD REVIEW)\n")
        f.write("=" * 80 + "\n")
        for warning in warnings:
            f.write(f"  ⚠️  {warning}\n")

    if not errors and not warnings:
        f.write("\n✅ ALL SOULS PASSED AUDIT! No errors or warnings found.\n")

    f.write("\n" + "=" * 80 + "\n")

print(f"Audit complete! Report written to: {output_file}")
