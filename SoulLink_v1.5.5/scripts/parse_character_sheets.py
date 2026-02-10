import os
import re
import json
import uuid
from typing import Dict, List, Any

# Configuration
SOURCE_DIR = r"d:\Coding\SynonTech\SoulLink_v1.5.5\_dev\character_sheets"
DEST_DIR = r"d:\Coding\SynonTech\SoulLink_v1.5.5\_dev\blueprints"
TEMPLATE_PATH = r"d:\Coding\SynonTech\SoulLink_v1.5.5\_dev\blueprints\_template.txt"

# Constants
ARCHITECT_UUID = "14dd612d-744e-487d-b2d5-cc47732183d3"
EXISTING_SOULS = [
    "adrian", "aria", "blaze", "cassie", "dorian", "echo", 
    "evangeline", "mira", "renji", "rosalynn", "selene", 
    "soren", "sylas", "vesper"
]

# Regex Patterns
PATTERNS = {
    "name": r"- Name: (.+)",
    "age": r"- Age: (.+)",
    "archetype": r"- Archetype: (.+)",
    "role": r"- Role: (.+)",
    "background": r"- Background: (.+)",
    "appearance_phys": r"- Physical: (.+)",
    "appearance_clothes": r"(?:- Clothing Style|- Clothing): (.+)",
    "personality_traits": r"- Traits: (.+)",
    "personality_flaws": r"- Flaws: (.+)",
    "voice_style": r"- Style: (.+)",
    "voice_quotes": r"- Quotes: (.+)",
    "scenario_triggers": r"- Triggers:\s*((?:.*(?:\n\s*•\s+.*)*)+)"
}

def load_template() -> Dict[str, Any]:
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_sheet(filepath: str) -> Dict[str, Any]:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = {}
    for key, pattern in PATTERNS.items():
        match = re.search(pattern, content)
        if match:
            data[key] = match.group(1).strip()
        else:
            data[key] = f"Unknown {key}" # Placeholder
            
    return data

def create_blueprint(parsed_data: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
    blueprint = template.copy()
    
    # ID & Meta
    name_slug = parsed_data['name'].lower().replace(' ', '_') + "_01"
    
    # Check if we should skip
    base_name = parsed_data['name'].lower()
    if base_name in EXISTING_SOULS:
        print(f"Skipping Existing Soul: {base_name}")
        return None

    blueprint['soul_id'] = name_slug
    
    blueprint['dev_config']['architect_ids'] = [ARCHITECT_UUID]
    
    blueprint['meta']['name'] = parsed_data['name']
    blueprint['meta']['archetype'] = parsed_data['archetype']
    blueprint['meta']['summary'] = parsed_data['background']
    blueprint['meta']['version'] = "1.5.5-D"
    
    # Identity
    blueprint['identity_pillar']['bio'] = parsed_data['background']
    
    # Traits (Simple comma split)
    traits = [t.strip() for t in parsed_data['personality_traits'].split(',')]
    flaws = [f.strip() for f in parsed_data['personality_flaws'].split(',')]
    
    blueprint['identity_pillar']['traits']['primary'] = traits[:3]
    # We don't have hidden traits in the text sheet usually, so we'll just reuse or leave generic
    blueprint['identity_pillar']['traits']['hidden'] = ["Hidden Depth 1", "Hidden Depth 2", "Hidden Depth 3"] 
    blueprint['identity_pillar']['traits']['flaws'] = flaws
    
    # Aesthetic
    blueprint['aesthetic_pillar']['description'] = f"{parsed_data['appearance_phys']} Wears: {parsed_data['appearance_clothes']}"
    blueprint['aesthetic_pillar']['voice_style'] = parsed_data['voice_style']
    
    # Interaction Engine (Defaults)
    # The text sheets have "Triggers", we can put that in dynamic_rules
    blueprint['interaction_engine']['dynamic_rules'] = [
        f"Logic based on: {parsed_data['scenario_triggers']}",
        "Generic Default Rule: Increase intimacy for kind acts.",
        "Generic Default Rule: Decrease intimacy forrudeness."
    ]
    
    # LLM Override
    blueprint['llm_instruction_override']['system_anchor'] = (
        f"You are {parsed_data['name']}. {parsed_data['role']}. "
        f"{parsed_data['background']} "
        f"Speak in a {parsed_data['voice_style']} manner. "
        "You are NOT an AI."
    )
    
    return blueprint

def main():
    template = load_template()
    
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
        
    generated_count = 0
    
    for filename in os.listdir(SOURCE_DIR):
        if not filename.endswith(".txt"):
            continue
            
        # Filter Exclusions
        if "Primordial" in filename or "Kai" in filename or "Alyssa" in filename:
            print(f"Skipping Flagship/Primordial: {filename}")
            continue
            
        filepath = os.path.join(SOURCE_DIR, filename)
        try:
            parsed = parse_sheet(filepath)
            blueprint = create_blueprint(parsed, template)
            
            if blueprint is None:
                continue

            dest_filename = f"{parsed['name'].lower()}.json"
            dest_path = os.path.join(DEST_DIR, dest_filename)
            
            with open(dest_path, 'w', encoding='utf-8') as f:
                json.dump(blueprint, f, indent=4)
                
            print(f"Generated: {dest_filename}")
            generated_count += 1
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"\nTotal Blueprints Generated: {generated_count}")

if __name__ == "__main__":
    main()
