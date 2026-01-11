"""
Service for managing shared chat functionality.
Handles business logic for creating and retrieving shared chats.
"""
from datetime import datetime, UTC
from typing import List, Optional
import logging

from database.daos.shared_chat import SharedChatDAO
from database.models.shared_chats import SharedChats
from schemas.shared_chat import (
    CreateSharedChatRequest,
    CreateSharedChatResponse,
    SharedChatResponse,
    SharedChatListItem,
    SharedChatMessage,
    SharedChatModelConfig,
)
from middlewares.rest import NotFoundException

logger = logging.getLogger(__name__)


class SharedChatService:
    """Service for shared chat operations."""

    def __init__(self, dao: SharedChatDAO, base_url: str = ""):
        """
        Initialize SharedChatService.

        Args:
            dao: SharedChatDAO instance
            base_url: Base URL for generating share links
        """
        self.dao = dao
        self.base_url = base_url

    def _generate_unique_share_id(self) -> str:
        """
        Generate a unique share ID that doesn't exist in the database.

        Returns:
            Unique share ID string
        """
        max_attempts = 10
        for _ in range(max_attempts):
            share_id = SharedChatDAO.generate_share_id()
            if not self.dao.share_id_exists(share_id):
                return share_id

        # Fallback: use longer ID if collisions occur
        return SharedChatDAO.generate_share_id(length=16)

    def create_shared_chat(
        self,
        request: CreateSharedChatRequest,
        user_id: Optional[str] = None
    ) -> CreateSharedChatResponse:
        """
        Create a new shared chat.

        Args:
            request: CreateSharedChatRequest with chat data
            user_id: Optional user ID who is creating the share

        Returns:
            CreateSharedChatResponse with share ID and URL
        """
        share_id = self._generate_unique_share_id()

        # Convert messages to dict for storage
        messages_data = [msg.model_dump(mode="json") for msg in request.messages]

        # Convert model config to dict
        model_config_dict = request.model_config_data.model_dump(mode="json")

        shared_chat = SharedChats(
            share_id=share_id,
            title=request.title,
            messages={"messages": messages_data},
            model_config_data=model_config_dict,
            prompt_meta=request.prompt_meta,
            total_tokens=request.total_tokens,
            total_cost=request.total_cost,
            created_by=user_id,
            created_at=datetime.now(UTC),
            is_active=True,
        )

        created = self.dao.create(shared_chat)

        share_url = f"{self.base_url}/shared/{created.share_id}"

        logger.info(
            f"Created shared chat",
            extra={
                "share_id": created.share_id,
                "user_id": user_id,
                "message_count": len(request.messages),
            }
        )

        return CreateSharedChatResponse(
            share_id=created.share_id,
            share_url=share_url
        )

    def get_shared_chat(self, share_id: str) -> SharedChatResponse:
        """
        Get a shared chat by its share ID.

        Args:
            share_id: The share identifier

        Returns:
            SharedChatResponse with chat data

        Raises:
            NotFoundException: If shared chat not found
        """
        shared_chat = self.dao.get_by_share_id(share_id)

        if not shared_chat:
            logger.warning(f"Shared chat not found: {share_id}")
            raise NotFoundException(
                resource="Shared chat",
                identifier=share_id
            )

        # Parse messages from stored JSON
        messages_data = shared_chat.messages.get("messages", [])
        messages = [SharedChatMessage(**msg) for msg in messages_data]

        # Parse model config
        model_config = SharedChatModelConfig(**shared_chat.model_config_data)

        return SharedChatResponse(
            id=shared_chat.id,
            share_id=shared_chat.share_id,
            title=shared_chat.title,
            messages=messages,
            model_config_data=model_config,
            prompt_meta=shared_chat.prompt_meta,
            total_tokens=shared_chat.total_tokens,
            total_cost=shared_chat.total_cost,
            created_at=shared_chat.created_at,
        )

    def list_user_shared_chats(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[SharedChatListItem]:
        """
        List all shared chats created by a user.

        Args:
            user_id: User ID
            limit: Maximum number of results
            offset: Number of records to skip

        Returns:
            List of SharedChatListItem
        """
        shared_chats = self.dao.get_by_user(user_id, limit, offset)

        items = []
        for chat in shared_chats:
            messages_data = chat.messages.get("messages", [])
            items.append(
                SharedChatListItem(
                    id=chat.id,
                    share_id=chat.share_id,
                    title=chat.title,
                    total_tokens=chat.total_tokens,
                    total_cost=chat.total_cost,
                    created_at=chat.created_at,
                    message_count=len(messages_data),
                )
            )

        return items

    def delete_shared_chat(self, share_id: str, user_id: str) -> bool:
        """
        Delete a shared chat (soft delete).

        Args:
            share_id: The share identifier
            user_id: User ID (must be owner)

        Returns:
            True if deleted successfully

        Raises:
            NotFoundException: If shared chat not found or not owned by user
        """
        success = self.dao.delete(share_id, user_id)

        if not success:
            raise NotFoundException(
                resource="Shared chat",
                identifier=share_id,
                context={"reason": "Not found or not owned by user"}
            )

        logger.info(
            f"Deleted shared chat",
            extra={"share_id": share_id, "user_id": user_id}
        )

        return True
