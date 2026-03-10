"""
Phase 1: Schema Normalization Script
Applies 3 changes to all standard soul JSONs:
  1. Adds "type": "standard" after "version"
  2. Normalizes gender: "M" -> "Male", "F" -> "Female"
  3. Flattens stress_trigger.responses from staged keys to single "response" key
"""
import json
import os
import sys

SOULS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "souls")

GENDER_MAP = {"M": "Male", "F": "Female"}


def merge_stress_responses(responses: dict) -> str:
    """Merge multiple staged stress responses into one cohesive paragraph."""
    if not responses:
        return ""
    
    # If already a single "response" key or "ALL" key, just return it
    if "response" in responses:
        return responses["response"]
    if "ALL" in responses:
        return responses["ALL"]
    
    # If only two keys (template-style STRANGER_TRUSTED / SOUL_LINKED), merge them
    if len(responses) == 2 and "STRANGER_TRUSTED" in responses and "SOUL_LINKED" in responses:
        parts = []
        st = responses.get("STRANGER_TRUSTED", "").strip()
        sl = responses.get("SOUL_LINKED", "").strip()
        if st:
            parts.append(st)
        if sl:
            parts.append(f"At SOUL_LINKED: {sl}")
        return " ".join(parts)
    
    # Multiple STAGE_ keys - merge in order
    sorted_keys = sorted(responses.keys())
    parts = []
    for key in sorted_keys:
        val = responses[key].strip()
        if val:
            parts.append(val)
    
    return " ".join(parts)


def normalize_soul(filepath: str) -> dict:
    """Normalize a single soul JSON file. Returns a summary of changes made."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    changes = {}
    
    # 1. Add "type": "standard" if missing
    if "type" not in data:
        # We need to insert it after "version" - rebuild ordered dict
        new_data = {}
        for key, value in data.items():
            new_data[key] = value
            if key == "version":
                new_data["type"] = "standard"
        data = new_data
        changes["type_added"] = True
    
    # 2. Normalize gender
    identity = data.get("identity", {})
    old_gender = identity.get("gender", "")
    if old_gender in GENDER_MAP:
        identity["gender"] = GENDER_MAP[old_gender]
        changes["gender"] = f"{old_gender} -> {GENDER_MAP[old_gender]}"
    
    # 3. Flatten stress_trigger responses
    interaction = data.get("interaction_system", {})
    stress = interaction.get("stress_trigger", {})
    responses = stress.get("responses", {})
    
    if responses and "response" not in responses:
        merged = merge_stress_responses(responses)
        if merged:
            stress.pop("responses", None)
            stress["response"] = merged
            changes["stress_flattened"] = True
    
    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    return changes


def main():
    if not os.path.isdir(SOULS_DIR):
        print(f"ERROR: Souls directory not found: {SOULS_DIR}")
        sys.exit(1)
    
    print(f"Processing souls in: {SOULS_DIR}")
    print("=" * 60)
    
    total_files = 0
    total_changes = 0
    
    for filename in sorted(os.listdir(SOULS_DIR)):
        if not filename.endswith(".json") or filename.startswith("_"):
            continue
        
        filepath = os.path.join(SOULS_DIR, filename)
        if not os.path.isfile(filepath):
            continue
        
        try:
            changes = normalize_soul(filepath)
            total_files += 1
            
            if changes:
                total_changes += len(changes)
                change_list = ", ".join(f"{k}: {v}" for k, v in changes.items())
                print(f"  ✓ {filename}: {change_list}")
            else:
                print(f"  - {filename}: no changes needed")
        except Exception as e:
            print(f"  ✗ {filename}: ERROR - {e}")
    
    print("=" * 60)
    print(f"Processed {total_files} files, made {total_changes} changes total.")


if __name__ == "__main__":
    main()
