import reflex as rx

def prbox(*children) -> rx.Component:
    """A styled box for the Prompt Repository."""
    return rx.box(
        *children,
        padding=20,
        background=rx.color("gray", 1),
        #background=["#A1F7D0"],
        border_radius=5,
        border=f"1px solid {rx.color('gray', 3)}",
        width="100%",
        margin_bottom=20,
    )