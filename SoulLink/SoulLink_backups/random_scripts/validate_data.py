"""
Validation script: Verifies all data folder cleanup changes were applied correctly.
"""
import json
import os
import sys

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SOULS_DIR = os.path.join(BASE_DIR, "souls")
SYSTEM_DIR = os.path.join(BASE_DIR, "system")

errors = []
warnings = []
passed = 0


def check(condition, msg):
    global passed
    if condition:
        passed += 1
    else:
        errors.append(msg)


def warn(msg):
    warnings.append(msg)


def main():
    global passed

    print("=" * 60)
    print("DATA FOLDER VALIDATION")
    print("=" * 60)

    # 1. Schema check: all standard souls have type, version, meta_data
    print("\n[1] Checking standard soul schemas...")
    soul_count = 0
    for f in sorted(os.listdir(SOULS_DIR)):
        if not f.endswith(".json") or f.startswith("_"):
            continue
        fp = os.path.join(SOULS_DIR, f)
        if not os.path.isfile(fp):
            continue

        with open(fp, "r", encoding="utf-8") as fh:
            d = json.load(fh)

        soul_count += 1
        check(d.get("type") == "standard", f"{f}: missing type='standard'")
        check(d.get("version") == "1.5.6",
              f"{f}: version is {d.get('version')}, expected 1.5.6")
        check("meta_data" in d, f"{f}: missing meta_data section")

    print(f"    Checked {soul_count} soul files")

    # 2. Gender check: no M/F abbreviations
    print("\n[2] Checking gender normalization...")
    for f in sorted(os.listdir(SOULS_DIR)):
        if not f.endswith(".json") or f.startswith("_"):
            continue
        fp = os.path.join(SOULS_DIR, f)
        if not os.path.isfile(fp):
            continue

        with open(fp, "r", encoding="utf-8") as fh:
            d = json.load(fh)

        gender = d.get("identity", {}).get("gender", "")
        check(gender in ("Male", "Female"),
              f"{f}: gender is '{gender}', expected Male/Female")

    # 3. Stress trigger check: no STAGE_ keys
    print("\n[3] Checking stress trigger format...")
    for f in sorted(os.listdir(SOULS_DIR)):
        if not f.endswith(".json") or f.startswith("_"):
            continue
        fp = os.path.join(SOULS_DIR, f)
        if not os.path.isfile(fp):
            continue

        with open(fp, "r", encoding="utf-8") as fh:
            d = json.load(fh)

        stress = d.get("interaction_system", {}).get("stress_trigger", {})
        check("responses" not in stress,
              f"{f}: still has 'responses' dict (should be flat 'response')")
        has_stage = any("STAGE" in k for k in stress.keys())
        check(not has_stage, f"{f}: still has STAGE_ keys")

    # 4. Version check: all system configs at 1.5.6
    print("\n[4] Checking system config versions...")
    for root, dirs, files in os.walk(SYSTEM_DIR):
        for f in sorted(files):
            if not f.endswith(".json"):
                continue
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, SYSTEM_DIR)

            with open(fp, "r", encoding="utf-8") as fh:
                d = json.load(fh)

            ver = d.get("version", "?")
            check(ver == "1.5.6", f"system/{rel}: version is {ver}")

    # 5. Linkside check
    print("\n[5] Checking linkside_estate not in zones...")
    zones_fp = os.path.join(SYSTEM_DIR, "zones.json")
    with open(zones_fp, "r", encoding="utf-8") as fh:
        zones = json.load(fh)

    for zone_id, zone_data in zones.get("zones", {}).items():
        locs = zone_data.get("locations", [])
        check("linkside_estate" not in locs,
              f"zones.json {zone_id}: still contains linkside_estate")

    # 6. Routine check: oracle_vigil exists
    print("\n[6] Checking oracle_vigil routine exists...")
    routines_fp = os.path.join(SYSTEM_DIR, "routines.json")
    with open(routines_fp, "r", encoding="utf-8") as fh:
        routines = json.load(fh)
    check("oracle_vigil" in routines, "routines.json: oracle_vigil not found")

    # 7. File location check: no .txt in data dirs
    print("\n[7] Checking no .txt files in data directories...")
    for f in os.listdir(SOULS_DIR):
        if f.endswith(".txt"):
            check(False, f"souls/{f}: txt file still in data dir")

    for f in os.listdir(SYSTEM_DIR):
        if f.endswith(".txt"):
            check(False, f"system/{f}: txt file still in data dir")

    # 8. Template check
    print("\n[8] Checking template schema...")
    tpl_fp = os.path.join(SOULS_DIR, "template", "_template.json")
    with open(tpl_fp, "r", encoding="utf-8") as fh:
        tpl = json.load(fh)
    check(tpl.get("version") == "1.5.6",
          f"_template.json: version is {tpl.get('version')}")
    check(tpl.get("type") == "standard",
          f"_template.json: missing type='standard'")
    check("meta_data" in tpl, f"_template.json: missing meta_data")
    stress = tpl.get("interaction_system", {}).get("stress_trigger", {})
    check("response" in stress,
          f"_template.json: stress_trigger missing flat 'response' key")

    # Results
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} checks passed")
    if errors:
        print(f"         {len(errors)} errors found:")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print(f"         {len(warnings)} warnings:")
        for w in warnings:
            print(f"  ⚠ {w}")
    if not errors and not warnings:
        print("         ALL CHECKS PASSED [OK]")
    print("=" * 60)

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
