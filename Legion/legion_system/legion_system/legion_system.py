import reflex as rx
from .state import LegionState

def dashboard() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.hstack(
                rx.heading("🔱 LEGION SWARM : MISSION CONTROL", size="8", color="cyan"),
                rx.spacer(),
                rx.text("OpenClaw Gateway: ", weight="bold", color="white"),
                rx.badge(
                    LegionState.gateway_status, 
                    color_scheme=rx.cond(LegionState.gateway_status == "Connected", "green", "red"),
                    variant="solid",
                    size="3"
                ),
                width="100%",
                padding_y="1em"
            ),
            rx.divider(),
            
            rx.hstack(
                rx.button(
                    "INITIALIZE LINK", 
                    on_click=LegionState.connect_to_openclaw,
                    color_scheme="cyan",
                    variant="outline",
                    size="3"
                ),
                width="100%",
                padding_y="1em"
            ),

            rx.heading("LIVE TELEMETRY FEED", size="4", color="gray"),
            rx.box(
                rx.vstack(
                    rx.foreach(
                        LegionState.logs,
                        lambda log: rx.text(log, font_family="monospace", size="2", color="green")
                    ),
                    align_items="flex-start",
                ),
                bg="black",
                border="1px solid #333",
                padding="1em",
                border_radius="md",
                width="100%",
                height="500px",
                overflow_y="auto",
                box_shadow="0 0 10px rgba(0,255,255,0.1)"
            ),
            width="100%",
            spacing="4"
        ),
        max_width="1200px",
        padding="2em"
    )

app = rx.App(
    theme=rx.theme(
        appearance="dark", 
        has_background=True, 
        radius="none", 
        accent_color="cyan"
    )
)
app.add_page(dashboard, route="/", title="Legion Swarm")
