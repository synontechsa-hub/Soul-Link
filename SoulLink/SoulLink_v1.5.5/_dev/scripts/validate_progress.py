"""
Script to validat character sheet authoring progress.
Scans all .txt files in character_sheets/ and reports completion status.
"""

import sys
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
SHEETS_DIR = BASE_DIR / "character_sheets"

def main():
    print(f"🔍 Scanning Character Sheets in {SHEETS_DIR}...\n")
    
    files = sorted(list(SHEETS_DIR.glob("*.txt")))
    total = len(files)
    complete = 0
    incomplete = []
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        remaining_placeholders = content.count("[NEEDS AUTHORING]") + content.count("[NEEDS LOCATION]")
        
        if remaining_placeholders == 0:
            complete += 1
            # Optional: Print success for completed ones (commented out to reduce noise)
            # print(f"  ✅ {file_path.stem} - COMPLETE")
        else:
            incomplete.append(f"{file_path.stem} ({remaining_placeholders} missing fields)")
    
    # Progress Bar
    percent = int((complete / total) * 100)
    bar_length = 20
    filled_length = int(bar_length * complete // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    print(f"📊 Progress: [{bar}] {percent}% ({complete}/{total})")
    print(f"\n🎉 Completed Souls: {complete}")
    
    if incomplete:
        print(f"\n📝 Needs Work ({len(incomplete)}):")
        for item in incomplete:
            print(f"  ❌ {item}")
    else:
        print("\n✨ ALL SOULS COMPLETED! Ready for JSON conversion! ✨")

if __name__ == "__main__":
    main()
