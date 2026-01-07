import os

OUTPUT_FILE = "root_folders.txt"

# Folders/files to ignore
IGNORE = {
    ".git", ".vscode", "__pycache__", ".idea", ".DS_Store",
    "node_modules", "build", "dist"
}

def tree(dir_path: str, prefix: str = "") -> str:
    """Recursively build a tree string for the given directory."""
    entries = sorted(
        [e for e in os.listdir(dir_path) if e not in IGNORE]
    )
    tree_str = ""
    for index, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        connector = "├── " if index < len(entries) - 1 else "└── "
        tree_str += f"{prefix}{connector}{entry}\n"
        if os.path.isdir(path):
            extension = "│   " if index < len(entries) - 1 else "    "
            tree_str += tree(path, prefix + extension)
    return tree_str

def main():
    root_dir = os.getcwd()  # current working directory in Codespace
    root_name = os.path.basename(root_dir)
    tree_output = f"{root_name}/\n" + tree(root_dir)

    # Print to console
    print(tree_output)

    # Write to root_folders.txt
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(tree_output)

    print(f"\nTree structure written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()