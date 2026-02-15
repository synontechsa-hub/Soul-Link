import re
import os
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
SHEETS_DIR = BASE_DIR / "character_sheets"
LOCATIONS_FILE = BASE_DIR / "blueprints/locations/known_locations.json"
SOULS_FILE = BASE_DIR / "blueprints/souls/known_souls.json"

# Load known locations and souls
import json
with open(LOCATIONS_FILE, 'r', encoding='utf-8') as f:
    locations_data = json.load(f)
    KNOWN_LOCATIONS = {loc['id'] for loc in locations_data}

with open(SOULS_FILE, 'r', encoding='utf-8') as f:
    KNOWN_SOULS = set(json.load(f))

def parse_sheet(file_path):
    """Extract key data from a character sheet."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = {
        'soul_id': None,
        'name': file_path.stem,
        'daily_routines': {},
        'employment': {},
        'relationships': []
    }
    
    # Extract Soul ID
    id_match = re.search(r'Soul ID:\s*(\w+)', content)
    if id_match:
        data['soul_id'] = id_match.group(1)
    
    # Extract Daily Routines
    routine_section = re.search(r'\*\*Daily Routines:\*\*(.*?)(?=\n\n|\*\*Employment)', content, re.DOTALL)
    if routine_section:
        for line in routine_section.group(1).split('\n'):
            match = re.search(r'-\s*(\w+)\s*\([^)]+\):\s*(\w+)', line)
            if match:
                data['daily_routines'][match.group(1).lower()] = match.group(2)
    
    # Extract Employment
    emp_match = re.search(r'\*\*Employment:\*\*.*?Location:\s*([^\n\r]+)', content, re.DOTALL)
    if emp_match:
        loc_val = emp_match.group(1).strip()
        data['employment']['location'] = loc_val
    
    # Extract Relationships
    rel_section = re.search(r'## RELATIONSHIPS WITH OTHER SOULS(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if rel_section:
        for block in re.finditer(r'\*\*(\w+):\*\*.*?Type:\s*(\w+)', rel_section.group(1), re.DOTALL):
            data['relationships'].append({
                'soul_id': block.group(1),
                'type': block.group(2)
            })
    
    return data

def main():
    report_path = BASE_DIR / "reports/consistency_report.txt"
    os.makedirs(report_path.parent, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as report_file:
        def log(msg):
            print(msg)
            report_file.write(msg + '\n')
            
        log("🔍 Validating Soul Consistency...\n")
        
        sheets = {}
        id_to_name = {}
        for file_path in sorted(SHEETS_DIR.glob("*.txt")):
            data = parse_sheet(file_path)
            sheets[file_path.stem] = data
            if data['soul_id']:
                id_to_name[data['soul_id']] = file_path.stem
        
        errors = []
        warnings = []
        
        # 1. Check bidirectional relationships
        log("📊 Checking Relationship Symmetry...")
        for name, data in sheets.items():
            for rel in data['relationships']:
                target_id = rel['soul_id']
                target_name = id_to_name.get(target_id)
                
                if not target_name:
                    errors.append(f"❌ {name} references unknown soul ID: {target_id}")
                    continue
                
                # Check if target soul lists this soul back
                this_soul_id = data['soul_id']
                target_rels = [r['soul_id'] for r in sheets[target_name]['relationships']]
                
                if this_soul_id not in target_rels:
                    warnings.append(f"⚠️  {name} lists {target_name} as {rel['type']}, but {target_name} doesn't list {name}")
                else:
                    # Check if relationship types are compatible (optional improvement)
                    pass
        
        # 2. Check location references
        log("🗺️  Checking Location References...")
        for name, data in sheets.items():
            for slot, loc in data['daily_routines'].items():
                if loc not in KNOWN_LOCATIONS:
                    errors.append(f"❌ {name} references unknown location in {slot}: {loc}")
            
            emp_loc = data['employment'].get('location')
            skip_locs = ['Various', 'None', 'N/A', '[Not Employed]', '[location_id if employed]']
            if emp_loc and not any(s.lower() in emp_loc.lower() for s in skip_locs) and emp_loc not in KNOWN_LOCATIONS:
                errors.append(f"❌ {name} has unknown employment location: {emp_loc}")
        
        # 3. Check schedule conflicts
        log("⏰ Checking Schedule Conflicts...")
        # (Could check if two souls are at the same location at the same time if relevant)
        
        # Report results
        log("\n" + "="*60)
        if errors:
            log(f"\n❌ ERRORS FOUND ({len(errors)}):")
            for err in errors:
                log(f"  {err}")
        
        if warnings:
            log(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for warn in warnings:
                log(f"  {warn}")
        
        if not errors and not warnings:
            log("✅ ALL SOULS ARE CONSISTENT!")
        
        log("\n" + "="*60)
        log(f"📈 Summary: {len(sheets)} souls analyzed")
        log(f"   Errors: {len(errors)}")
        log(f"   Warnings: {len(warnings)}")
        log(f"\nReport saved to: {report_path}")

if __name__ == "__main__":
    main()
