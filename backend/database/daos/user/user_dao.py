"""
Session management service for User_Sessions database operations.
"""
from sqlmodel import Session, select
from database.models.user import User
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class UserDAO:
    """Service for managing user sessions in database."""

    def __init__(self, db: Session):
        """
        Initialize UserService with database session.

        Args:
            db: Database session
        """
        self.db = db

    def save_user(
            self,
            user_data: User
    ) -> User:
        """
        Create a new user or update an existing one in the database.
        If a user with the same oauth_username and oauth_provider exists, it will be updated.
        Otherwise, a new user will be created.

        Args:
            user_data: User object containing user details to save
        Returns:
            The saved User object (either created or updated)
        """
        try:
            # Check if user already exists by oauth_username and oauth_provider combination
            # TODO: Should we use oauth_user_id or oauth_username for uniqueness, given oauth_username can change?
            existing_user = self.db.exec(
                select(User).where(
                    (User.oauth_username == user_data.oauth_username) &
                    (User.oauth_provider == user_data.oauth_provider)
                )
            ).first()

            if existing_user:
                # Update existing user
                update_data = user_data.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    if hasattr(existing_user, key):
                        setattr(existing_user, key, value)
                    else:
                        logger.warning(f"Attempted to update non-existent field '{key}' for user {existing_user.id}")
                self.db.add(existing_user)
                self.db.commit()
                self.db.refresh(existing_user)
                logger.info(f"Updated user: {existing_user.oauth_username} ({existing_user.oauth_provider})")
                return existing_user
            else:
                # Create new user record
                self.db.add(user_data)
                self.db.commit()
                self.db.refresh(user_data)
                logger.info(f"Created user: {user_data.oauth_username} ({user_data.oauth_provider})")
                return user_data

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save user {user_data.oauth_username} ({user_data.oauth_provider}): {e}")
            raise

    def get_user_by_id(
        self,
        user_id: str
    ) -> Optional[User]:
        """
        Retrieve a user by their ID.

        Args:
            user_id: The ID of the user to retrieve
        Returns:
            User object if found, else None
        """
        try:
            user = self.db.get(User, user_id)
            if user:
                logger.info(f"Retrieved user by ID: {user_id}")
            else:
                logger.info(f"User not found by ID: {user_id}")
            return user
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            raise

    def get_user_by_username(
        self,
        oauth_username: str
    ) -> Optional[User]:
        """
        Retrieve a user by their oauth_username.
        Note: This method may return any user with the given oauth_username regardless of OAuth provider.
        Consider using get_user_by_username_and_provider() for more specific queries.

        Args:
            oauth_username: The oauth_username of the user to retrieve
        Returns:
            User object if found, else None
        """
        try:
            user = self.db.exec(
                select(User).where(User.oauth_username == oauth_username)
            ).first()
            if user:
                logger.info(f"Retrieved user by oauth_username: {oauth_username}")
            else:
                logger.info(f"User not found by oauth_username: {oauth_username}")
            return user
        except Exception as e:
            logger.error(f"Failed to get user by oauth_username {oauth_username}: {e}")
            raise

    def get_user_by_username_and_provider(
        self,
        oauth_username: str,
        oauth_provider: str
    ) -> Optional[User]:
        """
        Retrieve a user by their oauth_username and OAuth provider combination.

        Args:
            oauth_username: The oauth_username of the user to retrieve
            oauth_provider: The OAuth provider (e.g., 'github', 'gitlab')
        Returns:
            User object if found, else None
        """
        try:
            user = self.db.exec(
                select(User).where(
                    (User.oauth_username == oauth_username) &
                    (User.oauth_provider == oauth_provider)
                )
            ).first()
            if user:
                logger.info(f"Retrieved user by oauth_username and provider: {oauth_username} ({oauth_provider})")
            else:
                logger.info(f"User not found by oauth_username and provider: {oauth_username} ({oauth_provider})")
            return user
        except Exception as e:
            logger.error(f"Failed to get user by oauth_username and provider {oauth_username} ({oauth_provider}): {e}")
            raise

    def get_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """
        Retrieve a list of users.

        Args:
            skip: Number of users to skip for pagination
            limit: Maximum number of users to return
        Returns:
            List of User objects
        """
        try:
            users = list(self.db.exec(
                select(User).offset(skip).limit(limit)
            ).all())
            logger.info(f"Retrieved {len(users)} users")
            return users
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            raise


    def delete_user(
        self,
        user_id: str
    ) -> bool:
        """
        Delete a user from the database.

        Args:
            user_id: The ID of the user to delete
        Returns:
            True if user was deleted, False if user was not found
        """
        try:
            user = self.db.get(User, user_id)
            if not user:
                logger.info(f"User not found for deletion: {user_id}")
                return False

            self.db.delete(user)
            self.db.commit()
            logger.info(f"Deleted user: {user_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise
