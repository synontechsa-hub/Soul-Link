#!/usr/bin/env python3
"""
Fix JSON encoding errors and update all portrait paths to .png format
"""

import json
from pathlib import Path

# Paths
SOULS_DIR = Path(r"d:\Coding\SynonTech\SoulLink_v1.5.6\_dev\data\souls")

def fix_encoding_and_portraits():
    """Fix encoding issues in JSON files and update portrait paths"""
    
    fixed_count = 0
    error_count = 0
    
    for soul_file in SOULS_DIR.glob("*.json"):
        if soul_file.name == "_template.json":
            continue
            
        try:
            # Read file with UTF-8 encoding
            with open(soul_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix common encoding issues
            content = content.replace('â€"', '—')  # Em dash
            content = content.replace('â€œ', '"')  # Left double quote
            content = content.replace('â€', '"')   # Right double quote
            content = content.replace(''', "'")   # Left single quote
            content = content.replace(''', "'")   # Right single quote
            
            # Update portrait path from .jpeg to .png
            content = content.replace('.jpeg"', '.png"')
            
            # Validate JSON
            try:
                json.loads(content)
                
                # Write back
                with open(soul_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Fixed: {soul_file.name}")
                fixed_count += 1
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON Error in {soul_file.name}: {e}")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Error processing {soul_file.name}: {e}")
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"Fixed: {fixed_count} files")
    print(f"Errors: {error_count} files")
    print(f"{'='*60}")

if __name__ == "__main__":
    fix_encoding_and_portraits()
