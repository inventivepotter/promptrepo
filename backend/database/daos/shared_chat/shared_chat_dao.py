"""
Data Access Object for shared chat operations.
Handles database operations for the shared_chats table.
"""
from sqlmodel import Session, select
from database.models.shared_chats import SharedChats
from typing import Optional, List
import logging
import secrets
import string

logger = logging.getLogger(__name__)


class SharedChatDAO:
    """DAO for managing shared chat records."""

    def __init__(self, db: Session):
        """
        Initialize SharedChatDAO with database session.

        Args:
            db: Database session
        """
        self.db = db

    @staticmethod
    def generate_share_id(length: int = 12) -> str:
        """
        Generate a unique, URL-safe share ID.

        Args:
            length: Length of the share ID

        Returns:
            URL-safe random string
        """
        alphabet = string.ascii_lowercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def create(self, shared_chat: SharedChats) -> SharedChats:
        """
        Create a new shared chat record.

        Args:
            shared_chat: SharedChats object to create

        Returns:
            Created SharedChats object
        """
        try:
            self.db.add(shared_chat)
            self.db.commit()
            self.db.refresh(shared_chat)

            logger.info(f"Created shared chat: {shared_chat.share_id}")
            return shared_chat

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create shared chat: {e}")
            raise

    def get_by_share_id(self, share_id: str) -> Optional[SharedChats]:
        """
        Get shared chat by share_id.

        Args:
            share_id: The share identifier

        Returns:
            SharedChats object if found, None otherwise
        """
        try:
            statement = select(SharedChats).where(
                SharedChats.share_id == share_id,
                SharedChats.is_active == True
            )
            return self.db.exec(statement).first()

        except Exception as e:
            logger.error(f"Failed to get shared chat {share_id}: {e}")
            return None

    def get_by_id(self, id: str) -> Optional[SharedChats]:
        """
        Get shared chat by primary key ID.

        Args:
            id: The database ID

        Returns:
            SharedChats object if found, None otherwise
        """
        try:
            statement = select(SharedChats).where(
                SharedChats.id == id,
                SharedChats.is_active == True
            )
            return self.db.exec(statement).first()

        except Exception as e:
            logger.error(f"Failed to get shared chat by id {id}: {e}")
            return None

    def get_by_user(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[SharedChats]:
        """
        Get all shared chats created by a user.

        Args:
            user_id: User ID
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of SharedChats objects
        """
        try:
            statement = (
                select(SharedChats)
                .where(
                    SharedChats.created_by == user_id,
                    SharedChats.is_active == True
                )
                .order_by(SharedChats.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            return list(self.db.exec(statement).all())

        except Exception as e:
            logger.error(f"Failed to get shared chats for user {user_id}: {e}")
            return []

    def delete(self, share_id: str, user_id: str) -> bool:
        """
        Soft delete a shared chat (only if owned by user).

        Args:
            share_id: The share identifier
            user_id: User ID (must be owner)

        Returns:
            True if deleted, False otherwise
        """
        try:
            statement = select(SharedChats).where(
                SharedChats.share_id == share_id,
                SharedChats.created_by == user_id,
                SharedChats.is_active == True
            )
            shared_chat = self.db.exec(statement).first()

            if not shared_chat:
                logger.warning(
                    f"Shared chat not found or not owned: {share_id}"
                )
                return False

            shared_chat.is_active = False
            self.db.add(shared_chat)
            self.db.commit()

            logger.info(f"Deleted shared chat: {share_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete shared chat {share_id}: {e}")
            return False

    def share_id_exists(self, share_id: str) -> bool:
        """
        Check if a share_id already exists.

        Args:
            share_id: The share identifier to check

        Returns:
            True if exists, False otherwise
        """
        try:
            statement = select(SharedChats).where(
                SharedChats.share_id == share_id
            )
            return self.db.exec(statement).first() is not None

        except Exception as e:
            logger.error(f"Failed to check share_id existence: {e}")
            return True  # Assume exists on error to be safe
