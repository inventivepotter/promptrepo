"""
Session management service for User_Sessions database operations.
"""
from sqlmodel import Session, select
from models.user import User
from models.user_sessions import UserSessions
from datetime import datetime, timedelta, UTC
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user sessions in database."""

    @staticmethod
    def create_user(
            db: Session,
            user: User
    ) -> User:
        """
        Create a new user in database.

        Args:
            db: Database session
            user: User object containing user details
        Returns:
            Created User object
        """
        try:
            # Check if user already exists
            existing_user = db.exec(
                select(User).where(User.username == user.username)
            ).first()
            if existing_user:
                logger.info(f"User already exists: {user.username}")
                return existing_user

            # Create new user record
            db.add(user)
            db.commit()
            db.refresh(user)

            logger.info(f"Created user: {user.username}")
            return user

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create user {user.username}: {e}")
            raise