import reflex as rx
from promptrepo.states import RepoState, AuthState
from promptrepo.components import layout, prbox

@rx.page(on_load=RepoState.get_repos)
def repos() -> rx.Component:
    return rx.cond(
        AuthState.is_authenticated,
        layout(
            prbox(
                rx.vstack(
                    rx.text("Select the repos you want to work with in PromptRepo."),
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell(""),
                                rx.table.column_header_cell("Name"),
                                rx.table.column_header_cell("Description"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                RepoState.repos,
                                lambda repo: rx.table.row(
                                    rx.table.cell(
                                        rx.checkbox(
                                            is_checked=RepoState.is_repo_selected(repo),
                                            on_change=RepoState.select_repo(repo),
                                        )
                                    ),
                                    rx.table.cell(
                                        rx.link(
                                            repo["name"],
                                            href=repo["html_url"],
                                            is_external=True,
                                        )
                                    ),
                                    rx.table.cell(repo["description"]),
                                ),
                            )
                        ),
                        variant="surface",
                        size="3",
                    ),
                    width="100%",
                ),
            )
        ),
        rx.center(
            rx.text("You must be logged in to view this page."),
        ),
    )