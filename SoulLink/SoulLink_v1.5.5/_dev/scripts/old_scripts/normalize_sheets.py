import os
import re
from pathlib import Path

# Absolute paths
PROJECT_ROOT = Path(r"d:\Coding\SynonTech\SoulLink_v1.5.5")
DEV_DIR = PROJECT_ROOT / "_dev"
SHEETS_DIR = DEV_DIR / "character_sheets"

def clean_content(content):
    # 1. Remove **Bold** from Keys: "**Name:**" or "**Name: **" -> "Name:"
    # This handles spaces inside/outside the asterisks
    content = re.sub(r'\*\*\s*([\w\s&]+):\s*\*\*', r'\1:', content)
    
    # 2. Fix the Meta section header if it exists
    content = content.replace("**Meta Information**", "Meta Information")
    
    # 3. Handle double-colons or missing spaces
    content = re.sub(r'(\w+):\s*:\s*', r'\1: ', content) # Fix "Key: : Value"
    content = re.sub(r'(\w+):(\S)', r'\1: \2', content) # Fix "Key:Value"
    
    # 4. Remove remaining stray asterisks from headers
    content = re.sub(r'^##\s*\*\*(.*?)\*\*', r'## \1', content, flags=re.MULTILINE)
    content = re.sub(r'^###\s*\*\*(.*?)\*\*', r'### \1', content, flags=re.MULTILINE)
    
    # 4. Normalize list markers from "* Item" to "- Item" for consistency
    # But only at the start of a line
    content = re.sub(r'^\* ', r'- ', content, flags=re.MULTILINE)
    
    return content

def main():
    print("🧹 Normalizing Character Sheets...")
    count = 0
    for file_path in SHEETS_DIR.glob("*.txt"):
        if file_path.stem == "_TEMPLATE": continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()
            
        cleaned = clean_content(original)
        
        if cleaned != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            print(f"  ✨ Cleaned: {file_path.name}")
            count += 1
        else:
            print(f"  ✅ Already Clean: {file_path.name}")
            
    print(f"\n✅ Finished. Normalized {count} files.")

if __name__ == "__main__":
    main()
