import reflex as rx
from promptrepo.components import layout

def app_page() -> rx.Component:
    """The app page."""
    return layout(
        rx.vstack(
            rx.heading("App Page", size="9"),
            rx.text("Welcome to the App section!", size="5"),
        )
    )