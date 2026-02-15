import os
from PIL import Image
import shutil

# Configuration
SOURCE_DIR = r"d:\Coding\SynonTech\SoulLink_v1.5.5\assets\images\locations"
TARGET_DIR = SOURCE_DIR  # Overwrite in place
TARGET_RATIO = 9 / 16
OVERWRITE = True

def process_images():
    print(f"🚀 Starting Image Processing...")
    print(f"📍 Source: {SOURCE_DIR}")
    print(f"🎯 Target: {TARGET_DIR}")
    print(f"📐 Target Ratio: 9:16")

    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)

    processed_count = 0
    skipped_count = 0

    # Walk through source directory
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Determine relative path to maintain structure
        rel_path = os.path.relpath(root, SOURCE_DIR)
        target_subdir = os.path.join(TARGET_DIR, rel_path)
        
        if not os.path.exists(target_subdir):
            os.makedirs(target_subdir)

        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                source_path = os.path.join(root, file)
                target_path = os.path.join(target_subdir, file)

                try:
                    with Image.open(source_path) as img:
                        width, height = img.size
                        
                        # Calculate crop dimensions
                        # We want 9:16. 
                        # If image is square (1:1), 9:16 means height is limiting factor if we want full width? 
                        # No, 9:16 is 0.5625. 1:1 is 1.0.
                        # Using full height (1024), width = 1024 * (9/16) = 576.
                        # Using full width (1024), height = 1024 * (16/9) = 1820. (Too big)
                        
                        # So we must fix Height to 1024 and Crop Width to 576.
                        
                        target_width = int(height * TARGET_RATIO)
                        target_height = height
                        
                        if target_width > width:
                            # If image is too wide? No.
                            # If we wanted 16:9 (1.77), target width would be 1820 (too big).
                            # If we stick to 9:16 vertical.
                            pass

                        # Center Crop
                        left = (width - target_width) / 2
                        top = (height - target_height) / 2
                        right = (width + target_width) / 2
                        bottom = (height + target_height) / 2

                        # Perform crop
                        img_cropped = img.crop((left, top, right, bottom))
                        
                        # Save
                        img_cropped.save(target_path)
                        print(f"✅ Processed: {file} ({width}x{height} -> {target_width}x{target_height})")
                        processed_count += 1

                except Exception as e:
                    print(f"❌ Error processing {file}: {e}")
                    skipped_count += 1
    
    print(f"\n✨ Done! Processed {processed_count} images. Skipped {skipped_count}.")
    print(f"📂 Output is in: {TARGET_DIR}")

if __name__ == "__main__":
    process_images()
