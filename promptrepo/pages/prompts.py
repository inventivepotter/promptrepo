import reflex as rx
from promptrepo.states import AuthState
from promptrepo.components import layout, prbox

@rx.page(on_load=AuthState.authenticate)
def prompts() -> rx.Component:
    return layout(
        prbox()
    )