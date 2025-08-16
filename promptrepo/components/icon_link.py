import reflex as rx

def icon_link(icon: str, size: int = 15, text: str = "", **kwargs) -> rx.Component:
    return rx.link(
        rx.icon(tag=icon, size=size),
        rx.text(text) if text else None,
        style={"cursor": "pointer"},
        **kwargs
    )