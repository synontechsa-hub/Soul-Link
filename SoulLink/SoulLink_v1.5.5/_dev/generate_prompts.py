
import os
import re

# Paths
BASE_DIR = r"d:\Coding\SynonTech\SoulLink_v1.5.5\_dev"
CHAR_SHEETS_DIR = os.path.join(BASE_DIR, "character_sheets")
PROMPTS_FILE = os.path.join(BASE_DIR, "soul_prompts.txt")
THUMBNAIL_FILE = os.path.join(BASE_DIR, "thumbnail_prompts.txt")

def parse_key_value(text, key):
    pattern = re.compile(f"^{key}:\\s*(.+)$", re.MULTILINE | re.IGNORECASE)
    match = pattern.search(text)
    return match.group(1).strip() if match else "Unknown"

def parse_section(text, header):
    pattern = re.compile(f"^{header}:?\\s*\\n(.*?)(?=\\n[A-Z_]+:|\\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""

def generate_prompts(filename):
    filepath = os.path.join(CHAR_SHEETS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    name = parse_key_value(content, "NAME")
    archetype = parse_key_value(content, "ARCHETYPE")
    description = parse_section(content, "DESCRIPTION").replace("\n", " ")
    
    # Base Cyberpunk Theme
    base_style = "cyberpunk 2077 style, futuristic fashion, neon lighting, volumetric fog, cinematic lighting, highly detailed, 8k, unreal engine 5 render, photorealistic, masterpiece"
    
    # Portrait Prompt (9:16)
    # emphasize full body / cinematic context
    portrait_prompt = (
        f"Portrait of {name}, {archetype}, {description}. "
        f"Full body shot, standing in a futuristic city street or high-tech interior. "
        f"{base_style}, vertical aspect ratio 9:16, depth of field, ray tracing."
    )
    
    # Thumbnail Prompt (1:1)
    # emphasize face / expression
    thumbnail_prompt = (
        f"Headshot of {name}, {archetype}, {description}. "
        f"Close up on face, expressive eyes, detailed skin texture. "
        f"Soft neon backlight. {base_style}, square aspect ratio 1:1, centered composition, icon style."
    )
    
    return name, portrait_prompt, thumbnail_prompt

# Main execution
files = sorted([f for f in os.listdir(CHAR_SHEETS_DIR) if f.endswith(".txt")])

portrait_output = ""
thumbnail_output = ""

for file in files:
    try:
        name, portrait, thumb = generate_prompts(file)
        
        portrait_output += f"--- {name} ---\n{portrait}\n\n"
        thumbnail_output += f"--- {name} ---\n{thumb}\n\n"
        
    except Exception as e:
        print(f"Error processing {file}: {e}")

with open(PROMPTS_FILE, "w", encoding="utf-8") as f:
    f.write(portrait_output)
    
with open(THUMBNAIL_FILE, "w", encoding="utf-8") as f:
    f.write(thumbnail_output)

print(f"Generated prompts for {len(files)} souls.")
print(f"Portraits: {PROMPTS_FILE}")
print(f"Thumbnails: {THUMBNAIL_FILE}")
