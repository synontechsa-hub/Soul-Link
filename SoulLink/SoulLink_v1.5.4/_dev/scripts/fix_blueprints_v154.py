import os

def fix_blueprints():
    path = '_dev/blueprints'
    for filename in os.listdir(path):
        if filename.endswith('.json'):
            filepath = os.path.join(path, filename)
            
            # 1. Read the content fully
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 2. Perform replacement
            new_content = content.replace('1.5.3-P', '1.5.4 Arise')
            
            # 3. Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
    
    print("✅ All blueprints synchronized to v1.5.4 Arise.")

if __name__ == "__main__":
    fix_blueprints()
