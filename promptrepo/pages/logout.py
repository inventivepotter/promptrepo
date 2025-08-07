import reflex as rx

from promptrepo.auth.auth_state import AuthState

@rx.page(on_load=AuthState.logout)
def logout() -> rx.Component:
    return rx.box(
        rx.text("Logging out..."),
    )