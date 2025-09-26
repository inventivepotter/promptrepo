from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from database.models import OAuthState


class OAuthStateDAO:
    def __init__(self, db: Session):
        self.session = db

    def save_state(self, state: OAuthState) -> OAuthState:
        self.session.add(state)
        self.session.commit()
        self.session.refresh(state)
        return state

    def get_state_by_token(self, state_token: str) -> Optional[OAuthState]:
        statement = select(OAuthState).where(OAuthState.state_token == state_token)
        result = self.session.exec(statement).first()
        return result

    def delete_state_by_token(self, state_token: str) -> bool:
        statement = select(OAuthState).where(OAuthState.state_token == state_token)
        state = self.session.exec(statement).first()
        if state:
            self.session.delete(state)
            self.session.commit()
            return True
        return False

    def cleanup_expired_states(self) -> int:
        statement = select(OAuthState).where(OAuthState.expires_at < datetime.utcnow())
        expired_states = self.session.exec(statement).all()
        count = len(expired_states)
        for state in expired_states:
            self.session.delete(state)
        self.session.commit()
        return count