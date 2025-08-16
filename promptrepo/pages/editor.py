import reflex as rx
from promptrepo.components import layout, prbox, horizontal_stack, icon_link
from promptrepo.states.prompt_editor_state import PromptEditorState
from promptrepo.states.prompts_state import PromptsState

@rx.page(route="/editor/[id]", on_load=[PromptEditorState.load_prompt])
def editor() -> rx.Component:
    prompt = PromptEditorState.current_prompt
    return layout(
        rx.cond(
            prompt != None,
            prompt_form(prompt),
            prbox(
                rx.text(f"Prompt '{PromptEditorState.prompt_id}' not found.")
            ),
        ),
    )

def prompt_form(prompt):
    return prbox(
        rx.box(
            rx.vstack(
                label("Name"),
                rx.input(
                    default_value=rx.cond(prompt.name != None, prompt.name, ""),
                    on_blur=lambda e: PromptEditorState.set_field("name", e),
                    width="100%",
                ),
                margin_bottom="1em"
            ),
            rx.vstack(
                rx.hstack(
                    label("Prompt"),
                    rx.hstack(
                        prompt_dialog(prompt),
                        icon_link("wand-sparkles", margin_top="0.25em"),
                        justify="end",
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.text_area(
                    default_value=rx.cond(prompt.prompt != None, prompt.prompt, ""),
                    on_blur=lambda e: PromptEditorState.set_field("prompt", e),
                    width="100%",
                    height="380px",
                ),
                # Dialog is now handled by dialog_root above
                margin_bottom="1em"
            ),
            rx.vstack(
                label("Model", width="120px"),
                rx.input(
                    default_value=rx.cond(prompt.model != None, prompt.model, ""),
                    on_blur=lambda e: PromptEditorState.set_field("model", e),
                    width="100%",
                ),
                margin_bottom="1em"
            ),
            rx.vstack(
                label("Description", width="120px"),
                rx.text_area(
                    default_value=rx.cond(prompt.description != None, prompt.description, ""),
                    on_blur=lambda e: PromptEditorState.set_field("description", e),
                    width="100%",
                    height="auto"
                ),
                margin_bottom="1em"
            ),
            width="100%"
        ),
    )

def prompt_dialog(prompt) -> rx.Component:
    return rx.dialog.root(
    rx.dialog.trigger(
        icon_link("file-chart-column-increasing", margin_top="0.25em"),
    ),
    rx.dialog.content(
        horizontal_stack(
            rx.text(
                f"{prompt.name} Prompt Markdown",
                font_weight="bold",
            ),
            rx.dialog.close(
                icon_link("x", margin_top="0.25em"),
            ),
            margin_bottom="1em",
        ),
        rx.scroll_area(
            rx.markdown(rx.cond(prompt.prompt != None, prompt.prompt, "")),
            type="always",
            scrollbars="vertical",
            height="80vh",
        ),
    ),
)

def label(text, **kwargs):
    return rx.text(
        text,
        margin_bottom="0",
        padding_bottom="0",
        font_weight="500",
        margin_top="0.5em",
        size='1',
        **kwargs
    )