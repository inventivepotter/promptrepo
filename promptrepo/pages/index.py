import reflex as rx

from promptrepo.auth.auth_state import AuthState
from promptrepo.components.layout import layout
from promptrepo.components.prbox import prbox

@rx.page()
def index() -> rx.Component:
    return layout(
        prbox(
            rx.text(
                "Explore and manage your prompts with ease.",
                rx.text("Access Token:", var=AuthState.access_token),
                rx.text("User:", var=AuthState.user),
                size="3",
            ),
        )
    )