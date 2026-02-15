
import os
import re

# Paths
BASE_DIR = r"d:\Coding\SynonTech\SoulLink_v1.5.5\_dev"
CHAR_SHEETS_DIR = os.path.join(BASE_DIR, "character_sheets")
OUTPUT_FILE = os.path.join(BASE_DIR, "character_breakdown.txt")

def parse_key_value(text, key):
    pattern = re.compile(f"^{key}:\\s*(.+)$", re.MULTILINE | re.IGNORECASE)
    match = pattern.search(text)
    return match.group(1).strip() if match else "Unknown"

def parse_list(text, header):
    pattern = re.compile(f"^{header}\\s*=+\\s*\\n(.*?)(?=\\n=[A-Z_]+|\\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    if not match:
        return []
    items = []
    for line in match.group(1).split('\n'):
        line = line.strip()
        if line.startswith('- ') or line.startswith('* '):
            items.append(line[2:].strip())
    return items

def infer_routine(text, occupation):
    text_lower = text.lower()
    occ_lower = occupation.lower()
    
    if "student" in occ_lower or "academy" in text_lower:
        return "academic_scholar (Student)"
    if "mechanic" in occ_lower or "technician" in occ_lower:
        return "commercial_worker (Shift Work)"
    if "waitress" in occ_lower or "server" in occ_lower or "barista" in occ_lower:
        return "commercial_worker (Service)"
    if "idol" in occ_lower or "performer" in occ_lower or "dancer" in occ_lower:
        return "nightlife_performer"
    if "security" in occ_lower or "guard" in occ_lower:
        return "stoic_protector"
    if "executive" in occ_lower or "manager" in occ_lower:
        return "corporate_executive"
    if "hacker" in occ_lower or "fixer" in occ_lower:
        return "underground_fixer"
    
    return "unbound_wanderer (Default/Unknown)"

def infer_faction(text, occupation):
    text_lower = text.lower()
    occ_lower = occupation.lower()
    
    if "stop n go" in text_lower or "racer" in occ_lower:
        return "racers"
    if "academy" in text_lower or "student" in occ_lower:
        return "academy_students"
    if "apex" in text_lower or "executive" in occ_lower:
        return "corporate_elite"
    if "circuit" in text_lower or "underground" in text_lower:
        return "underground"
    if "glitch" in text_lower or "pixel" in text_lower or "ai" in occ_lower:
        return "digital_natives"
    if "garden" in text_lower or "artist" in occ_lower:
        return "creatives"
    if "healer" in occ_lower or "archive" in text_lower:
        return "caretakers"
        
    return "Unknown/Citizen"

def analyze_file(filename):
    filepath = os.path.join(CHAR_SHEETS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    name = parse_key_value(content, "NAME")
    age = parse_key_value(content, "AGE")
    archetype = parse_key_value(content, "ARCHETYPE")
    
    # Try to find Occupation in Bio or Summary if not explicit key
    # Simple search for "is a [Occupatoin]" pattern or similar? 
    # Actually, let's just use the text for inference.
    occupation = "Unknown" # Placeholder, we infer deeper
    
    routine = infer_routine(content, archetype)
    faction = infer_faction(content, archetype)
    
    # Extract locations mentioned in access list
    locations = []
    loc_section = re.search(r"location_access:\s*\n((?:\s*-\s*[a-z0-9_]+\s*\n)+)", content)
    if loc_section:
        for line in loc_section.group(1).split('\n'):
            if line.strip().startswith('-'):
                locations.append(line.strip()[2:])
    
    return f"""
--------------------------------------------------
SOUL: {name} ({age})
FILE: {filename}
--------------------------------------------------
ARCHETYPE: {archetype}
FACTION:   {faction}
ROUTINE:   {routine}
LOCATIONS: {', '.join(locations[:5])}{'...' if len(locations) > 5 else ''}
SUMMARY:   {parse_section(content, "SUMMARY")[:200].replace(chr(10), ' ')}...
"""

def parse_section(text, header):
    pattern = re.compile(f"^{header}:?\\s*\\n(.*?)(?=\\n[A-Z_]+:|\\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""

# Main execution
files = sorted([f for f in os.listdir(CHAR_SHEETS_DIR) if f.endswith(".txt")])
output_content = f"CHARACTER BREAKDOWN REPORT\nGenerated for Manual Migration\nTotal Souls: {len(files)}\n"

for count, file in enumerate(files, 1):
    try:
        output_content += analyze_file(file)
    except Exception as e:
        output_content += f"\nError processing {file}: {e}\n"

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(output_content)

print(f"Generated {OUTPUT_FILE} with {len(files)} entries.")
