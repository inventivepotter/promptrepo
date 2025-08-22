import reflex as rx
from promptrepo.components import horizontal_stack, icon_link, layout, prbox
from promptrepo.states.settings_state import SettingsState


@rx.page()
def settings() -> rx.Component:
    return layout(
        prbox(
            rx.vstack(
                rx.heading("Settings", size="5"),
                rx.text("Configure your LLM providers below.", size="2"),
                provider_actions(),
                configured_providers_table(),
                width="100%",
                spacing="4",
            ),
        )
    )


def provider_actions() -> rx.Component:
    return rx.hstack(
        rx.select(
            SettingsState.unselected_providers,
            placeholder="Add a provider...",
            on_change=lambda value: SettingsState.add_provider(value),
            width="100%",
        ),
        width="100%",
    )


def configured_providers_table() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Provider"),
            )
        ),
        rx.table.body(
            rx.cond(
                SettingsState.selected_providers,
                rx.foreach(
                    SettingsState.selected_providers,
                    lambda provider: rx.table.row(
                        rx.table.cell(provider),
                    ),
                ),
                rx.table.row(
                    rx.table.cell(
                        "No providers configured. Please select a provider from the dropdown above to get started.",
                        col_span=1,
                        text_align="center",
                        padding_y="1em",
                    )
                ),
            )
        ),
        variant="surface",
        size="3",
    )