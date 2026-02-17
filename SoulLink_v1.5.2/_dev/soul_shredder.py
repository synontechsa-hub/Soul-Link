import json
import os
import re

# Load the snapshot
with open('character_sheets_snapshot.json', 'r') as f:
    data = json.load(f)

output_base = "souls"
os.makedirs(output_base, exist_ok=True)

def parse_section(content, section_name):
    """Extracts a section from the text sheet using regex."""
    pattern = rf"{section_name}\n(.*?)(?=\n\n|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match: return {}
    
    lines = match.group(1).strip().split('\n')
    result = {}
    for line in lines:
        if ':' in line:
            key, val = line.split(':', 1)
            result[key.strip('- ').lower().replace(' ', '_')] = val.strip()
    return result

for soul_entry in data['files']:
    content = soul_entry['content']
    
    # 1. Extract Raw Data
    core_raw = parse_section(content, "Core Identity")
    app_raw = parse_section(content, "Appearance")
    pers_raw = parse_section(content, "Personality")
    voice_raw = parse_section(content, "Voice & Tone")
    integ_raw = parse_section(content, "App Integration")
    model_raw = parse_section(content, "Dialogue Model")
    
    soul_id = core_raw.get('name', 'unknown').lower()
    soul_dir = os.path.join(output_base, soul_id)
    os.makedirs(soul_dir, exist_ok=True)

    # 2. Build CORE.JSON
    core_data = {
        "identity": {
            "name": core_raw.get('name'),
            "age": core_raw.get('age'),
            "gender": core_raw.get('gender'),
            "archetype": core_raw.get('archetype')
        },
        "appearance": {
            "physical": app_raw.get('physical'),
            "clothing": app_raw.get('clothing_style'),
            "visual_tone": app_raw.get('visual_tone'),
            "aesthetic": app_raw.get('aesthetic')
        }
    }

    # 3. Build CONTEXT.JSON
    context_data = {
        "persona": {
            "public": pers_raw.get('public_persona'),
            "private": pers_raw.get('private_persona'),
            "traits": pers_raw.get('traits', "").split(','),
            "flaws": pers_raw.get('flaws', "").split(',')
        },
        "psychographics": {
            "motivations": pers_raw.get('motivations', "").split(','),
            "goal": integ_raw.get('user_experience_goal')
        },
        "lore": {
            "background": core_raw.get('background')
        }
    }

    # 4. Build METADATA.JSON (High-Fidelity)
    metadata_data = {
        "dialogue": {
            "model": model_raw.get('model', 'llama2'),
            "system_prompt": model_raw.get('systemprompt'),
            "style_hints": model_raw.get('stylehints', "").split(',')
        },
        "social_engine": {
            "trust": 0.1,
            "affection": 0.1,
            "tension": 0.0
        },
        "ui": {
            "theme_palette": integ_raw.get('theme_palette'),
            "card_variants": ["Standard"]
        }
    }

    # Write files
    with open(f"{soul_dir}/core.json", 'w') as f: json.dump(core_data, f, indent=2)
    with open(f"{soul_dir}/context.json", 'w') as f: json.dump(context_data, f, indent=2)
    with open(f"{soul_dir}/metadata.json", 'w') as f: json.dump(metadata_data, f, indent=2)

print(f"✅ Shredding complete. {len(data['files'])} souls migrated to the Pillar system.")