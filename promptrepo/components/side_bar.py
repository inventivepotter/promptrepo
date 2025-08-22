from typing import Callable, Optional
import reflex as rx

import os
from dotenv import load_dotenv
from promptrepo.states.auth_state import AuthState
from promptrepo.components import branding, small_branding

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

class SideBar(rx.State):
    """State for the left navigation component."""
    is_collapsed: bool = False
    
    def toggle_nav(self) -> None:
        """Toggle the navigation between collapsed and expanded states."""
        self.is_collapsed = not self.is_collapsed

def side_bar() -> rx.Component:
    """Returns a left navigation component with menu items."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.cond(
                    SideBar.is_collapsed,
                    small_branding(),
                    branding()
                ),
                padding_bottom=20,
                padding_top=20,
                border_bottom=f"1px solid {rx.color('gray', 4)}",
                width="100%",
                justify="center",
            ),
            rx.vstack(
                side_bar_item("home", "Home", "/"),
                side_bar_item("book-copy", "Repos", "/repos"),
                side_bar_item("braces", "Prompts", "/prompts"),
                side_bar_item("settings", "Settings", "/settings"),
                width="100%",
            ),
            rx.vstack(
                rx.cond(
                    AuthState.access_token,
                    side_bar_item("log-out", "Logout", "/logout"),
                    side_bar_item("github", "Sign in with github", "/login"),
                ),
                side_bar_item("chevron-right", "Collapse", "", on_click=SideBar.toggle_nav),
                padding_top=0.75,
                border_top=f"1px solid {rx.color('gray', 4)}",
                width="100%",
            ),
            width=rx.cond(
                SideBar.is_collapsed,
                ["70px", "70px", "60px"],
                ["250px", "250px", "200px"]
            ),
            border_right=f"1px solid {rx.color('gray', 4)}",
            transition="all 0.3s ease",
            height="100%",
        ),
        height="100%",
        #ackground=rx.color('gray', 2),
    )



def side_bar_item(icon: str, text: str, href: str, on_click: Optional[Callable] = None) -> rx.Component:
    """Create a reusable sidebar item component.
    
    Args:
        icon: The name of the icon to display
        text: The text label for the navigation item
        href: The URL path for this navigation item
        on_click: The event handler for when the item is clicked
        
    Returns:
        A styled sidebar navigation component
    """
    return rx.link(
        rx.hstack(
            rx.cond(
                SideBar.is_collapsed,
                rx.icon(
                    icon,
                    size=16,
                    margin_top="2px",
                ),
                rx.icon(
                    icon if text != "Collapse" else "chevron-left",
                    size=16,
                    margin_top="2px",
                ),
            ),
            rx.cond(
                SideBar.is_collapsed == False,
                rx.text(
                    text,
                    size="2",
                ),
            ),
            height="12px",
        ),
        on_click=on_click,
        href=href,
        padding=20,
        margin_down=0,
    )
