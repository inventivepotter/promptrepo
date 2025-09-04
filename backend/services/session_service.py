"""
Session management service for User_Sessions database operations.
"""
from sqlmodel import Session, select
from models.user_sessions import User_Sessions
from datetime import datetime, timedelta, UTC
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing user sessions in database."""

    @staticmethod
    def create_session(
            db: Session,
            username: str,
            oauth_token: str,
            session_data: Optional[str] = None
    ) -> User_Sessions:
        """
        Create a new user session in database.

        Args:
            db: Database session
            username: GitHub username
            oauth_token: GitHub OAuth access token
            session_data: Optional JSON string for additional session metadata

        Returns:
            Created User_Sessions object
        """
        try:
            # Generate unique session ID
            session_id = User_Sessions.generate_session_key()

            # Create new session record
            user_session = User_Sessions(
                username=username,
                session_id=session_id,
                oauth_token=oauth_token,
                data=session_data
            )

            # Save to database
            db.add(user_session)
            db.commit()
            db.refresh(user_session)

            logger.info(f"Created session for user: {username}")
            return user_session

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create session for {username}: {e}")
            raise

    @staticmethod
    def get_session_by_id(db: Session, session_id: str) -> Optional[User_Sessions]:
        """
        Get user session by session_id.

        Args:
            db: Database session
            session_id: Session identifier

        Returns:
            User_Sessions object if found, None otherwise
        """
        try:
            statement = select(User_Sessions).where(User_Sessions.session_id == session_id)
            return db.exec(statement).first()

        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    @staticmethod
    def get_sessions_by_username(db: Session, username: str) -> list[User_Sessions]:
        """
        Get all active sessions for a user.

        Args:
            db: Database session
            username: GitHub username

        Returns:
            List of User_Sessions objects
        """
        try:
            statement = select(User_Sessions).where(User_Sessions.username == username)
            return list(db.exec(statement).all())

        except Exception as e:
            logger.error(f"Failed to get sessions for {username}: {e}")
            return []

    @staticmethod
    def update_session(
            db: Session,
            session_id: str,
            oauth_token: Optional[str] = None,
            session_data: Optional[str] = None
    ) -> bool:
        """
        Update existing session.

        Args:
            db: Database session
            session_id: Session identifier
            oauth_token: New OAuth token (optional)
            session_data: New session data (optional)

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            statement = select(User_Sessions).where(User_Sessions.session_id == session_id)
            user_session = db.exec(statement).first()

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

            db.add(user_session)
            db.commit()

            logger.info(f"Updated session: {session_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update session {session_id}: {e}")
            return False

    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        """
        Delete a user session.

        Args:
            db: Database session
            session_id: Session identifier

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            statement = select(User_Sessions).where(User_Sessions.session_id == session_id)
            user_session = db.exec(statement).first()

            if not user_session:
                logger.warning(f"Session not found for deletion: {session_id}")
                return False

            db.delete(user_session)
            db.commit()

            logger.info(f"Deleted session: {session_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    @staticmethod
    def delete_user_sessions(db: Session, username: str) -> int:
        """
        Delete all sessions for a user (used for logout all).

        Args:
            db: Database session
            username: GitHub username

        Returns:
            Number of sessions deleted
        """
        try:
            statement = select(User_Sessions).where(User_Sessions.username == username)
            sessions = db.exec(statement).all()

            count = 0
            for session in sessions:
                db.delete(session)
                count += 1

            db.commit()
            logger.info(f"Deleted {count} sessions for user: {username}")
            return count

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete sessions for {username}: {e}")
            return 0

    @staticmethod
    def cleanup_expired_sessions(db: Session, ttl_minutes: int = 1440) -> int:
        """
        Clean up expired sessions (older than TTL).

        Args:
            db: Database session
            ttl_minutes: Time-to-live in minutes (default: 24 hours)

        Returns:
            Number of sessions deleted
        """
        try:
            ttl = timedelta(minutes=ttl_minutes)
            return User_Sessions.delete_expired(db, ttl)

        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0

    @staticmethod
    def is_session_valid(db: Session, session_id: str, ttl_minutes: int = 1440) -> bool:
        """
        Check if session is valid (exists and not expired).

        Args:
            db: Database session
            session_id: Session identifier
            ttl_minutes: Time-to-live in minutes

        Returns:
            True if session is valid, False otherwise
        """
        try:
            user_session = SessionService.get_session_by_id(db, session_id)

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

    @staticmethod
    def get_oauth_token_and_username(db: Session, session_id: str) -> Optional[dict]:
        """
        Get OAuth token and username by session_id.

        Args:
            db: Database session
            session_id: Session identifier

        Returns:
            Dict with 'oauth_token' and 'username' keys if found, None otherwise
        """
        try:
            statement = select(User_Sessions).where(User_Sessions.session_id == session_id)
            user_session = db.exec(statement).first()

            if user_session:
                return {
                    'oauth_token': user_session.oauth_token,
                    'username': user_session.username
                }
            return None

        except Exception as e:
            logger.error(f"Failed to get oauth token and username for session {session_id}: {e}")
            return None
