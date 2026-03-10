import re
import os
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
SHEETS_DIR = BASE_DIR / "character_sheets"

def parse_relationships(content):
    rels = []
    rel_section = re.search(r'## RELATIONSHIPS WITH OTHER SOULS(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if rel_section:
        # Match blocks: **soul_id**: \n - Type: type ...
        for block in re.finditer(r'\*\*(\w+):\*\*.*?Type:\s*(\w+)(.*?)(?=\n\n\*\*|\Z)', rel_section.group(1), re.DOTALL):
            rels.append({
                'id': block.group(1),
                'type': block.group(2).lower(),
                'full_block': block.group(0)
            })
    return rels

def main():
    print("🔄 Synchronizing Soul Relationships...")
    
    sheets = {}
    id_to_file = {}
    for file_path in SHEETS_DIR.glob("*.txt"):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        id_match = re.search(r'Soul ID:\s*(\w+)', content)
        if id_match:
            soul_id = id_match.group(1)
            sheets[soul_id] = content
            id_to_file[soul_id] = file_path

    # Identify missing back-links
    synchronizations_needed = defaultdict(list)
    
    for soul_id, content in sheets.items():
        rels = parse_relationships(content)
        for rel in rels:
            target_id = rel['id']
            if target_id in sheets:
                target_rels = [r['id'] for r in parse_relationships(sheets[target_id])]
                if soul_id not in target_rels:
                    # Target doesn't mention Source.
                    # We need to add Source to Target.
                    rel_type = rel['type']
                    # Map back-link types
                    back_type = rel_type
                    if rel_type == 'rival': back_type = 'rival'
                    elif rel_type == 'friend': back_type = 'friend'
                    else: back_type = 'acquaintance'
                    
                    synchronizations_needed[target_id].append({
                        'from_id': soul_id,
                        'type': back_type
                    })

    # Apply synchronizations
    count = 0
    for target_id, news in synchronizations_needed.items():
        file_path = id_to_file[target_id]
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        rel_header = "## RELATIONSHIPS WITH OTHER SOULS"
        for new_rel in news:
            from_name = new_rel['from_id'].split('_')[0].capitalize()
            new_block = f"\n\n**{new_rel['from_id']}:**\n- Type: {new_rel['type']}\n- Strength: 0.5\n- Effect: Mutual interaction\n- Shared Location: Various\n- Notes: (Auto-synchronized relationship with {from_name}.)"
            
            # Find insertion point
            if rel_header in content:
                # Add to the end of the section
                parts = re.split(rf'({rel_header})', content)
                # content is parts[0] + parts[1] + parts[2]
                # parts[2] might have next header
                next_header = re.search(r'\n## ', parts[2])
                if next_header:
                    idx = next_header.start()
                    parts[2] = parts[2][:idx] + new_block + parts[2][idx:]
                else:
                    parts[2] = parts[2] + new_block
                
                content = "".join(parts)
                count += 1
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    print(f"✅ Successfully added {count} missing relationship back-links.")

if __name__ == "__main__":
    main()
