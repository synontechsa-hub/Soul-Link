
import json
import os
import glob
from typing import Dict, Any

# --- CONFIGURATION ---
TARGET_ROOT = r"d:\Coding\SynonTech\SoulLink_v1.5.6\_dev\data\souls"
TARGET_VERSION = "1.5.6"

def get_recognition_defaults(is_premium: bool) -> Dict[str, bool]:
    """
    Returns the recognition_protocol dictionary based on soul type.
    """
    return {
        # 1. ARCHITECT: All souls know he exists (Creator/God-figure)
        "architect_awareness": True,
        
        # 2. ALYSSA: All souls know the anomaly
        "alyssa_awareness": True,
        
        # 3. PRIMORDIAL: Only Premium souls (and specific others) know the Truth (Time/Space/Chaos)
        "primordial_awareness": True if is_premium else False,
        
        # 4. LINKER: Replaces standard_user_awareness. All souls know Linkers exist (Users).
        "linker_awareness": True,
        
        # 5. CREATOR: All souls have this true (for Alpha Testers / Unique Created Souls)
        "creator_awareness": True
    }

def update_soul_file(file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Determine Type
        soul_type = data.get("type", "standard") # Default to standard if missing
        is_premium = soul_type == "premium"
        
        # 1. Update Version
        data['version'] = TARGET_VERSION
        
        # 2. Update Meta Data
        if 'meta_data' not in data:
            data['meta_data'] = {}
        
        # Clean naming: remove old keys if they exist, or just overwrite with new dict?
        # User said: "change all the fields... to reflect these new naming schemas"
        # Strategy: Build new dict, preserving 'primordial_awareness' value if it explicitly exists 
        # (in case a standard soul was manually given awareness), otherwise use default.
        
        current_meta = data['meta_data'].get('recognition_protocol', {})
        
        # Check if we should preserve specific flags (like if a standard soul was modified to know primordials)
        # For this bulk update, we will leverage the `is_premium` logic but respect existing True values for primordials if sound.
        # Actually, simply enforcing the new schema is safer and cleaner as requested.
        
        new_recognition = get_recognition_defaults(is_premium)
        
        # Edge case: If current_meta had 'primordial_awareness' set to True explicitly, keep it?
        # For now, let's strictly follow the rule: Premium=True, Standard=False (unless we want to be fancy).
        # We will strictly enforce the defaults to ensure consistency as requested ("do all souls nce").
        
        data['meta_data']['recognition_protocol'] = new_recognition
            
        # 3. Save
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        status = "PREMIUM" if is_premium else "STD"
        print(f"[{status}] Updated: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to update {os.path.basename(file_path)}: {e}")
        return False

def main():
    print(f"Starting Bulk Schema Enforcement (v{TARGET_VERSION})...")
    print(f"Target Directory: {TARGET_ROOT}")
    
    # Recursive search
    count = 0
    errors = 0
    
    # Walk through all directories
    for root, dirs, files in os.walk(TARGET_ROOT):
        for file in files:
            if file.endswith(".json") and "_template.json" not in file:
                file_path = os.path.join(root, file)
                if update_soul_file(file_path):
                    count += 1
                else:
                    errors += 1
            
    print("-" * 30)
    print(f"Schema Update Complete.")
    print(f"Processed: {count} files")
    print(f"Errors: {errors}")

if __name__ == "__main__":
    main()
