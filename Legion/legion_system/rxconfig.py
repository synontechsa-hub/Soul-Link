import reflex as rx

config = rx.Config(
    app_name="legion_system",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)