"""
Phase 2: Bump all system config file versions from 1.5.5 to 1.5.6.
"""
import json
import os
import sys

SYSTEM_DIR = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), "data", "system")


def bump_version(filepath: str) -> bool:
    """Bump version fields from 1.5.5 to 1.5.6. Returns True if changes were made."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if '"1.5.5"' not in content:
        return False

    new_content = content.replace('"1.5.5"', '"1.5.6"')

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    return True


def main():
    if not os.path.isdir(SYSTEM_DIR):
        print(f"ERROR: System directory not found: {SYSTEM_DIR}")
        sys.exit(1)

    print(f"Bumping versions in: {SYSTEM_DIR}")
    print("=" * 60)

    changed = 0
    skipped = 0

    for root, dirs, files in os.walk(SYSTEM_DIR):
        for filename in sorted(files):
            if not filename.endswith(".json"):
                continue

            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, SYSTEM_DIR)

            if bump_version(filepath):
                print(f"  ✓ {rel_path}: bumped to 1.5.6")
                changed += 1
            else:
                print(f"  - {rel_path}: already at 1.5.6")
                skipped += 1

    print("=" * 60)
    print(f"Updated {changed} files, {skipped} already current.")


if __name__ == "__main__":
    main()
