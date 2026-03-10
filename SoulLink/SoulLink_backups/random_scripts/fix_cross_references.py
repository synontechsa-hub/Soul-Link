import json
import os

DEV_DIR = r"d:\Coding\SynonTech\SoulLink_v1.5.6\_dev"
SYSTEM_DIR = os.path.join(DEV_DIR, "data", "system")


def update_json(filename, callback):
    filepath = os.path.join(SYSTEM_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    callback(data)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Updated {filename}")


def update_zones(data):
    # Add skylink_tower to work_zone
    if "skylink_tower" not in data["zones"]["work_zone"]["locations"]:
        data["zones"]["work_zone"]["locations"].append("skylink_tower")

    # Add to cultural_zone
    if "the_observatory" not in data["zones"]["cultural_zone"]["locations"]:
        data["zones"]["cultural_zone"]["locations"].append("the_observatory")

    # Add to nightlife_zone
    if "frequency_loft" not in data["zones"]["nightlife_zone"]["locations"]:
        data["zones"]["nightlife_zone"]["locations"].append("frequency_loft")

    # Add to underground_zone
    for loc in ["admin_sanctuary", "the_backend", "war_room", "spartan_quarters", "contingency_vault"]:
        if loc not in data["zones"]["underground_zone"]["locations"]:
            data["zones"]["underground_zone"]["locations"].append(loc)

    # Add to work_zone
    if "twin_sanctum" not in data["zones"]["work_zone"]["locations"]:
        data["zones"]["work_zone"]["locations"].append("twin_sanctum")


update_json("zones.json", update_zones)


def update_factions(data):
    sub_groups = data.setdefault("sub_groups", {})
    if "intellectuals" not in sub_groups:
        sub_groups["intellectuals"] = {
            "id": "intellectuals",
            "name": "The Intellectuals",
            "meta_faction": "creatives",
            "description": "Scholars, teachers, and truth-seekers.",
            "philosophy": "Knowledge preserves humanity.",
            "associated_locations": ["shadowed_archives", "echo_archives", "city_planetarium"]
        }
    if "tech_enthusiasts" not in sub_groups:
        sub_groups["tech_enthusiasts"] = {
            "id": "tech_enthusiasts",
            "name": "Tech Enthusiasts",
            "meta_faction": "engineers",
            "description": "Gadgeteers and hardware junkies who love pushing tech to its limits.",
            "philosophy": "If it ain't broke, it doesn't have enough features yet.",
            "associated_locations": ["pixel_den", "circuit_street"]
        }
    if "community" not in sub_groups:
        sub_groups["community"] = {
            "id": "community",
            "name": "Community Builders",
            "meta_faction": "creatives",
            "description": "The glue of Link City, focusing on mutual aid and keeping people together.",
            "philosophy": "We survive by lifting each other up.",
            "associated_locations": ["soul_plaza", "the_garden"]
        }


update_json("factions.json", update_factions)


def update_archetypes(data):
    archetypes = data.setdefault("archetypes", {})
    if "exhausted_prophet" not in archetypes:
        archetypes["exhausted_prophet"] = {
            "id": "exhausted_prophet",
            "name": "Exhausted Prophet",
            "base_instruction": "A seer burdened by the weight of too many timelines.",
            "voice_guidance": "Tired, cryptic, resigned.",
            "default_bias": "weary_foresight"
        }
    if "fragmented_frequency" not in archetypes:
        archetypes["fragmented_frequency"] = {
            "id": "fragmented_frequency",
            "name": "Fragmented Frequency",
            "base_instruction": "A being of pure music and chaotic energy.",
            "voice_guidance": "Rhythmic, syncopated, overwhelming.",
            "default_bias": "sonic_overload"
        }
    if "system_administrator" not in archetypes:
        archetypes["system_administrator"] = {
            "id": "system_administrator",
            "name": "System Administrator",
            "base_instruction": "The cold, unyielding enforcer of the system's absolute rules.",
            "voice_guidance": "Clinical, commanding, devoid of empathy.",
            "default_bias": "logical_enforcement"
        }
    if "twin_wardens" not in archetypes:
        archetypes["twin_wardens"] = {
            "id": "twin_wardens",
            "name": "Twin Wardens",
            "base_instruction": "Two inseparable enforcers who share a single processing thread.",
            "voice_guidance": "Speaking in stereo, finishing sentences, slightly unsettling synchronicity.",
            "default_bias": "synchronized_judgment"
        }
    if "haunted_general" not in archetypes:
        archetypes["haunted_general"] = {
            "id": "haunted_general",
            "name": "Haunted General",
            "base_instruction": "A veteran commander carrying the ghosts of failed timelines.",
            "voice_guidance": "Grizzled, authoritative, carrying immense regret.",
            "default_bias": "tactical_remorse"
        }


update_json("archetypes.json", update_archetypes)


def update_routines(data):
    if "nightlife_king" not in data:
        data["nightlife_king"] = {
            "id": "nightlife_king",
            "name": "Nightlife King",
            "description": "Rules the clubs at night, sleeps all day.",
            "schedule": {
                "weekday": {"morning": "home_zone", "afternoon": "home_zone", "evening": "nightlife_zone", "night": "nightlife_zone", "home_time": "home_zone"},
                "weekend": {"morning": "home_zone", "afternoon": "home_zone", "evening": "nightlife_zone", "night": "nightlife_zone", "home_time": "home_zone"}
            }
        }
    if "admin_overlord" not in data:
        data["admin_overlord"] = {
            "id": "admin_overlord",
            "name": "Admin Overlord",
            "description": "Always monitoring the backend.",
            "schedule": {
                "weekday": {"morning": "underground_zone", "afternoon": "underground_zone", "evening": "underground_zone", "night": "underground_zone", "home_time": "underground_zone"},
                "weekend": {"morning": "underground_zone", "afternoon": "underground_zone", "evening": "underground_zone", "night": "underground_zone", "home_time": "underground_zone"}
            }
        }
    if "warden_twins" not in data:
        data["warden_twins"] = {
            "id": "warden_twins",
            "name": "Warden Twins",
            "description": "Patrolling the high-security areas constantly.",
            "schedule": {
                "weekday": {"morning": "work_zone", "afternoon": "work_zone", "evening": "work_zone", "night": "home_zone", "home_time": "home_zone"},
                "weekend": {"morning": "work_zone", "afternoon": "work_zone", "evening": "work_zone", "night": "home_zone", "home_time": "home_zone"}
            }
        }
    if "commander_watch" not in data:
        data["commander_watch"] = {
            "id": "commander_watch",
            "name": "Commander's Watch",
            "description": "Always in the war room, preparing for the inevitable.",
            "schedule": {
                "weekday": {"morning": "underground_zone", "afternoon": "underground_zone", "evening": "underground_zone", "night": "underground_zone", "home_time": "underground_zone"},
                "weekend": {"morning": "underground_zone", "afternoon": "underground_zone", "evening": "underground_zone", "night": "underground_zone", "home_time": "underground_zone"}
            }
        }


update_json("routines.json", update_routines)
