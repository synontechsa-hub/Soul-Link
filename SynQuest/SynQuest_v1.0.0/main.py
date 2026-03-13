from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Header, Input, Static, RichLog
from textual.containers import Horizontal, Vertical

from core.state import GameState
from core.controller import GameController
from core.world import get_room
from llm.client import generate_narration
from llm.prompt_builder import PromptBuilder, OPENING_CRAWL


class StatsSidebar(Static):
    """Displays the player's mechanical state."""

    def update_stats(self, state: GameState):
        room = get_room(state.player.location_id)
        if not room:
            return

        # Sanity colour: green -> yellow -> red as it drops
        sanity = state.player.sanity
        if sanity > 60:
            sanity_color = "green"
        elif sanity > 30:
            sanity_color = "yellow"
        else:
            sanity_color = "red"

        content = f"""
[bold red]⚔  {state.player.name}[/bold red]

[b]HP[/b]     [red]{state.player.hp} / {state.player.max_hp}[/red]
[b]Sanity[/b] [{sanity_color}]{sanity} / 100[/{sanity_color}]
[b]Gold[/b]   [yellow]{state.player.gold}[/yellow]
[b]Turn[/b]   [dim]{state.turn_count}[/dim]

[b]📍 Location[/b]
[italic]{room.name}[/italic]

[b]🚪 Exits[/b]
{", ".join(room.exits.keys()) if room.exits else "[dim]None[/dim]"}

[b]🎒 Carrying[/b]
{chr(10).join([f"[dim]• {i}[/dim]" for i in state.player.inventory]) if state.player.inventory else "[dim]Nothing[/dim]"}
"""
        self.update(content)


class SynQuestApp(App):
    CSS = """
    Screen {
        layout: horizontal;
        background: #0a0a0a;
    }
    #main-pane {
        width: 3fr;
        height: 100%;
        border-right: solid #3a0000;
    }
    #sidebar {
        width: 1fr;
        height: 100%;
        padding: 1 2;
        background: #0f0a0a;
        border-left: solid #1a0000;
    }
    #narrative-log {
        height: 1fr;
        border: blank;
        padding: 1 2;
    }
    #player-input {
        dock: bottom;
        margin: 1;
        border: solid #3a0000;
    }
    .system-msg {
        color: #555555;
        text-style: italic;
    }
    """

    def __init__(self):
        super().__init__()
        self.game_state = GameState()
        self.controller = GameController(self.game_state)
        self.prompt_builder = PromptBuilder(self.game_state)

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="main-pane"):
                yield Header(show_clock=True)
                yield RichLog(id="narrative-log", wrap=True, highlight=True, markup=True)
                yield Input(placeholder="> What do you do?", id="player-input")
            yield StatsSidebar(id="sidebar")

    def on_mount(self) -> None:
        log = self.query_one(RichLog)
        log.write(OPENING_CRAWL)

        room = get_room(self.game_state.player.location_id)
        if room:
            log.write(f"\n[dim]─────────────────────────────────[/dim]")
            log.write(f"[italic dim]{room.description}[/italic dim]")
            log.write(f"[dim]─────────────────────────────────[/dim]\n")

        self.query_one(StatsSidebar).update_stats(self.game_state)
        self.query_one(Input).focus()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        action = message.value.strip()
        message.input.value = ""
        if not action:
            return

        log = self.query_one(RichLog)

        if action.lower() in ["exit", "quit"]:
            self.exit()
            return

        # 1. Echo player command
        log.write(f"\n[bold cyan]> {action}[/bold cyan]")

        # 2. Mechanical resolution
        success, system_outcome = self.controller.process_command(action)

        # 3. Update sidebar immediately
        self.query_one(StatsSidebar).update_stats(self.game_state)
        log.write(f"[dim italic]{system_outcome}[/dim italic]")

        # 4. Fire off narrator in background thread
        log.write("[dim]... the darkness stirs ...[/dim]")
        self.fetch_narration(action, system_outcome)

    @work(thread=True)
    def fetch_narration(self, action: str, outcome: str):
        log = self.query_one(RichLog)
        sys_msg = self.prompt_builder.build_system_message()
        prompt = self.prompt_builder.get_narrative_prompt(action, outcome)

        try:
            narrative = generate_narration(sys_msg, self.prompt_builder.history, prompt)
            self.prompt_builder.add_to_history(prompt, narrative)
            self.call_from_thread(log.write, f"\n[white]{narrative}[/white]\n")
        except Exception as e:
            self.call_from_thread(log.write, f"\n[bold red]Narrator Error:[/bold red] {str(e)}\n")


if __name__ == "__main__":
    app = SynQuestApp()
    app.run()
