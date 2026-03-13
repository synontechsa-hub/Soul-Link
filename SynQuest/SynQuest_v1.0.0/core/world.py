from pydantic import BaseModel
from typing import Dict, List, Optional


class Room(BaseModel):
    id: str
    name: str
    description: str
    exits: Dict[str, str]  # direction -> room_id
    items: List[str] = []


# SynQuest: The Ashen Veil — World Map
WORLD_MAP: Dict[str, Room] = {
    "village_square": Room(
        id="village_square",
        name="The Village Square",
        description="A cobblestone square choked with grey weeds. The fountain is a cracked basin filled with stagnant black water that occasionally ripples with no wind.",
        exits={"north": "dark_forest", "east": "tavern", "south": "ruined_crypt"}
    ),
    "dark_forest": Room(
        id="dark_forest",
        name="The Dark Forest Edge",
        description="The trees here are ancient and wrong — bark split open like wounds, sap the color of dried blood. Something large drags itself through the undergrowth just out of sight.",
        exits={"south": "village_square"}
    ),
    "tavern": Room(
        id="tavern",
        name="The Rusty Boar Tavern",
        description="Tables lie on their sides like slain beasts. A single tallow candle burns on the bar, its flame bending toward the door as if trying to escape. You smell old blood and cheaper ale.",
        exits={"west": "village_square"},
        items=["health_potion"]
    ),
    "ruined_crypt": Room(
        id="ruined_crypt",
        name="The Sundered Crypt",
        description="Stone steps descend into darkness. The air tastes of wet bone. Faint scratching comes from behind the sealed doors.",
        exits={"north": "village_square", "down": "forgotten_altar"}
    ),
    "forgotten_altar": Room(
        id="forgotten_altar",
        name="The Shattered Altar",
        description="A black stone slab stained with centuries of sacrifice. The statue of the old sun-god has no head — only a jagged stump leaking shadow.",
        exits={"up": "ruined_crypt"},
        items=["cursed_amulet"]
    ),
}


def get_room(room_id: str) -> Optional[Room]:
    return WORLD_MAP.get(room_id)
