"""
Generate new character sheets from old .txt and .json files.
Merges data, INVOLVES SMART INFERENCE, and creates human-readable character sheets.
"""

import json
import os
import re
import random
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
OLD_SHEETS_DIR = BASE_DIR / "character_sheets" / "old_sheets"
OLD_JSON_DIR = BASE_DIR / "blueprints" / "old_souls_style"
OUTPUT_DIR = BASE_DIR / "character_sheets"

# Default values
AUTHOR_UUID = "14dd612d-744e-487d-b2d5-cc47732183d3"
AUTHOR_NAME = "Syn"

# Known locations with metadata for inference
LOCATION_METADATA = {
    "shadowed_archives": {"tags": ["intellectual", "mysterious", "quiet"], "type": "public"},
    "linkgate_mall": {"tags": ["social", "shopping", "public"], "type": "public"},
    "soul_plaza": {"tags": ["social", "public", "generic"], "type": "public"},
    "the_garden": {"tags": ["nature", "quiet", "romantic"], "type": "public"},
    "scenic_overlook": {"tags": ["nature", "romantic", "quiet"], "type": "public"},
    "crimson_arms": {"tags": ["street", "gritty", "residential"], "type": "home"},
    "skylink_tower": {"tags": ["corporate", "rich", "elite"], "type": "work"},
    "linkview_cuisine": {"tags": ["rich", "romantic", "food"], "type": "public"},
    "apex_corporate_plaza": {"tags": ["corporate", "work", "busy"], "type": "public"},
    "rooftop_lounge": {"tags": ["rich", "party", "social"], "type": "public"},
    "zenith_lounge": {"tags": ["rich", "party", "social"], "type": "public"},
    "circuit_street": {"tags": ["street", "gritty", "cyberpunk"], "type": "public"},
    "stop_n_go": {"tags": ["street", "mechanic", "work"], "type": "work"},
    "circuit_diner": {"tags": ["street", "food", "casual"], "type": "public"},
    "midline_residences": {"tags": ["average", "residential"], "type": "home"},
    "iron_resolve_gym": {"tags": ["fitness", "active", "public"], "type": "public"},
    "linkside_estate": {"tags": ["rich", "elite", "residential"], "type": "home"},
    "dollhouse_dungeon": {"tags": ["kinky", "dark", "club"], "type": "public"},
    "neon_span_bridge": {"tags": ["transit", "romantic", "public"], "type": "public"},
    "ether_baths": {"tags": ["relax", "spa", "rich"], "type": "public"},
    "twilight_park": {"tags": ["nature", "quiet", "mysterious"], "type": "public"},
    "city_planetarium": {"tags": ["intellectual", "romantic", "quiet"], "type": "public"},
    "echo_archives": {"tags": ["intellectual", "mysterious"], "type": "public"},
    "neon_nights": {"tags": ["party", "club", "street"], "type": "public"},
    "pixel_den": {"tags": ["gaming", "casual", "tech"], "type": "public"},
    "umbral_exchange": {"tags": ["shady", "trade", "street"], "type": "public"}
}

KNOWN_LOCATIONS = list(LOCATION_METADATA.keys())

# Known souls (loaded dynamically or hardcoded)
KNOWN_SOULS = [
    "adrian", "akira", "amber", "anzu", "aria", "blaze", "cassie", "chiara",
    "clair", "daichi", "dorian", "echo", "elizabeth", "evangeline", "hana",
    "haruto", "heather", "juno", "kana", "lyra", "mai", "mami", "mariko",
    "mira", "momoka", "nova", "nozomi", "orion", "reina", "renji", "rosalynn",
    "rubii", "selene", "soren", "sylas", "talia", "tatiana", "vesper"
]

# Inference Logic Helpers
def get_vibe_from_archetype(archetype, bio):
    text = (archetype + " " + bio).lower()
    
    if any(x in text for x in ["rich", "elite", "ceo", "executive", "princess", "heiress", "corporate", "arrogant"]):
        return "rich"
    if any(x in text for x in ["rebel", "street", "thug", "punk", "mechanic", "outcast", "gritty", "fighter"]):
        return "street"
    if any(x in text for x in ["smart", "library", "book", "shy", "quiet", "researcher", "student", "intellectual"]):
        return "intellectual"
    if any(x in text for x in ["idol", "star", "popular", "social", "party", "energetic", "cheerful"]):
        return "social"
    if any(x in text for x in ["nature", "calm", "gentle", "healer", "spirit"]):
        return "nature"
    return "average"

def infer_home(vibe):
    options = [loc for loc, meta in LOCATION_METADATA.items() if meta['type'] == 'home' and (vibe in meta['tags'] or 'residential' in meta['tags'])]
    
    # Specific overrides
    if vibe == "rich":
        return "linkside_estate"
    if vibe == "street":
        return "crimson_arms"
    if vibe == "average":
        return "midline_residences"
        
    return random.choice(options) if options else "midline_residences"

def infer_job(vibe, archetype):
    arch = archetype.lower()
    if "mechanic" in arch: return ("stop_n_go", "Head Mechanic")
    if "maid" in arch: return ("linkview_cuisine", "Server")
    if "idol" in arch: return ("link_city_arena", "Performer")
    if "nurse" in arch: return ("ether_baths", "Healer")
    if "student" in arch: return ("shadowed_archives", "Student")
    
    if vibe == "rich": return ("skylink_tower", "Executive Consultant")
    if vibe == "street": return ("circuit_diner", "Line Cook")
    if vibe == "intellectual": return ("shadowed_archives", "Archivist")
    if vibe == "social": return ("linkgate_mall", "Brand Ambassador")
    
    return (None, None)

def infer_routines(home, job_loc, vibe):
    routines = {}
    routines['home_time'] = home
    routines['night'] = home
    
    # Work logic
    if job_loc:
        routines['morning'] = job_loc
        routines['afternoon'] = job_loc
    else:
        # Unemployed logic
        if vibe == "street":
            routines['morning'] = "midline_residences"
            routines['afternoon'] = "circuit_street"
        elif vibe == "rich":
            routines['morning'] = "ether_baths"
            routines['afternoon'] = "linkgate_mall"
        else:
            routines['morning'] = "the_garden"
            routines['afternoon'] = "soul_plaza"

    # Evening is for fun
    fun_spots = [loc for loc, meta in LOCATION_METADATA.items() if vibe in meta['tags'] and meta['type'] == 'public']
    routines['evening'] = random.choice(fun_spots) if fun_spots else "soul_plaza"
    
    return routines

def infer_relationships(name, archetype, vibe, key_items):
    # Pick 2 random souls
    others = [s for s in KNOWN_SOULS if s.lower() != name.lower()]
    selected = random.sample(others, 2)
    
    rels = []
    for other in selected:
        rel_type = "friend" if random.random() > 0.5 else "rival"
        # Simple logic: Street vs Rich = Rival
        
        rels.append({
            "soul_id": f"{other}_01",
            "type": rel_type,
            "relationship_strength": "0.5",
            "interaction_effect": f"Typical {rel_type} dynamics",
            "shared_location": "soul_plaza",
            "notes": "Inferred connection"
        })
    return rels


def parse_old_txt(filepath):
    """Parse old character sheet .txt file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    data = {}
    # Extract name
    name_match = re.search(r'- Name:\s*(.+)', content)
    data['name'] = name_match.group(1).strip() if name_match else ""
    # Extract age
    age_match = re.search(r'- Age:\s*(\d+)', content)
    data['age'] = age_match.group(1) if age_match else "25"
    # Extract gender
    gender_match = re.search(r'- Gender:\s*(.+)', content)
    gender_raw = gender_match.group(1).strip() if gender_match else "Female"
    data['gender'] = "M" if gender_raw.lower() == "male" else "F" if gender_raw.lower() == "female" else "NB"
    # Extract archetype
    archetype_match = re.search(r'- Archetype:\s*(.+)', content)
    data['archetype'] = archetype_match.group(1).strip() if archetype_match else ""
    # Extract background
    bg_match = re.search(r'- Background:\s*(.+)', content)
    data['background'] = bg_match.group(1).strip() if bg_match else ""
    # Extract physical
    phys_match = re.search(r'- Physical:\s*(.+)', content)
    data['physical'] = phys_match.group(1).strip() if phys_match else ""
    # Extract clothing
    clothing_match = re.search(r'- Clothing(?:\s+Style)?:\s*(.+)', content)
    data['clothing'] = clothing_match.group(1).strip() if clothing_match else ""
    # Extract voice style
    voice_match = re.search(r'- Style:\s*(.+)', content, re.MULTILINE)
    data['voice_style'] = voice_match.group(1).strip() if voice_match else ""
    # Extract traits/flaws
    traits_match = re.search(r'- Traits:\s*(.+)', content)
    data['traits'] = traits_match.group(1).strip() if traits_match else ""
    flaws_match = re.search(r'- Flaws:\s*(.+)', content)
    data['flaws'] = flaws_match.group(1).strip() if flaws_match else ""
    
    return data

def parse_old_json(filepath):
    if not filepath.exists(): return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_character_sheet(name, txt_data, json_data):
    soul_id = f"{name.lower()}_01"
    
    # Basic Data
    archetype = json_data.get('meta', {}).get('archetype', txt_data.get('archetype', ''))
    summary = json_data.get('meta', {}).get('summary', txt_data.get('background', ''))
    bio = json_data.get('identity_pillar', {}).get('bio', txt_data.get('background', ''))
    
    # INFERENCE ENGINE START
    vibe = get_vibe_from_archetype(archetype, bio)
    
    # 1. Locations
    meta = json_data.get('meta', {})
    home_loc = meta.get('home_location', infer_home(vibe))
    
    # 2. Jobs
    job_loc, job_role = infer_job(vibe, archetype)
    is_employed = "Yes" if job_loc else "No"
    
    # 3. Routines
    existing_routines = meta.get('routines', {})
    inferred_routines = infer_routines(home_loc, job_loc, vibe)
    final_routines = {
        'morning': existing_routines.get('morning', inferred_routines['morning']),
        'afternoon': existing_routines.get('afternoon', inferred_routines['afternoon']),
        'evening': existing_routines.get('evening', inferred_routines['evening']),
        'night': existing_routines.get('night', inferred_routines['night']),
        'home_time': existing_routines.get('home_time', inferred_routines['home_time'])
    }
    
    # 4. Starting Location
    starting_loc = meta.get('starting_location', final_routines['morning']) # Start where they are in morning
    
    # 5. Relationships
    existing_rels = json_data.get('world_presence', {}).get('relationships_with_souls', [])
    if not existing_rels:
        existing_rels = infer_relationships(name, archetype, vibe, [])

    # INFERENCE ENGINE END
    
    # Formatting fields
    physical = txt_data.get('physical', '')
    clothing = txt_data.get('clothing', '')
    description = json_data.get('aesthetic_pillar', {}).get('description', f"{physical}. Wears: {clothing}")
    voice_style = json_data.get('aesthetic_pillar', {}).get('voice_style', txt_data.get('voice_style', ''))
    
    traits_primary = json_data.get('identity_pillar', {}).get('traits', {}).get('primary', [])
    if not traits_primary:
        traits_str = txt_data.get('traits', '')
        traits_primary = [t.strip() for t in traits_str.split(',')][:3] if traits_str else []
        
    traits_hidden = json_data.get('identity_pillar', {}).get('traits', {}).get('hidden', [])
    if not traits_hidden or "Hidden Depth" in str(traits_hidden):
        traits_hidden = ["Inferred Hidden Trait 1", "Inferred Hidden Trait 2", "Inferred Hidden Trait 3"]
        
    traits_flaws = json_data.get('identity_pillar', {}).get('traits', {}).get('flaws', [])
    if not traits_flaws:
        flaws_str = txt_data.get('flaws', '')
        flaws_list = [f.strip() for f in flaws_str.split(',')][:3] if flaws_str else []
        traits_flaws = [f"{flaw} ([NEEDS EXPLANATION])" for flaw in flaws_list]
        
    key_items = json_data.get('identity_pillar', {}).get('key_items', {})
    capabilities = json_data.get('meta', {}).get('capabilities', {})
    content_rating = json_data.get('meta', {}).get('content_rating', 'mature')
    consent = json_data.get('meta', {}).get('consent_model', {})
    intimacy = json_data.get('interaction_engine', {}).get('intimacy_tiers', {}) or json_data.get('interaction_engine', {}).get('tiers', {})
    dynamic_rules = json_data.get('interaction_engine', {}).get('dynamic_rules', [])
    llm_anchor = json_data.get('llm_instruction_override', {}).get('system_anchor', '') or json_data.get('llm_system_anchor', '')
    emote = json_data.get('aesthetic_pillar', {}).get('signature_emote', '✨')

    sheet = f"""# CHARACTER SHEET: {name}

---
**Meta Information**
- Soul ID: {soul_id}
- Author: {AUTHOR_NAME} / Synonimity
- Author UUID: {AUTHOR_UUID}
- Version: 1.5.5
- Completion Status: draft
- Last Updated: {datetime.now().strftime('%Y-%m-%d')}
---

## CORE IDENTITY

**Name:** {name}  
**Age:** {txt_data.get('age', '25')}  
**Gender:** {txt_data.get('gender', 'F')}  
**Archetype:** {archetype}  
**Content Rating:** {content_rating}

**Summary** (2-3 sentences - who they are BENEATH the mask):
{summary}

**Bio** (4-6 sentences - who are they, what do they want, what's their conflict, what are they hiding):
{bio}

---

## APPEARANCE & AESTHETIC

**Physical Description** (2-3 sentences):
{description}

**Clothing Style:**
{clothing}

**Voice & Speech Style:**
{voice_style}

**Signature Emote:** {emote}

**Things They Would NEVER Do/Say:**
{format_list(json_data.get('aesthetic_pillar', {}).get('sensory_forbidden', ['[NEEDS AUTHORING]', '[NEEDS AUTHORING]', '[NEEDS AUTHORING]']))}

---

## PERSONALITY DEEP DIVE

### Traits

**Primary (What the world sees):**
{format_list(traits_primary)}

**Hidden (Revealed only at high intimacy):**
{format_list(traits_hidden)}

**Flaws (With explanations):**
{format_list(traits_flaws)}

### Key Items (Name + Symbolic Meaning)

{format_key_items(key_items)}

---

## WORLD INTEGRATION

**Starting Location:** {starting_loc}  
**Home Location:** {home_loc}

**Daily Routines:**
- Morning (06:00-12:00): {final_routines.get('morning', '[NEEDS LOCATION]')}
- Afternoon (12:00-18:00): {final_routines.get('afternoon', '[NEEDS LOCATION]')}
- Evening (18:00-22:00): {final_routines.get('evening', '[NEEDS LOCATION]')}
- Night (22:00-04:00): {final_routines.get('night', '[NEEDS LOCATION]')}
- Home Time (04:00-06:00): {final_routines.get('home_time', home_loc)}

**Employment:**
- Employed: {is_employed}
- Location: {job_loc if job_loc else "[Not Employed]"}
- Role: {job_role if job_role else "[N/A]"}
- Shift Times: Morning/Afternoon
- Salary per Shift: 150

---

## CAPABILITIES & CONSENT

**Capabilities:**
- Romance: {str(capabilities.get('romance', True)).lower()}
- Sexual Content: {str(capabilities.get('sexual_content', True)).lower()}
- Explicit Language: {str(capabilities.get('explicit_language', False)).lower()}
- Emotional Dependency: {str(capabilities.get('emotional_dependency', True)).lower()}

**Consent Model:**

*Explicit Consent Required For:*
{format_list(consent.get('explicit_consent_required_for', ['[NEEDS AUTHORING]', '[NEEDS AUTHORING]']))}

*Can Initiate:*
- Emotional Support: {str(consent.get('can_initiate', {}).get('emotional_support', True)).lower()}
- Protective Gestures: {str(consent.get('can_initiate', {}).get('protective_gestures', True)).lower()}
- Physical Touch: {str(consent.get('can_initiate', {}).get('physical_touch', False)).lower()}

*Character-Specific Consent Notes* (2+ sentences, NO generic templates):
{consent.get('notes', '[NEEDS AUTHORING - Character-specific consent behavior based on ' + archetype + ']')}

---

## INTIMACY PROGRESSION

{format_intimacy_tier('STRANGER', intimacy.get('STRANGER', {}), 0.8)}

{format_intimacy_tier('TRUSTED', intimacy.get('TRUSTED', {}), 1.2)}

{format_intimacy_tier('SOUL_LINKED', intimacy.get('SOUL_LINKED', {}), 1.5)}

---

## DYNAMIC INTERACTION RULES

**Primary Emotional State:** {json_data.get('interaction_engine', {}).get('metrics', {}).get('primary_emotional_state', '[NEEDS AUTHORING]')}  
**Mask Integrity:** {json_data.get('interaction_engine', {}).get('metrics', {}).get('mask_integrity', '0.7')}

**Character-Specific Rules:**
{format_dynamic_rules(dynamic_rules)}

**Stress Trigger:**
[NEEDS AUTHORING - What breaks them? How do they respond when pushed too far?]

---

## RELATIONSHIPS WITH OTHER SOULS

{format_relationships(existing_rels)}

---

## LLM SYSTEM ANCHOR

**Single Authoritative Instruction (Max 30 words):**
{llm_anchor if llm_anchor else f'You are {name}. [NEEDS AUTHORING - Complete this instruction]'}
"""
    return sheet

def format_list(items):
    if not items: return "- [NEEDS AUTHORING]\n- [NEEDS AUTHORING]\n- [NEEDS AUTHORING]"
    return "\n".join([f"- {item}" for item in items])

def format_key_items(items_dict):
    if not items_dict or all('item_' in str(k) for k in items_dict.keys()):
        return """**Item 1:** [NEEDS AUTHORING - Specific name and symbolic meaning]  
**Item 2:** [NEEDS AUTHORING - Specific name and symbolic meaning]  
**Item 3:** [NEEDS AUTHORING - Specific name and symbolic meaning]"""
    result = []
    for i, (key, value) in enumerate(items_dict.items(), 1):
        if 'item_' not in key.lower():
            result.append(f"**{key.replace('_', ' ').title()}:** {value}")
        else:
            result.append(f"**Item {i}:** {value}")
    return "\n".join(result)

def format_intimacy_tier(tier_name, tier_data, default_modifier):
    LOCATION_HELPER = "\\n".join([f"# - {loc}" for loc in KNOWN_LOCATIONS])
    if not tier_data:
        return f"""### {tier_name} ({get_score_range(tier_name)})

**Behavior Logic** (2-3 sentences):
[NEEDS AUTHORING - How do they behave at this tier?]

**Allowed Topics:**
- [NEEDS AUTHORING]
- [NEEDS AUTHORING]
- [NEEDS AUTHORING]

**Forbidden Topics:**
- [NEEDS AUTHORING]
- [NEEDS AUTHORING]

**LLM Bias:** [NEEDS AUTHORING]

**Location Access:**
- [NEEDS AUTHORING]
# Available Locations:
{LOCATION_HELPER}

**Affection Gain Modifier:** {default_modifier}"""
    
    logic = tier_data.get('logic', '[NEEDS AUTHORING]')
    allowed = tier_data.get('allowed_topics', ['[NEEDS AUTHORING]'])
    forbidden = tier_data.get('forbidden_topics', ['[NEEDS AUTHORING]'])
    bias = tier_data.get('llm_bias', '[NEEDS AUTHORING]')
    locations = tier_data.get('location_access', ['[NEEDS AUTHORING]'])
    modifier = tier_data.get('affection_gain_modifier', default_modifier)
    
    return f"""### {tier_name} ({tier_data.get('score_range', get_score_range(tier_name))})

**Behavior Logic** (2-3 sentences):
{logic}

**Allowed Topics:**
{format_list(allowed)}

**Forbidden Topics:**
{format_list(forbidden)}

**LLM Bias:** {bias}

**Location Access:**
{format_list(locations)}
# Available Locations:
{LOCATION_HELPER}

**Affection Gain Modifier:** {modifier}"""

def get_score_range(tier_name):
    return {'STRANGER': '0-35', 'TRUSTED': '36-85', 'SOUL_LINKED': '86-100'}.get(tier_name, '0-100')

def format_dynamic_rules(rules):
    if not rules or len(rules) < 3:
        return """1. If {user_name} [NEEDS AUTHORING - specific action], [consequence with +/- intimacy]
2. If {user_name} [NEEDS AUTHORING], [consequence]
3. If {user_name} [NEEDS AUTHORING], [consequence]"""
    formatted = []
    for i, rule in enumerate(rules[:5], 1):
        formatted.append(f"{i}. {rule}")
    return "\n".join(formatted)

def format_relationships(relationships):
    SOUL_HELPER = ", ".join(KNOWN_SOULS)
    if not relationships:
        return f"""[NEEDS AUTHORING - Add relationships with other souls]
# Available Souls: {SOUL_HELPER}"""
    result = []
    for rel in relationships:
        soul_id = rel.get('soul_id', '[soul_id]')
        rel_type = rel.get('type', 'neutral')
        strength = rel.get('relationship_strength', '0.5')
        effect = rel.get('interaction_effect', '[NEEDS AUTHORING]')
        location = rel.get('shared_location', '[location]')
        notes = rel.get('notes', '')
        result.append(f"""**{soul_id}:**
- Type: {rel_type}
- Strength: {strength}
- Effect: {effect}
- Shared Location: {location}
- Notes: {notes}""")
    result.append(f"# Available Souls: {SOUL_HELPER}")
    return "\n\n".join(result)

def main():
    print("Generating character sheets with AI inference...")
    old_sheets = list(OLD_SHEETS_DIR.glob("Character Sheet - *.txt"))
    for old_sheet in old_sheets:
        name = old_sheet.stem.replace("Character Sheet - ", "")
        print(f"\nProcessing: {name}")
        txt_data = parse_old_txt(old_sheet)
        json_path = OLD_JSON_DIR / f"{name.lower()}.json"
        json_data = parse_old_json(json_path)
        sheet_content = generate_character_sheet(name, txt_data, json_data)
        output_path = OUTPUT_DIR / f"{name}.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sheet_content)
        print(f"  ✓ Created: {output_path.name}")
    print(f"\n✅ Generated {len(old_sheets)} character sheets in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
