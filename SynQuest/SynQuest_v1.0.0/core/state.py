from pydantic import BaseModel, Field
from typing import List


class PlayerState(BaseModel):
    name: str = "Wanderer"
    hp: int = 100
    max_hp: int = 100
    sanity: int = 100       # Added: erodes as the Veil takes hold
    gold: int = 0
    location_id: str = "village_square"
    inventory: List[str] = Field(default_factory=list)


class GameState(BaseModel):
    player: PlayerState = Field(default_factory=PlayerState)
    turn_count: int = 0
    world_flags: dict = Field(default_factory=dict)
