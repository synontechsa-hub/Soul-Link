"""
Generate an updated character_breakdown.txt from the actual soul JSON files.
"""
import json
import os

SOULS_DIR = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), "data", "souls")
OUTPUT_PATH = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), "notes", "character_breakdown.txt")


def main():
    souls = []

    for filename in sorted(os.listdir(SOULS_DIR)):
        if not filename.endswith(".json") or filename.startswith("_"):
            continue

        filepath = os.path.join(SOULS_DIR, filename)
        if not os.path.isfile(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        identity = data.get("identity", {})
        routine = data.get("routine", {})

        # Get STRANGER location_access as primary locations
        interaction = data.get("interaction_system", {})
        tiers = interaction.get("intimacy_tiers", {})
        stranger = tiers.get("STRANGER", {})
        locations = stranger.get("location_access", [])

        # Map archetype_id to a readable name from the identity
        archetype_id = identity.get("archetype_id", "Unknown")
        archetype_display = archetype_id.replace(
            "___", " / ").replace("_", " ").title()

        souls.append({
            "name": identity.get("name", "Unknown"),
            "age": identity.get("age", "?"),
            "gender": identity.get("gender", "?"),
            "filename": filename,
            "archetype": archetype_display,
            "faction": identity.get("faction_id", "Unknown"),
            "routine": routine.get("template_id", "Unknown"),
            "locations": locations,
            "summary": identity.get("summary", ""),
            "occupation": identity.get("occupation", ""),
        })

    lines = []
    lines.append("CHARACTER BREAKDOWN REPORT")
    lines.append(f"Generated for SoulLink v1.5.6")
    lines.append(f"Total Souls: {len(souls)}")
    lines.append("")

    for soul in souls:
        lines.append("-" * 50)
        lines.append(f"SOUL: {soul['name']} ({soul['age']}, {soul['gender']})")
        lines.append(f"FILE: {soul['filename']}")
        lines.append("-" * 50)
        lines.append(f"ARCHETYPE: {soul['archetype']}")
        lines.append(f"FACTION:   {soul['faction']}")
        lines.append(f"ROUTINE:   {soul['routine']}")
        lines.append(f"OCCUPATION: {soul['occupation']}")
        loc_str = ", ".join(soul["locations"][:5])
        if len(soul["locations"]) > 5:
            loc_str += "..."
        lines.append(f"LOCATIONS: {loc_str}")
        summary = soul["summary"]
        if len(summary) > 180:
            summary = summary[:180] + "..."
        lines.append(f"SUMMARY:   {summary}")
        lines.append("")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Generated character breakdown for {len(souls)} souls.")
    print(f"Written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
