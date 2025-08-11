import reflex as rx
from promptrepo.states import AuthState, RepoState
from promptrepo.components import layout

@rx.page(on_load=AuthState.authenticate)
def prompts() -> rx.Component:
    return layout(
        rx.vstack(
            rx.heading("Prompts Page", size="9"),
            rx.select(
                RepoState.selected_repo_names,
                placeholder="Select a repository",
                on_change=RepoState.set_current_repo,
            ),
            rx.text("Welcome to the Prompts section!", size="5"),
        )
    )