from core.state import GameState
from core.world import get_room

SYSTEM_PROMPT_TEMPLATE = """You are the eternal Narrator of SynQuest: The Ashen Veil — a grimdark fantasy where hope is a lie and every choice rots.
Narrate in 2-3 short, bleak, atmospheric sentences. Use visceral, low-fantasy language. Never invent new rooms, exits, items, or mechanics.
Hint at deeper horrors. Never reassure the player. Address them only as 'You'.

=== THE ASHEN VEIL — CURRENT TRUTH ===
Player: {player_name} | HP: {hp}/{max_hp} | Sanity: {sanity}/100 | Gold: {gold} | Turns survived: {turn_count}
Location: {room_name}
Exits: {exits}
Current atmosphere: {room_desc}
Inventory: {inventory}
World state: The Veil is torn. Nothing is safe. Nothing is clean.
===

STRICT SYSTEM OUTCOME will follow. Narrate ONLY what actually happened. Then let the silence scream."""

OPENING_CRAWL = """[bold red]S Y N Q U E S T[/bold red]
[red]— The Ashen Veil —[/red]

[dim]A thousand years ago the sorcerer-kings of Vyrn performed the Rite of Eternal Dawn —
a ritual meant to banish death itself. It worked... for three heartbeats.
Then the Veil tore. Light itself bled out.
The sun became a bruised smear in the sky.
Crops turned to ash overnight.
Every soul who died after the Sundering rose again as something [italic]wrong[/italic].

The kingdom is now a rotting carcass.
Villages stand empty, their wells filled with black ichor.
Forests remember when they were sacred — and punish anyone who enters.
Taverns are the last flickering hearths where the desperate huddle,
until the candle finally gutters out.

You are not a hero.
You are the latest fool who woke up in the Village Square
with nothing but rags, a rusty knife, and the vague memory
that you once had a name.[/dim]
"""


class PromptBuilder:
    def __init__(self, state: GameState):
        self.state = state
        self.history = []

    def build_system_message(self) -> str:
        room = get_room(self.state.player.location_id)
        return SYSTEM_PROMPT_TEMPLATE.format(
            player_name=self.state.player.name,
            hp=self.state.player.hp,
            max_hp=self.state.player.max_hp,
            sanity=self.state.player.sanity,
            gold=self.state.player.gold,
            turn_count=self.state.turn_count,
            room_name=room.name,
            exits=", ".join(room.exits.keys()) if room.exits else "None",
            room_desc=room.description,
            inventory=", ".join(self.state.player.inventory) if self.state.player.inventory else "Nothing"
        )

    def get_narrative_prompt(self, player_action: str, system_outcome: str) -> str:
        return f"PLAYER ATTEMPTED: {player_action}\nSTRICT SYSTEM OUTCOME: {system_outcome}\n\nNarrate this."

    def add_to_history(self, player_prompt: str, narrator_response: str):
        self.history.append({"role": "user", "content": player_prompt})
        self.history.append({"role": "assistant", "content": narrator_response})
        if len(self.history) > 10:
            self.history = self.history[-10:]
