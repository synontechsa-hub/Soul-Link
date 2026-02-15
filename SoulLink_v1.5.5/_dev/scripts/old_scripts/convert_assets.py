# /_dev/scripts/convert_assets.py
import os
from PIL import Image

from pathlib import Path

# Path to your soul portraits
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
ASSETS_DIR = str(project_root / "assets" / "images" / "souls")

def sanitize_images():
    print(f"🚀 Scanning {ASSETS_DIR} for non-jpeg signals...")
    
    for filename in os.listdir(ASSETS_DIR):
        if filename.lower().endswith((".png", ".webp", ".jpg")):
            # Construct full paths
            file_path = os.path.join(ASSETS_DIR, filename)
            
            # If it's already a .jpeg, we leave it alone
            if filename.lower().endswith(".jpeg"):
                continue
                
            # Define the new name
            name_without_ext = os.path.splitext(filename)[0]
            new_path = os.path.join(ASSETS_DIR, f"{name_without_ext}.jpeg")
            
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                    img = img.crop((0, 0, width, height - 60))
                    # Convert to RGB (required for JPEG if source is PNG/RGBA)
                    rgb_img = img.convert("RGB")
                    rgb_img.save(new_path, "JPEG", quality=95)
                
                # Optionally delete the old file to keep it clean
                os.remove(file_path)
                print(f"✅ Converted: {filename} -> {name_without_ext}.jpeg")
            except Exception as e:
                print(f"❌ Failed to convert {filename}: {e}")

if __name__ == "__main__":
    sanitize_images()
    print("✨ Folder is now 100% JPEG compliant.")