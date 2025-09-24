"""
Service for managing user sessions in the database.
Handles data access operations for the user_sessions table.
"""
from sqlmodel import Session, select
from database.models.user_sessions import UserSessions
from datetime import datetime, timedelta, UTC
from typing import Optional, List
import logging
import uuid

logger = logging.getLogger(__name__)


class UserSessionDAO:
    """Service for managing user sessions."""

    def __init__(self, db: Session):
        """
        Initialize UserSessionDAO with database session.

        Args:
            db: Database session
        """
        self.db = db

    @staticmethod
    def generate_session_key() -> str:
        """Generate a secure random session key"""
        return str(uuid.uuid4()).replace("-", "")

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
            session_id = UserSessionDAO.generate_session_key()

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

    def get_sessions_by_user_id(self, user_id: str) -> List[UserSessions]:
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

    def get_active_session(self, user_id: str) -> Optional[UserSessions]:
        """
        Get the most recently accessed session for a user.

        Args:
            user_id: User ID

        Returns:
            UserSessions object if found, None otherwise
        """
        try:
            sessions = self.get_sessions_by_user_id(user_id)
            if not sessions:
                return None
            return max(sessions, key=lambda s: s.accessed_at)
        except Exception as e:
            logger.error(f"Failed to get active session for user_id {user_id}: {e}")
            return None

    def delete_expired(self, ttl: timedelta) -> int:
        """
        Delete sessions older than the given TTL.

        Args:
            ttl: timedelta after which sessions are considered expired
        
        Returns:
            Number of deleted sessions
        """
        try:
            expiration_time = datetime.now(UTC) - ttl
            statement = select(UserSessions).where(UserSessions.accessed_at < expiration_time)
            expired_sessions = self.db.exec(statement).all()
            
            count = len(expired_sessions)
            for session in expired_sessions:
                self.db.delete(session)
            
            self.db.commit()
            logger.info(f"Deleted {count} expired sessions.")
            return count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete expired sessions: {e}")
            raise

    def is_expired(self, session: UserSessions, ttl_seconds: int) -> bool:
        """
        Check if the session is expired based on the time-to-live (TTL).

        Args:
            session: The UserSessions object to check.
            ttl_seconds: Time-to-live in seconds.

        Returns:
            True if the session is expired, False otherwise.
        """
        try:
            expiration_time = datetime.now(UTC) - timedelta(seconds=ttl_seconds)
            
            # Ensure both datetimes have timezone info for comparison
            accessed_at = session.accessed_at
            if accessed_at.tzinfo is None:
                # If accessed_at is naive, assume it's UTC
                accessed_at = accessed_at.replace(tzinfo=UTC)
            
            return accessed_at < expiration_time
        except Exception as e:
            logger.error(f"Failed to check session expiration for session {session.id}: {e}")
            # Default to true (expired) on error to be safe
            return True