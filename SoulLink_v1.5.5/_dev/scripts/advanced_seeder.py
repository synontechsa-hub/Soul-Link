import re
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# DYNAMIC PATHS
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.resolve().parent.parent
DEV_DIR = PROJECT_ROOT / "_dev"
sys.path.append(str(PROJECT_ROOT))

SHEETS_DIR = DEV_DIR / "character_sheets"

# LOAD GLOBAL CONFIGS
def load_global_configs():
    with open(DEV_DIR / "blueprints/data/system/global_config.json", 'r') as f:
        sys_config = json.load(f)
    with open(DEV_DIR / "blueprints/data/intimacy/config.json", 'r') as f:
        int_config = json.load(f)
    with open(DEV_DIR / "blueprints/data/system/archetypes.json", 'r') as f:
        arch_config = json.load(f)
    with open(DEV_DIR / "blueprints/data/system/traits.json", 'r') as f:
        traits_config = json.load(f)
    with open(DEV_DIR / "blueprints/data/system/routines.json", 'r') as f:
        rout_config = json.load(f)
    return sys_config, int_config, arch_config, traits_config, rout_config

SYS_GLOBAL, INT_GLOBAL, ARCH_GLOBAL, TRAITS_GLOBAL, ROUT_GLOBAL = load_global_configs()

def get_sections(content):
    """Split content into sections based on headers (#, ##, ###, ====)."""
    sections = {}
    current_section = "HEADER"
    lines = content.split('\n')
    current_body = []
    
    for line in lines:
        header_match = re.match(r'^#+\s*(.*?)$', line) or \
                       re.match(r'^={4,}\s*(.*?)\s*={4,}$', line) or \
                       re.match(r'^---$', line)
        if header_match:
            sections[current_section] = '\n'.join(current_body).strip()
            title = header_match.group(1).strip().upper() if header_match.groups() and header_match.group(1) else ""
            if title:
                slug = re.sub(r'[^A-Z0-9_]', '_', title).strip('_')
                current_section = f"SEC_{slug}"
            else:
                current_section = f"DIVIDER_{len(sections)}"
            current_body = []
        else:
            current_body.append(line)
    
    sections[current_section] = '\n'.join(current_body).strip()
    return sections

def parse_list(content):
    if not content: return []
    results = []
    for line in content.split("\n"):
        line = line.strip()
        if re.match(r'^\s*[-*]|\d+\.', line):
            cleaned = re.sub(r'^\s*[-*]\s*|\s*\d+\.\s*', '', line).strip()
            if cleaned: results.append(cleaned)
    return results

def parse_key_value(content, key):
    if not content: return ""
    key_pattern = key.replace("_", "[ _]")
    pattern = rf'^\s*-?\s*{key_pattern}\s*[:=]\s*(.*?)\s*$'
    match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
    return match.group(1).strip() if match else ""

def parse_number(text, default=0.0):
    if not text: return default
    match = re.search(r'(\d+\.?\d*)', str(text))
    return float(match.group(1)) if match else default

def get_trait_definitions(trait_list, category):
    defs = {}
    for trait in trait_list:
        slug = re.sub(r'[^a-z0-9_]', '_', trait.lower()).strip('_')
        definition = TRAITS_GLOBAL['traits'].get(category, {}).get(slug, trait)
        defs[trait] = definition
    return defs

def find_archetype_data(archetype_text):
    text = re.sub(r'[^a-z0-9_]', '_', archetype_text.lower())
    for arch_id, data in ARCH_GLOBAL['archetypes'].items():
        if arch_id in text or re.sub(r'[^a-z0-9_]', '_', data['name'].lower()) in text:
            return data
    return {}

def parse_sheet_deep(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = get_sections(content)
    full_text = content[:2000] # Increased for more meta
    
    soul_id = parse_key_value(full_text, "Soul ID") or parse_key_value(full_text, "SOUL_ID")
    if not soul_id:
        raise ValueError(f"Missing SOUL_ID in {file_path.name}")

    author_user = parse_key_value(full_text, "Author")
    author_id = parse_key_value(full_text, "Author UUID") or "14dd612d-744e-487d-b2d5-cc47732183d3"
    
    meta_sec = sections.get("SEC_CORE_IDENTITY", "")
    name = parse_key_value(meta_sec, "Name") or soul_id.split('_')[0].title()
    age = int(parse_number(parse_key_value(meta_sec, "Age") or "25"))
    gender = parse_key_value(meta_sec, "Gender")
    
    arch_val = parse_key_value(meta_sec, "Archetype")
    arch_data = find_archetype_data(arch_val)
    
    # Improved Trait Extraction (handles both Markdown and Plain)
    ident_sec = sections.get("SEC_PERSONALITY_DEEP_DIVE", "")
    def extract_trait_list(category_pattern):
        match = re.search(rf'{category_pattern}.*?\n(.*?)(?=\n\n|\n\*\*|\n---|\Z)', ident_sec, re.DOTALL | re.IGNORECASE)
        return parse_list(match.group(1)) if match else []

    p_traits = extract_trait_list(r'\*\*Primary') or extract_trait_list(r'Primary')
    h_traits = extract_trait_list(r'\*\*Hidden') or extract_trait_list(r'Hidden')
    f_traits = extract_trait_list(r'\*\*Flaws') or extract_trait_list(r'Flaws')
    
    # Intimacy Tiers
    tiers = {}
    for tier_glob in INT_GLOBAL['tiers']:
        tid = tier_glob['id'].upper()
        tier_body = ""
        for sname, sbody in sections.items():
            if tid in sname:
                tier_body = sbody
                break
        if tier_body:
            logic_match = re.search(r'\*\*Behavior Logic\*\*.*?\n(.*?)(?=\n\n|\n---|\Z)', tier_body, re.DOTALL | re.IGNORECASE)
            tiers[tier_glob['id']] = {
                "display_name": tier_glob['display_name'],
                "score_range": f"{tier_glob['score_range'][0]}-{tier_glob['score_range'][1]}",
                "logic": logic_match.group(1).strip() if logic_match else "",
                "llm_bias": parse_key_value(tier_body, "LLM Bias"),
                "affection_gain_modifier": parse_number(parse_key_value(tier_body, "Affection Gain Modifier"), tier_glob['default_affection_mod'])
            }

    # Construct DNA
    dna = {
        "soul_id": soul_id,
        "dev_config": {
            "architect_ids": [a['id'] for a in SYS_GLOBAL['architects']],
            "author_username": author_user,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        },
        "meta": {
            "name": name, "age": age, "gender": gender, "archetype": arch_data.get('id', arch_val),
            "summary": parse_key_value(meta_sec, "Summary") or "",
            "portrait_full": f"/portraits/{soul_id}_full.jpeg"
        },
        "identity_pillar": {
            "bio": parse_key_value(meta_sec, "Bio") or "",
            "traits": { "primary": get_trait_definitions(p_traits, "primary"), "hidden": get_trait_definitions(h_traits, "hidden"), "flaws": get_trait_definitions(f_traits, "flaws") }
        },
        "aesthetic_pillar": { 
            "description": parse_key_value(sections.get("SEC_APPEARANCE___AESTHETIC", ""), "Description") or "", 
            "voice_style": parse_key_value(sections.get("SEC_APPEARANCE___AESTHETIC", ""), "Voice & Speech Style") or arch_data.get('voice_guidance', ""),
            "signature_emote": parse_key_value(sections.get("SEC_APPEARANCE___AESTHETIC", ""), "Signature Emote")
        },
        "interaction_pillar": { "intimacy_tiers": tiers },
        "llm_system_anchor": f"You are {name}. Template v1.5.5. Instruction: {arch_data.get('base_instruction', '')}"
    }
    return dna

def main():
    print("[DEBUG] DEEP SOUL DNA COMPILER (v1.5.5-Modular)")
    REFINED_DNA_DIR = DEV_DIR / "blueprints/data/souls_refined"
    os.makedirs(REFINED_DNA_DIR, exist_ok=True)
    
    all_files = [f for f in os.listdir(SHEETS_DIR) if f.endswith(".txt") and f != "_TEMPLATE.txt"]
    print(f"[DEBUG] Processing {len(all_files)} files in {SHEETS_DIR}")
    
    processed = 0
    for filename in sorted(all_files):
        try:
            dna = parse_sheet_deep(SHEETS_DIR / filename)
            with open(REFINED_DNA_DIR / f"{dna['soul_id']}.json", 'w', encoding='utf-8') as f:
                json.dump(dna, f, indent=4)
            print(f"    [OK] -> {dna['soul_id']}.json")
            processed += 1
        except Exception as e:
            print(f"  [FAIL] {filename} -> {e}")

    print(f"\n[DONE] COMPILATION COMPLETE. SUCCESS: {processed}/{len(all_files)}")

if __name__ == "__main__":
    main()
