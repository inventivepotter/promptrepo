import reflex as rx

def horizontal_stack(left: rx.Component, right: rx.Component, **kwargs) -> rx.Component:
    return rx.hstack(
        rx.hstack(
            left,
            justify="start",
            width="50%",
        ),
        rx.hstack(
            right,
            justify="end",
            width="50%",
        ),
        width="100%",
        **kwargs
    )