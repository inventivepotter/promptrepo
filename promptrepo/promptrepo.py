"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
from promptrepo.auth.auth_state import AuthState
from promptrepo.pages.index import index
from promptrepo.pages.app import app_page


app = rx.App()

# Frontend
app.add_page(index)
app.add_page(app_page, route="/app")
app.add_page(rx.box(
    rx.text("Authenticating with GitHub. Will be redirecting to Prompt Repo shortly..."),
), route="/login", on_load=AuthState.login)
app.add_page(rx.box(
    rx.text("Authenticating with GitHub. Will be redirecting to Prompt Repo shortly..."),
), route="/callback", on_load=AuthState.callback)

# Backend
