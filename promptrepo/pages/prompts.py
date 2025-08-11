import reflex as rx
from promptrepo.states import AuthState
from promptrepo.components import layout

@rx.page(on_load=AuthState.authenticate)
def prompts() -> rx.Component:
    return layout(
        rx.vstack(
            rx.heading("Prompts Page", size="9"),
            rx.text("Welcome to the Prompts section!", size="5"),
        )
    )