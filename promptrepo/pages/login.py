import reflex as rx

from promptrepo.auth.auth_state import AuthState

@rx.page(on_load=AuthState.login)
def login() -> rx.Component:
    return rx.box(
        rx.text("Authenticating with GitHub. Will be redirecting to Prompt Repo shortly..."),
    )