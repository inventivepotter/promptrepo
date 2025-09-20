"""
Session management service for User_Sessions database operations.
"""
from sqlmodel import Session, select
from models.user import User
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user sessions in database."""

    @staticmethod
    def save_user(
            db: Session,
            user_data: User
    ) -> User:
        """
        Create a new user or update an existing one in the database.
        If a user with the same username exists, it will be updated.
        Otherwise, a new user will be created.

        Args:
            db: Database session
            user_data: User object containing user details to save
        Returns:
            The saved User object (either created or updated)
        """
        try:
            # Check if user already exists by username
            existing_user = db.exec(
                select(User).where(User.username == user_data.username)
            ).first()

            if existing_user:
                # Update existing user
                update_data = user_data.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    if hasattr(existing_user, key):
                        setattr(existing_user, key, value)
                    else:
                        logger.warning(f"Attempted to update non-existent field '{key}' for user {existing_user.id}")
                db.add(existing_user)
                db.commit()
                db.refresh(existing_user)
                logger.info(f"Updated user: {existing_user.username}")
                return existing_user
            else:
                # Create new user record
                db.add(user_data)
                db.commit()
                db.refresh(user_data)
                logger.info(f"Created user: {user_data.username}")
                return user_data

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save user {user_data.username}: {e}")
            raise

    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: str
    ) -> Optional[User]:
        """
        Retrieve a user by their ID.

        Args:
            db: Database session
            user_id: The ID of the user to retrieve
        Returns:
            User object if found, else None
        """
        try:
            user = db.get(User, user_id)
            if user:
                logger.info(f"Retrieved user by ID: {user_id}")
            else:
                logger.info(f"User not found by ID: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            raise

    @staticmethod
    def get_user_by_username(
        db: Session,
        username: str
    ) -> Optional[User]:
        """
        Retrieve a user by their username.

        Args:
            db: Database session
            username: The username of the user to retrieve
        Returns:
            User object if found, else None
        """
        try:
            user = db.exec(
                select(User).where(User.username == username)
            ).first()
            if user:
                logger.info(f"Retrieved user by username: {username}")
            else:
                logger.info(f"User not found by username: {username}")
            return user
        except Exception as e:
            logger.error(f"Failed to get user by username {username}: {e}")
            raise

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Retrieve a list of users.

        Args:
            db: Database session
            skip: Number of users to skip for pagination
            limit: Maximum number of users to return
        Returns:
            List of User objects
        """
        try:
            users = list(db.exec(
                select(User).offset(skip).limit(limit)
            ).all())
            logger.info(f"Retrieved {len(users)} users")
            return users
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            raise


    @staticmethod
    def delete_user(
        db: Session,
        user_id: str
    ) -> bool:
        """
        Delete a user from the database.

        Args:
            db: Database session
            user_id: The ID of the user to delete
        Returns:
            True if user was deleted, False if user was not found
        """
        try:
            user = db.get(User, user_id)
            if not user:
                logger.info(f"User not found for deletion: {user_id}")
                return False

            db.delete(user)
            db.commit()
            logger.info(f"Deleted user: {user_id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise