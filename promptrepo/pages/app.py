import reflex as rx
from promptrepo.components import layout

@rx.page()
def app() -> rx.Component:
    return layout(
        rx.vstack(
            rx.heading("App Page", size="9"),
            rx.text("Welcome to the App section!", size="5"),
        )
    )