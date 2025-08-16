import reflex as rx
from promptrepo.states import AuthState
import promptrepo.states.prompts_state as PromptsState
from promptrepo.components import layout, prbox

@rx.page(on_load=[AuthState.authenticate, PromptsState.PromptsState.load_prompts_from_repos])
def prompts() -> rx.Component:
    return layout(
        prbox(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Name"),
                        rx.table.column_header_cell("Description"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        PromptsState.PromptsState.all_prompts,
                        lambda prompt: rx.table.row(
                            rx.table.cell(
                                rx.link(
                                    prompt.id,
                                    href=f"/editor/{prompt.id}",
                                    underline="always"
                                )
                            ),
                            rx.table.cell(prompt.description),
                        )
                    )
                ),
                variant="surface",
                size="3",
            )
        )
    )