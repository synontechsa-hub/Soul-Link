from .state import GameState
from .world import get_room, WORLD_MAP

# Items that drain sanity when carried
CURSED_ITEMS = {
    "cursed_amulet": {"sanity_drain": 2, "description": "a tarnished amulet that feels wrong in your hand"},
}

# Items that restore HP when used
CONSUMABLES = {
    "health_potion": {"hp_restore": 40, "description": "a vial of murky red liquid"},
}


class GameController:
    def __init__(self, state: GameState):
        self.state = state

    def process_command(self, action: str) -> tuple[bool, str]:
        """
        Takes raw player input and applies strict mechanical changes.
        Returns (success_bool, system_message).
        """
        action = action.lower().strip()
        parts = action.split()
        if not parts:
            return False, "SYSTEM: Nothing happened."

        verb = parts[0]
        noun = parts[-1] if len(parts) > 1 else ""

        # --- MOVEMENT ---
        if verb in ["go", "move", "walk", "north", "south", "east", "west", "up", "down"]:
            direction = noun if verb in ["go", "move", "walk"] else verb
            current_room = get_room(self.state.player.location_id)

            if direction in current_room.exits:
                self.state.player.location_id = current_room.exits[direction]
                new_room = get_room(self.state.player.location_id)
                self._tick_curse()
                self.state.turn_count += 1
                return True, f"SYSTEM: Player moved to {new_room.name}."
            else:
                return False, f"SYSTEM: No exit to the {direction} from here."

        # --- LOOK / EXAMINE ---
        if verb in ["look", "examine", "inspect", "l"]:
            room = get_room(self.state.player.location_id)
            items_str = f" Items present: {', '.join(room.items)}." if room.items else " The room holds nothing of use."
            return True, f"SYSTEM: Player examined their surroundings.{items_str}"

        # --- TAKE / PICK UP ---
        if verb in ["take", "grab", "pick", "get"]:
            room = get_room(self.state.player.location_id)
            if noun in room.items:
                room.items.remove(noun)
                self.state.player.inventory.append(noun)
                self.state.turn_count += 1
                curse_note = " It pulses with a sickly warmth." if noun in CURSED_ITEMS else ""
                return True, f"SYSTEM: Player picked up {noun}.{curse_note}"
            elif noun in self.state.player.inventory:
                return False, f"SYSTEM: {noun} is already in inventory."
            else:
                return False, f"SYSTEM: No {noun} here to take."

        # --- DROP ---
        if verb == "drop":
            if noun in self.state.player.inventory:
                self.state.player.inventory.remove(noun)
                room = get_room(self.state.player.location_id)
                room.items.append(noun)
                self.state.turn_count += 1
                return True, f"SYSTEM: Player dropped {noun}."
            else:
                return False, f"SYSTEM: Player doesn't have {noun}."

        # --- USE ---
        if verb in ["use", "drink", "consume"]:
            if noun in self.state.player.inventory:
                if noun in CONSUMABLES:
                    item = CONSUMABLES[noun]
                    healed = min(item["hp_restore"], self.state.player.max_hp - self.state.player.hp)
                    self.state.player.hp += healed
                    self.state.player.inventory.remove(noun)
                    self.state.turn_count += 1
                    return True, f"SYSTEM: Player used {noun}. HP restored by {healed}. Current HP: {self.state.player.hp}/{self.state.player.max_hp}."
                else:
                    return False, f"SYSTEM: Nothing happens when the player tries to use {noun}."
            else:
                return False, f"SYSTEM: Player doesn't have {noun}."

        # --- INVENTORY ---
        if verb in ["inventory", "inv", "i"]:
            if self.state.player.inventory:
                items = ", ".join(self.state.player.inventory)
                return True, f"SYSTEM: Player checked inventory. Carrying: {items}."
            else:
                return True, "SYSTEM: Player checked inventory. Carrying nothing."

        # --- CATCH-ALL ---
        self.state.turn_count += 1
        return True, f"SYSTEM: Player attempted '{action}'. Nothing concrete occurred."

    def _tick_curse(self):
        """Drain sanity for each cursed item carried."""
        for item in self.state.player.inventory:
            if item in CURSED_ITEMS:
                drain = CURSED_ITEMS[item]["sanity_drain"]
                self.state.player.sanity = max(0, self.state.player.sanity - drain)
