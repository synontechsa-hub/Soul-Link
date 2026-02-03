# _dev/scripts/garbage_service.py
# version.py

import os
import shutil
from pathlib import Path

# --- CONFIGURATION ---
# Frontend "Nuclear" Targets
FRONTEND_GARBAGE_FOLDERS = [
    "android", "ios", "windows", "linux", "macos", "web", 
    ".dart_tool", ".idea", ".vscode", "build"
]
FRONTEND_GARBAGE_FILES = [
    "pubspec.lock", ".metadata", "analysis_options.yaml", "README.md"
]

def clean_soul_link():
    # Path Resolution (Script is in _dev/scripts/)
    script_dir = Path(__file__).parent
    root_dir = (script_dir / ".." / "..").resolve()
    frontend_dir = root_dir / "frontend"
    backend_dir = root_dir / "backend"

    print(f"🔱 SoulLink Engine Maintenance: {root_dir.name}")
    print("=" * 50)

    # --- 1. FRONTEND CLEAN (The Reconstruction Prep) ---
    if frontend_dir.exists():
        print(f"🧹 Cleaning Frontend: {frontend_dir.relative_to(root_dir)}")
        for folder in FRONTEND_GARBAGE_FOLDERS:
            target = frontend_dir / folder
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)
                print(f"   [DELETED] Folder: {folder}/")
        
        for file_path in frontend_dir.glob("*"):
            if file_path.name in FRONTEND_GARBAGE_FILES or file_path.suffix == ".iml":
                file_path.unlink(missing_ok=True)
                print(f"   [DELETED] File:   {file_path.name}")
    
    # --- 2. BACKEND CLEAN (The Bytecode Exorcism) ---
    if backend_dir.exists():
        print(f"\n🐍 Cleaning Backend: {backend_dir.relative_to(root_dir)}")
        pycache_count = 0
        for p in backend_dir.rglob("__pycache__"):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
                pycache_count += 1
        
        pyc_count = 0
        for f in backend_dir.rglob("*.py[co]"):
            f.unlink(missing_ok=True)
            pyc_count += 1
            
        print(f"   [DELETED] {pycache_count} __pycache__ directories found.")
        print(f"   [DELETED] {pyc_count} compiled .pyc/.pyo files.")

    print("=" * 50)
    print("✨ SoulLink is clinical-levels of clean.")
    print("🚀 Next: 'flutter create --org com.synontech --project-name soul_link .'")

if __name__ == "__main__":
    confirm = input("Nuke frontend junk and backend bytecode? (y/n): ")
    if confirm.lower() == 'y':
        clean_soul_link()
    else:
        print("Aborted.")