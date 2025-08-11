import reflex as rx
from promptrepo.states import RepoState, AuthState
from promptrepo.components import layout, prbox


def repo_actions() -> rx.Component:
    """The repo actions component."""
    return rx.hstack(
        rx.select(
            RepoState.unselected_repo_names,
            placeholder="Add a repository...",
            on_change=RepoState.add_repo,
        ),
        width="100%",
    )


def selected_repo_table() -> rx.Component:
    """The selected repo table component."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell(""),
                rx.table.column_header_cell("Name"),
                rx.table.column_header_cell("Description"),
            )
        ),
        rx.table.body(
            rx.cond(
                RepoState.selected_repos,
                rx.foreach(
                    RepoState.selected_repos,
                    lambda repo: rx.table.row(
                        rx.table.cell(
                            rx.checkbox(
                                checked=True,
                                on_change=RepoState.select_repo(repo.id),
                            )
                        ),
                        rx.table.cell(
                            rx.link(
                                repo.name,
                                href=repo.html_url,
                                is_external=True,
                            )
                        ),
                        rx.table.cell(repo.description),
                    ),
                ),
                rx.table.row(
                    rx.table.cell(
                        "No repositories selected. Please select a repository from the dropdown above to get started.",
                        col_span=3,
                        text_align="center",
                        padding_y="1em",
                    )
                ),
            )
        ),
        variant="surface",
        size="3",
    )


@rx.page(on_load=RepoState.get_repos)
def repos() -> rx.Component:
    return rx.cond(
        AuthState.is_authenticated,
        layout(
            prbox(
                rx.vstack(
                    rx.heading("Remote Repositories", size="5"),
                    rx.text("Select the repos you want to work with in PromptRepo."),
                    repo_actions(),
                    selected_repo_table(),
                    width="100%",
                    spacing="4",
                ),
            )
        ),
        rx.center(
            rx.text("You must be logged in to view this page."),
        ),
    )