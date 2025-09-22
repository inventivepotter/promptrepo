"""
Session management service for UserSessions database operations.
"""
from sqlmodel import Session, select
from database.models.user_sessions import UserSessions
from database.models.user import User
from services.auth.models import OAuthTokenUserInfo
from datetime import datetime, timedelta, UTC
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing user sessions in database."""

    def __init__(self, db: Session):
        """
        Initialize SessionService with database session.
        
        Args:
            db: Database session instance
        """
        self.db = db

    def create_session(
            self,
            user_id: str,
            oauth_token: str,
            session_data: Optional[str] = None
    ) -> UserSessions:
        """
        Create a new user session in database.

        Args:
            user_id: User ID to link the session to
            oauth_token: OAuth access token
            session_data: Optional JSON string for additional session metadata

        Returns:
            Created UserSessions object
        """
        try:
            # Generate unique session ID
            session_id = UserSessions.generate_session_key()

            # Create new session record
            user_session = UserSessions(
                user_id=user_id,
                session_id=session_id,
                oauth_token=oauth_token,
                data=session_data
            )

            # Save to database
            self.db.add(user_session)
            self.db.commit()
            self.db.refresh(user_session)

            logger.info(f"Created session for user_id: {user_id}")
            return user_session

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create session for user_id {user_id}: {e}")
            raise

    def get_session_by_id(self, session_id: str) -> Optional[UserSessions]:
        """
        Get user session by session_id.

        Args:
            session_id: Session identifier

        Returns:
            UserSessions object if found, None otherwise
        """
        try:
            statement = select(UserSessions).where(UserSessions.session_id == session_id)
            return self.db.exec(statement).first()

        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    def get_sessions_by_user_id(self, user_id: str) -> list[UserSessions]:
        """
        Get all active sessions for a user.

        Args:
            user_id: User ID

        Returns:
            List of UserSessions objects
        """
        try:
            statement = select(UserSessions).where(UserSessions.user_id == user_id)
            return list(self.db.exec(statement).all())

        except Exception as e:
            logger.error(f"Failed to get sessions for user_id {user_id}: {e}")
            return []

    def update_session(
            self,
            session_id: str,
            oauth_token: Optional[str] = None,
            session_data: Optional[str] = None
    ) -> bool:
        """
        Update existing session.

        Args:
            session_id: Session identifier
            oauth_token: New OAuth token (optional)
            session_data: New session data (optional)

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            statement = select(UserSessions).where(UserSessions.session_id == session_id)
            user_session = self.db.exec(statement).first()

            if not user_session:
                logger.warning(f"Session not found: {session_id}")
                return False

            # Update fields if provided
            if oauth_token:
                user_session.oauth_token = oauth_token
            if session_data:
                user_session.data = session_data

            # Update accessed timestamp (should happen automatically)
            user_session.accessed_at = datetime.now(UTC)

            self.db.add(user_session)
            self.db.commit()

            logger.info(f"Updated session: {session_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update session {session_id}: {e}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a user session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            statement = select(UserSessions).where(UserSessions.session_id == session_id)
            user_session = self.db.exec(statement).first()

            if not user_session:
                logger.warning(f"Session not found for deletion: {session_id}")
                return False

            self.db.delete(user_session)
            self.db.commit()

            logger.info(f"Deleted session: {session_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    def delete_user_sessions(self, user_id: str) -> int:
        """
        Delete all sessions for a user (used for logout all).

        Args:
            user_id: User ID

        Returns:
            Number of sessions deleted
        """
        try:
            statement = select(UserSessions).where(UserSessions.user_id == user_id)
            sessions = self.db.exec(statement).all()

            count = 0
            for session in sessions:
                self.db.delete(session)
                count += 1

            self.db.commit()
            logger.info(f"Deleted {count} sessions for user_id: {user_id}")
            return count

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete sessions for user_id {user_id}: {e}")
            return 0

    def cleanup_expired_sessions(self, ttl_minutes: int = 1440) -> int:
        """
        Clean up expired sessions (older than TTL).

        Args:
            ttl_minutes: Time-to-live in minutes (default: 24 hours)

        Returns:
            Number of sessions deleted
        """
        try:
            ttl = timedelta(minutes=ttl_minutes)
            return UserSessions.delete_expired(self.db, ttl)

        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0

    def is_session_valid(self, session_id: str, ttl_minutes: int = 1440) -> bool:
        """
        Check if session is valid (exists and not expired).

        Args:
            session_id: Session identifier
            ttl_minutes: Time-to-live in minutes

        Returns:
            True if session is valid, False otherwise
        """
        try:
            user_session = self.get_session_by_id(session_id)

            if not user_session:
                return False

            # Check if session is expired
            ttl = timedelta(minutes=ttl_minutes)
            expiry_time = datetime.now(UTC) - ttl

            # Ensure both datetimes have timezone info for comparison
            accessed_at = user_session.accessed_at
            if accessed_at.tzinfo is None:
                # If accessed_at is naive, assume it's UTC
                accessed_at = accessed_at.replace(tzinfo=UTC)

            return accessed_at > expiry_time

        except Exception as e:
            logger.error(f"Failed to validate session {session_id}: {e}")
            return False

    def get_oauth_token_and_user_info(self, session_id: str) -> Optional[OAuthTokenUserInfo]:
        """
        Get OAuth token and user info by session_id using relationship.

        Args:
            session_id: Session identifier

        Returns:
            OAuthTokenUserInfo object if found, None otherwise
        """
        try:
            statement = select(UserSessions).where(UserSessions.session_id == session_id)
            user_session = self.db.exec(statement).first()

            if user_session:
                return OAuthTokenUserInfo(
                    oauth_token=user_session.oauth_token,
                    oauth_provider=user_session.user.oauth_provider,
                    user_id=user_session.user_id,
                    username=user_session.user.username,
                    name=user_session.user.name
                )
            return None

        except Exception as e:
            logger.error(f"Failed to get oauth token and user info for session {session_id}: {e}")
            return None

    def get_user_from_session(self, session_id: str) -> Optional[User]:
        """
        Get User object from session_id using relationship.

        Args:
            session_id: Session identifier

        Returns:
            User object if found, None otherwise
        """
        try:
            statement = select(UserSessions).where(UserSessions.session_id == session_id)
            user_session = self.db.exec(statement).first()

            if user_session:
                return user_session.user
            return None

        except Exception as e:
            logger.error(f"Failed to get user from session {session_id}: {e}")
            return None
