import reflex as rx
from .auth.auth_state import AuthState

class State(rx.State):
    auth: AuthState