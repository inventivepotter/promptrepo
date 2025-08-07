import reflex as rx
from typing import Optional

class User(rx.Base):
    login: str
    name: str
    avatar_url: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None