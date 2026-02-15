import re
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlmodel import select, SQLModel

# This script must be run with the project root in sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
DEV_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = DEV_DIR.parent
sys.path.append(str(PROJECT_ROOT))

# Import models
from backend.app.models import Soul, SoulPillar, SoulState

# Database Connection
DB_PATH = PROJECT_ROOT / "backend/soul_link.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL)

SHEETS_DIR = DEV_DIR / "character_sheets"
DNA_DIR = DEV_DIR / "blueprints/souls/dna"
os.makedirs(DNA_DIR, exist_ok=True)

def extract_section(content, header_regex):
    """Extract content between two headers."""
    match = re.search(rf'{header_regex}(.*?)(?=\n##|\Z)', content, re.DOTALL)
    return match.group(1).strip() if match else ""

def parse_list(content):
    """Parse a markdown list into a Python list."""
    return [line.strip("- ").strip() for line in content.split("\n") if line.strip().startswith("-")]

def parse_key_value(content, key):
    """Extract a value from a **Key:** Value or - Key: Value line."""
    match = re.search(rf'[\*-]\s*{key}:\s*(.*)', content, re.IGNORECASE)
    return match.group(1).strip() if match else ""

def parse_sheet_deep(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # SECTION: Meta Information
    meta_section = extract_section(content, r'---') # First block
    soul_id = parse_key_value(meta_section, "Soul ID")
    author = parse_key_value(meta_section, "Author")
    author_uuid = parse_key_value(meta_section, "Author UUID") or "14dd612d-744e-487d-b2d5-cc47732183d3"
    status = parse_key_value(meta_section, "Completion Status")
    updated = parse_key_value(meta_section, "Last Updated")

    # SECTION: CORE IDENTITY
    core_section = extract_section(content, r'## CORE IDENTITY')
    name = parse_key_value(core_section, "Name")
    age = parse_key_value(core_section, "Age")
    gender = parse_key_value(core_section, "Gender")
    archetype = parse_key_value(core_section, "Archetype")
    content_rating = parse_key_value(core_section, "Content Rating")
    
    summary = ""
    summary_match = re.search(r'\*\*Summary\*\*.*?\n(.*?)(?=\n\n|\n\*\*|\Z)', core_section, re.DOTALL)
    if summary_match: summary = summary_match.group(1).strip()
    
    bio = ""
    bio_match = re.search(r'\*\*Bio\*\*.*?\n(.*?)(?=\n\n|\n\*\*|\Z)', core_section, re.DOTALL)
    if bio_match: bio = bio_match.group(1).strip()

    # SECTION: APPEARANCE & AESTHETIC
    appearance_section = extract_section(content, r'## APPEARANCE & AESTHETIC')
    phys_desc = parse_key_value(appearance_section, "Physical Description") # Sometimes it's a block
    if not phys_desc:
        phys_match = re.search(r'\*\*Physical Description\*\*.*?\n(.*?)(?=\n\n|\n\*\*|\Z)', appearance_section, re.DOTALL)
        if phys_match: phys_desc = phys_match.group(1).strip()
    
    voice_style = parse_key_value(appearance_section, "Voice & Speech Style")
    sig_emote = parse_key_value(appearance_section, "Signature Emote")
    never_list = parse_list(extract_section(appearance_section, r'\*\*Things They Would NEVER Do/Say:\*\*'))

    # SECTION: PERSONALITY DEEP DIVE
    pers_section = extract_section(content, r'## PERSONALITY DEEP DIVE')
    traits_sub = extract_section(pers_section, r'### Traits')
    primary_traits = parse_list(extract_section(traits_sub, r'\*\*Primary.*?\*\*'))
    hidden_traits = parse_list(extract_section(traits_sub, r'\*\*Hidden.*?\*\*'))
    flaws = parse_list(extract_section(traits_sub, r'\*\*Flaws.*?\*\*'))
    
    items_sub = extract_section(pers_section, r'### Key Items')
    key_items = {}
    item_matches = re.finditer(r'\*\*(.*?)\*\*:\s*(.*)', items_sub)
    for i, m in enumerate(item_matches):
        key = f"item_{['one', 'two', 'three', 'four'][i] if i < 4 else i}"
        key_items[key] = f"{m.group(1).strip()}: {m.group(2).strip()}"

    # SECTION: WORLD INTEGRATION
    world_section = extract_section(content, r'## WORLD INTEGRATION')
    start_loc = parse_key_value(world_section, "Starting Location")
    home_loc = parse_key_value(world_section, "Home Location")
    
    routines = {}
    routine_lines = re.findall(r'- (Morning|Afternoon|Evening|Night|Home Time) \(.*?\):\s*(\w+)', world_section)
    for slot, loc in routine_lines:
        routines[slot.lower().replace(" ", "_")] = loc

    emp_sub = extract_section(content, r'\*\*Employment:\*\*')
    emp_data = {}
    if "Employed: Yes" in emp_sub:
        emp_data = {
            "location_id": parse_key_value(emp_sub, "Location"),
            "role_id": parse_key_value(emp_sub, "Role"),
            "shift_slots": [s.strip().lower() for s in parse_key_value(emp_sub, "Shift Times").split("|")],
            "salary_per_shift": parse_key_value(emp_sub, "Salary per Shift")
        }

    # SECTION: CAPABILITIES & CONSENT
    cap_section = extract_section(content, r'## CAPABILITIES & CONSENT')
    caps = {
        "romance": parse_key_value(cap_section, "Romance").lower() == "true",
        "sexual_content": parse_key_value(cap_section, "Sexual Content").lower() == "true",
        "explicit_language": parse_key_value(cap_section, "Explicit Language").lower() == "true",
        "emotional_dependency": parse_key_value(cap_section, "Emotional Dependency").lower() == "true"
    }
    
    consent_notes = ""
    notes_match = re.search(r'\*Character-Specific Consent Notes\*.*?\n(.*?)(?=\n\n|\n---|\Z)', cap_section, re.DOTALL)
    if notes_match: consent_notes = notes_match.group(1).strip()

    can_init = {
        "emotional_support": parse_key_value(cap_section, "Emotional Support").lower() == "true",
        "protective_gestures": parse_key_value(cap_section, "Protective Gestures").lower() == "true",
        "physical_touch": parse_key_value(cap_section, "Physical Touch").lower() == "true"
    }

    # SECTION: INTIMACY PROGRESSION
    intimacy_section = extract_section(content, r'## INTIMACY PROGRESSION')
    tiers = {}
    for tier in ["STRANGER", "TRUSTED", "SOUL_LINKED"]:
        tier_sub = extract_section(intimacy_section, rf'### {tier}')
        if tier_sub:
            tiers[tier] = {
                "score_range": re.search(r'\((\d+-\d+)\)', content.split(f"### {tier}")[0].split("\n")[-1]) or "0-0", # Hacky range
                "logic": "",
                "allowed_topics": parse_list(extract_section(tier_sub, r'\*\*Allowed Topics:\*\*')),
                "forbidden_topics": parse_list(extract_section(tier_sub, r'\*\*Forbidden Topics:\*\*')),
                "llm_bias": parse_key_value(tier_sub, "LLM Bias"),
                "location_access": parse_list(extract_section(tier_sub, r'\*\*Location Access:\*\*')),
                "affection_gain_modifier": float(parse_key_value(tier_sub, "Affection Gain Modifier") or 1.0)
            }
            # Score range fix
            range_match = re.search(rf'{tier}\s*\((\d+-\d+)\)', content)
            if range_match: tiers[tier]["score_range"] = range_match.group(1)
            
            logic_match = re.search(r'\*\*Behavior Logic\*\*.*?\n(.*?)(?=\n\n|\n\*\*|\Z)', tier_sub, re.DOTALL)
            if logic_match: tiers[tier]["logic"] = logic_match.group(1).strip()

    # SECTION: DYNAMIC INTERACTION RULES
    rules_section = extract_section(content, r'## DYNAMIC INTERACTION RULES')
    primary_state = parse_key_value(rules_section, "Primary Emotional State")
    mask_integrity = float(parse_key_value(rules_section, "Mask Integrity") or 0.5)
    
    dyn_rules = []
    rules_list = re.findall(r'\d+\.\s*(.*)', rules_section)
    for r in rules_list: dyn_rules.append(r.strip())

    # SECTION: RELATIONSHIPS
    rel_section = extract_section(content, r'## RELATIONSHIPS WITH OTHER SOULS')
    relationships = []
    # Find all soul blocks like **talia_01:**
    soul_blocks = re.finditer(r'\*\*(.*?)_01\*\*:\s*\n(.*?)(?=\n\n\*\*|\Z)', rel_section, re.DOTALL)
    for m in soul_blocks:
        s_id = f"{m.group(1).strip().lower()}_01"
        block = m.group(2)
        relationships.append({
            "soul_id": s_id,
            "type": parse_key_value(block, "Type"),
            "relationship_strength": float(parse_key_value(block, "Strength") or 0.5),
            "interaction_effect": parse_key_value(block, "Effect"),
            "shared_location": parse_key_value(block, "Shared Location"),
            "notes": parse_key_value(block, "Notes")
        })

    # SECTION: LLM ANCHOR
    anchor = extract_section(content, r'## LLM SYSTEM ANCHOR').split("\n")[-1].strip()

    # CONSTRUCT FINAL JSON
    dna = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"dna_{soul_id}",
        "soul_id": soul_id,
        "dev_config": {
            "author_id": author_uuid,
            "author_username": author,
            "completion_status": status,
            "last_updated": updated
        },
        "meta": {
            "name": name,
            "version": "1.5.5",
            "age": int(re.search(r'\d+', age).group(0)) if re.search(r'\d+', age) else 0,
            "gender": gender,
            "archetype": archetype,
            "summary": summary,
            "content_rating": content_rating,
            "portrait_full": f"/assets/images/souls/{soul_id}.jpeg",
            "portrait_thumb": f"/assets/images/souls/{soul_id}_thumb.jpeg",
            "starting_location": start_loc,
            "home_location": home_loc,
            "routines": routines,
            "capabilities": caps,
            "consent_model": {
                "explicit_consent_required_for": parse_list(extract_section(cap_section, r'\*Explicit Consent Required For:\*')),
                "can_initiate": can_init,
                "notes": consent_notes
            }
        },
        "identity_pillar": {
            "bio": bio,
            "traits": {
                "primary": primary_traits,
                "hidden": hidden_traits,
                "flaws": flaws
            },
            "key_items": key_items
        },
        "aesthetic_pillar": {
            "description": phys_desc,
            "voice_style": voice_style,
            "sensory_forbidden": never_list,
            "signature_emote": sig_emote
        },
        "interaction_pillar": {
            "metrics": {
                "primary_emotional_state": primary_state,
                "mask_integrity": mask_integrity
            },
            "intimacy_tiers": tiers,
            "dynamic_rules": dyn_rules
        },
        "world_presence": {
            "employment": emp_data,
            "relationships_with_souls": relationships
        },
        "llm_system_anchor": anchor
    }

    return dna

def seed_souls():
    print("🚀 Starting Advanced Soul DNA Seed (v1.5.5)...")
    print(f"📂 DNA Output Directory: {DNA_DIR}")
    
    with Session(engine) as session:
        for file_path in sorted(SHEETS_DIR.glob("*.txt")):
            if file_path.stem == "_TEMPLATE": continue
            
            print(f"  🧬 Deep Parsing {file_path.name}...")
            try:
                dna = parse_sheet_deep(file_path)
            except Exception as e:
                print(f"  ❌ Error parsing {file_path.name}: {e}")
                continue
            
            soul_id = dna['soul_id']
            if not soul_id:
                print(f"  ⚠️ Skip {file_path.name}: No Soul ID found.")
                continue

            # ... (DB injection logic) ...
            
            # 4. EXPORT DNA JSON
            dna_path = DNA_DIR / f"{soul_id}.json"
            with open(dna_path, 'w', encoding='utf-8') as f:
                json.dump(dna, f, indent=4)
            print(f"    ✅ Exported DNA: {dna_path.name}")

            # 1. UPSERT SOUL
            soul = session.get(Soul, soul_id)
            if not soul:
                soul = Soul(soul_id=soul_id)
            
            soul.name = dna['meta']['name']
            soul.summary = dna['meta']['summary']
            soul.archetype = dna['meta']['archetype']
            soul.version = dna['meta']['version']
            soul.portrait_url = dna['meta']['portrait_full']
            session.add(soul)

            # 2. UPSERT SOUL PILLAR
            pillar = session.get(SoulPillar, soul_id)
            if not pillar:
                pillar = SoulPillar(soul_id=soul_id)
            
            pillar.routines = dna['meta']['routines']
            pillar.personality = dna['identity_pillar']['bio']
            pillar.background = dna['meta']['summary']
            
            pillar.identity_pillar = dna['identity_pillar']
            pillar.aesthetic_pillar = dna['aesthetic_pillar']
            pillar.interaction_engine = dna['interaction_pillar']
            pillar.meta_data = dna['dev_config']
            pillar.llm_instruction_override = {"anchor": dna['llm_system_anchor']}
            session.add(pillar)

            # 3. UPSERT SOUL STATE
            state = session.get(SoulState, soul_id)
            if not state:
                state = SoulState(soul_id=soul_id)
            
            state.current_location_id = dna['meta']['starting_location']
            state.energy = 100
            state.mood = dna['interaction_pillar']['metrics']['primary_emotional_state']
            session.add(state)
            
            # 4. EXPORT DNA JSON
            dna_path = DNA_DIR / f"{soul_id}.json"
            with open(dna_path, 'w', encoding='utf-8') as f:
                json.dump(dna, f, indent=4)

        session.commit()
    print("✨ Advanced Soul DNA Seed Complete!")

if __name__ == "__main__":
    seed_souls()
