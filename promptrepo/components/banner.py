import reflex as rx
from promptrepo.auth.auth_state import AuthState
from promptrepo.components.branding import branding
from promptrepo.components.prbox import prbox

def banner() -> rx.Component:
        """Welcome banner for the Prompt Repository."""
        return prbox(
            rx.box(
                rx.color_mode.button(),
                position="absolute",
                top=25,
                right=25,
                z_index=100,
            ),
            rx.cond(
                AuthState.access_token,
                rx.vstack(
                    rx.heading(f"Hello {AuthState.user.name}!", size="6"),
                    rx.text("Welcome to the Prompt Repository!", size="3"),
                    #rx.text(f"email: {AuthState.user.email}, Avatar: {AuthState.user.avatar_url}, {AuthState.user.url}, {AuthState.user.login}, {AuthState.user.name}", size="3"),
                ),
                rx.vstack(
                    rx.heading("Hello there!", size="6"),
                    rx.text("Please login with GitHub to start prompting!", size="3"),
                ),
            ),
        )