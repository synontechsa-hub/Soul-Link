
import os
import re

# Paths
BASE_DIR = r"d:\Coding\SynonTech\SoulLink_v1.5.5\_dev"
PRIMORDIALS_DIR = os.path.join(BASE_DIR, "data", "flagship_souls", "the_seven")
OUTPUT_FILE = os.path.join(BASE_DIR, "primordials_prompts.txt")

def extract_field(content, field_name):
    match = re.search(f"- {field_name}:\\s*(.+)", content, re.IGNORECASE)
    return match.group(1).strip() if match else ""

def extract_section(content, section_name):
    # Match section header until next numbered section or end of file
    pattern = rf"{section_name}.*?\n(.*?)(?=\n\d\.|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

def generate_primordial_prompt(filename):
    filepath = os.path.join(PRIMORDIALS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    name = extract_field(content, "Name")
    title = extract_field(content, "Title")
    domain = extract_field(content, "Domain")
    
    # Appearance details
    hair = extract_field(content, "Hair")
    eyes = extract_field(content, "Eyes")
    build = extract_field(content, "Build")
    style = extract_field(content, "Style")
    
    # Throne room context
    throne_room = extract_field(content, "Throne Room")
    throne_features = extract_field(content, "Features")
    
    # Base Cyberpunk/Divine Style
    base_style = "hyper-realistic, volumetric lighting, unreal engine 5, 8k, cinematic, divine aura, cyberpunk neon accents, masterpiece, intricate detail"
    
    appearance_desc = f"{build}, {hair} hair, {eyes} eyes, wearing {style}."
    background_desc = f"Background: {throne_room}. {throne_features}."
    
    # Portrait 9:16
    portrait = f"Epic Portrait of {name} ({title}). {appearance_desc} {background_desc} {base_style}, aspect ratio 9:16, low angle shot, regal and imposing."
    
    # Thumbnail 1:1
    thumbnail = f"Iconic Headshot of {name}, {title}. Close up on face, {eyes} eyes glowing with ancient power. {base_style}, aspect ratio 1:1, centered, sharp focus."
    
    return name, portrait, thumbnail

files = sorted([f for f in os.listdir(PRIMORDIALS_DIR) if f.endswith(".txt")])
output = "--- PRIMORDIAL IMAGE PROMPTS ---\n\n"

for f in files:
    try:
        name, portrait, thumb = generate_primordial_prompt(f)
        output += f"=== {name} ===\n"
        output += f"PORTRAIT (9:16):\n{portrait}\n\n"
        output += f"THUMBNAIL (1:1):\n{thumb}\n"
        output += "-"*40 + "\n\n"
    except Exception as e:
        print(f"Error processing {f}: {e}")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(output)

print(f"Generated prompts for {len(files)} Primordials.")
print(f"Output: {OUTPUT_FILE}")
