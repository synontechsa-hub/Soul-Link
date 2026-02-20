
import json
import os
import glob
from typing import Dict, Any

# --- CONFIGURATION ---
TARGET_DIR = r"d:\Coding\SynonTech\SoulLink_v1.5.6\_dev\data\souls"
TARGET_VERSION = "1.5.6"

AWARENESS_PROTOCOL = {
    "alyssa_awareness": True,
    "administrator_awareness": True,
    "architect_awareness": True,
    "primordial_awareness": False,
    "flagship_awareness": False
}

def update_soul_file(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 1. Update Version
        data['version'] = TARGET_VERSION
        
        # 2. Update Meta Data
        if 'meta_data' not in data:
            data['meta_data'] = {}
        
        # Ensure recognition_protocol exists
        if 'recognition_protocol' not in data['meta_data']:
            data['meta_data']['recognition_protocol'] = {}
            
        # Update flags (overwrite or add)
        for key, value in AWARENESS_PROTOCOL.items():
            data['meta_data']['recognition_protocol'][key] = value
            
        # 3. Save
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        print(f"[OK] Updated: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to update {os.path.basename(file_path)}: {e}")
        return False

def main():
    print(f"Starting Batch Update to v{TARGET_VERSION}...")
    print(f"Target Directory: {TARGET_DIR}")
    
    # Get all JSON files in the directory (excluding subdirectories)
    json_files = glob.glob(os.path.join(TARGET_DIR, "*.json"))
    
    count = 0
    errors = 0
    
    for file_path in json_files:
        # Skip _template.json if present
        if "_template.json" in file_path:
            continue
            
        if update_soul_file(file_path):
            count += 1
        else:
            errors += 1
            
    print("-" * 30)
    print(f"Update Complete.")
    print(f"Processed: {count} files")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    main()
