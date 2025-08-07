from typing_extensions import Literal
import reflex as rx

def branding(font_size: str = "24px") -> rx.Component:
    """Returns a branding component with logo and app name.
    
    Args:
        font_size: The font size for the logo text. Defaults to "24px".
    """
    return rx.hstack(
        #rx.image(src="/static/logo.png", height="40px"),
        rx.text("{Prompt}", font_size=font_size, font_weight="light"),
        rx.text("Repo", font_size=font_size, font_weight="bold"),
        spacing="1",
    )

def small_branding(font_size: str = "24px") -> rx.Component:
    """Returns a smaller branding component for compact views."""
    return rx.hstack(
        #rx.image(src="/static/logo.png", height="24px"),
        rx.text("{P", font_size=font_size, font_weight="light"),
        rx.text("R", font_size=font_size, font_weight="bold"),
        rx.text("}", font_size=font_size, font_weight="light"),
        spacing="0",
    )