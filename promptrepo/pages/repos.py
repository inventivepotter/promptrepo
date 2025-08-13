import reflex as rx
from promptrepo.states import RepoState, AuthState
from promptrepo.components import layout, prbox


def repo_actions() -> rx.Component:
    """The repo actions component."""
    return rx.hstack(
        rx.select(
            RepoState.unselected_repo_names,
            placeholder="Add a repository...",
            value=RepoState.current_repo,
            on_change=lambda value: [RepoState.add_repo(value), RepoState.set_current_repo("")],
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


@rx.page(on_load=[RepoState.get_repos, RepoState.refresh_local_repos])
def repos() -> rx.Component:
    return rx.cond(
        AuthState.is_authenticated,
        layout(
            remote_repositories_box(),
            local_repositories_box(),
        ),
        rx.center(
            rx.text("You must be logged in to view this page."),
        ),
    )

def remote_repositories_box() -> rx.Component:
    """The remote repositories box component."""
    return prbox(
        rx.vstack(
            rx.heading("Remote Repositories", size="5"),
            rx.text("Select the repos you want to work with in PromptRepo. They will be cloned to the server.", size="2"),
            repo_actions(),
            selected_repo_table(),
            width="100%",
            spacing="4",
        ),
    )

import os

def local_repo_table() -> rx.Component:
    """Table of local repositories."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Name"),
            )
        ),
        rx.table.body(
            rx.cond(
                RepoState.local_repos,
                rx.foreach(
                    RepoState.local_repos,
                    lambda name: rx.table.row(
                        rx.table.cell(name),
                    ),
                ),
                rx.table.row(
                    rx.table.cell(
                        "No local repositories found.",
                        col_span=1,
                        text_align="center",
                        padding_y="1em",
                    )
                ),
            )
        ),
        variant="surface",
        size="3",
        width="100%",
    )

def local_repositories_box() -> rx.Component:
    """The local repositories box component."""
    return prbox(
        rx.vstack(
            rx.heading("Local Repositories", size="5"),
            rx.text("List of local repositories cloned into your local directory.", size="2"),
            local_repo_table(),
            width="100%",
            spacing="4",
        ),
    )