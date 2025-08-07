import reflex as rx

from promptrepo.components import banner
from promptrepo.components.side_bar import side_bar

def layout(*children) -> rx.Component:
    """The main layout for the app."""
    return rx.box(
        #nav_bar(),
        rx.flex(
            rx.box(
                side_bar(),
              ),
            rx.box(
                banner(),
                *children,
                padding=20,
                width="100%",
                background=rx.color("gray", 2),
            ),
            height="100%",
        ),
        height="100vh",  # Use viewport height for full page height
    )