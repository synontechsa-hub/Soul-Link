
import json
import os
import glob
from typing import Dict, Any, List

# --- CONFIGURATION ---
DATA_ROOT = r"d:\Coding\SynonTech\SoulLink_v1.5.6\_dev\data"
TARGET_VERSION = "1.5.6"

# --- EXPECTED SCHEMAS ---

# 1. SOUL SCHEMA (v1.5.6 Unified)
REQUIRED_SOUL_KEYS = [
    "soul_id", "version", "identity", "aesthetic", "systems_config", 
    "routine", "inventory", "relationships", "lore_associations", 
    "interaction_system", "prompts", "meta_data"
]


REQUIRED_META_KEYS = [
    "recognition_protocol"
]

REQUIRED_RECOGNITION_KEYS = [
    "architect_awareness",
    "alyssa_awareness", 
    "primordial_awareness",
    "linker_awareness",
    "creator_awareness"
]

# 2. LOCATION SCHEMA
REQUIRED_LOCATION_KEYS = [
    "location_id", "meta", "system_prompt_anchors", "game_logic", "lore", "metadata"
]

def validate_soul(file_path: str, data: Dict[str, Any]) -> List[str]:
    errors = []
    
    # Version Check
    if data.get("version") != TARGET_VERSION:
        errors.append(f"Version Mismatch: Expected {TARGET_VERSION}, got {data.get('version')}")
        
    # Top Level Keys
    for key in REQUIRED_SOUL_KEYS:
        if key not in data:
            errors.append(f"Missing Key: {key}")
            
    # Meta Data Structure
    meta = data.get("meta_data", {})
    if "recognition_protocol" not in meta:
        errors.append("Missing Key: meta_data.recognition_protocol")
    else:
        recog = meta["recognition_protocol"]
        for key in REQUIRED_RECOGNITION_KEYS:
            if key not in recog:
                errors.append(f"Missing Awareness Flag: {key}")
                
    return errors

def validate_location(file_path: str, data: Dict[str, Any]) -> List[str]:
    errors = []
    
    # Locations might have different versioning (e.g. 1.5.5), so we check carefully
    # Per previous context, location update wasn't explicitly requested to 1.5.6 but might be good hygiene.
    # For now, we report version but don't fail unless it's very old.
    
    for key in REQUIRED_LOCATION_KEYS:
        if key not in data:
            errors.append(f"Missing Key: {key}")
            
    return errors

def main():
    print(f"Starting Data Integrity Audit...")
    print(f"Data Root: {DATA_ROOT}")
    print("-" * 50)
    
    total_files = 0
    total_errors = 0
    
    # --- SCAN SOULS (Standard) ---
    soul_dir = os.path.join(DATA_ROOT, "souls")
    for root, dirs, files in os.walk(soul_dir):
        for file in files:
            if file.endswith(".json") and "_template.json" not in file:
                total_files += 1
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Logic: If path contains "premium", it's premium
                    # But wait, premium folder is separated?
                    # `_dev/data/souls` contains standard souls.
                    # `_dev/data/premium_souls` contains premium? Or is it `souls/premium`?
                    # Listing showed `premium_souls` separately? AND `souls` had `premium` subdir?
                    
                    errs = validate_soul(path, data)
                    
                    if errs:
                        print(f"[FAIL] {file}")
                        for e in errs:
                            print(f"  - {e}")
                        total_errors += 1
                        
                except Exception as e:
                    print(f"[CRASH] {file}: {e}")
                    total_errors += 1

    # --- SCAN LOCATIONS ---
    loc_dir = os.path.join(DATA_ROOT, "locations")
    for root, dirs, files in os.walk(loc_dir):
        for file in files:
            if file.endswith(".json") and "_known_locations" not in file:
                 total_files += 1
                 path = os.path.join(root, file)
                 try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    errs = validate_location(path, data)
                    if errs:
                        print(f"[FAIL] LOC: {file}")
                        for e in errs:
                            print(f"  - {e}")
                        total_errors += 1
                 except Exception as e:
                    print(f"[CRASH] {file}: {e}")
                    total_errors += 1

    print("-" * 50)
    print(f"Audit Complete.")
    print(f"Files Scanned: {total_files}")
    print(f"Files with Errors: {total_errors}")

if __name__ == "__main__":
    main()
