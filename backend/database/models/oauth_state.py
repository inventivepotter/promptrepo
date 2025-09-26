from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import JSON
from sqlmodel import SQLModel, Field

from schemas.oauth_provider_enum import OAuthProvider


class OAuthState(SQLModel, table=True):
    __tablename__ = "oauth_states" # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    state_token: str = Field(index=True, unique=True)
    provider: OAuthProvider
    redirect_uri: str
    scopes: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    meta_data: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    expires_at: datetime

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at