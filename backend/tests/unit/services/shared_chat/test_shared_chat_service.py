"""
Unit tests for SharedChatService.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, UTC

from services.shared_chat import SharedChatService
from database.daos.shared_chat import SharedChatDAO
from database.models.shared_chats import SharedChats
from schemas.shared_chat import (
    CreateSharedChatRequest,
    SharedChatMessage,
    SharedChatModelConfig,
    SharedChatTokenUsage,
)
from middlewares.rest import NotFoundException


class TestSharedChatService:
    """Test cases for SharedChatService."""

    @pytest.fixture
    def mock_dao(self):
        """Create a mock DAO."""
        return Mock(spec=SharedChatDAO)

    @pytest.fixture
    def service(self, mock_dao):
        """Create service instance with mock DAO."""
        return SharedChatService(dao=mock_dao, base_url="https://example.com")

    @pytest.fixture
    def sample_messages(self):
        """Create sample messages for testing."""
        return [
            SharedChatMessage(
                id="msg_1",
                role="user",
                content="Hello, how are you?",
                timestamp=datetime.now(UTC),
            ),
            SharedChatMessage(
                id="msg_2",
                role="assistant",
                content="I'm doing well, thank you!",
                timestamp=datetime.now(UTC),
                usage=SharedChatTokenUsage(
                    prompt_tokens=10,
                    completion_tokens=8,
                    total_tokens=18,
                ),
                cost=0.001,
                inference_time_ms=250.0,
            ),
        ]

    @pytest.fixture
    def sample_model_config(self):
        """Create sample model config for testing."""
        return SharedChatModelConfig(
            provider="openai",
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000,
        )

    @pytest.fixture
    def sample_request(self, sample_messages, sample_model_config):
        """Create sample create request."""
        return CreateSharedChatRequest(
            title="Test Chat",
            messages=sample_messages,
            model_config_data=sample_model_config,
            total_tokens=18,
            total_cost=0.001,
        )

    def test_init(self, mock_dao):
        """Test SharedChatService initialization."""
        service = SharedChatService(dao=mock_dao, base_url="https://test.com")
        assert service.dao == mock_dao
        assert service.base_url == "https://test.com"

    def test_generate_unique_share_id(self, service, mock_dao):
        """Test generating a unique share ID."""
        mock_dao.share_id_exists.return_value = False

        share_id = service._generate_unique_share_id()

        assert len(share_id) == 12
        assert share_id.isalnum()
        mock_dao.share_id_exists.assert_called_once()

    def test_generate_unique_share_id_with_collision(self, service, mock_dao):
        """Test generating share ID with initial collisions."""
        # First call returns True (collision), second returns False
        mock_dao.share_id_exists.side_effect = [True, True, False]

        share_id = service._generate_unique_share_id()

        assert len(share_id) == 12
        assert mock_dao.share_id_exists.call_count == 3

    def test_create_shared_chat_success(self, service, mock_dao, sample_request):
        """Test successfully creating a shared chat."""
        mock_dao.share_id_exists.return_value = False

        mock_created = Mock(spec=SharedChats)
        mock_created.share_id = "abc123xyz456"
        mock_dao.create.return_value = mock_created

        result = service.create_shared_chat(sample_request, user_id="user_123")

        assert result.share_id == "abc123xyz456"
        assert result.share_url == "https://example.com/shared/abc123xyz456"
        mock_dao.create.assert_called_once()

        # Verify the created model
        created_arg = mock_dao.create.call_args[0][0]
        assert created_arg.title == "Test Chat"
        assert created_arg.total_tokens == 18
        assert created_arg.total_cost == 0.001
        assert created_arg.created_by == "user_123"

    def test_create_shared_chat_without_user(self, service, mock_dao, sample_request):
        """Test creating a shared chat without user ID."""
        mock_dao.share_id_exists.return_value = False

        mock_created = Mock(spec=SharedChats)
        mock_created.share_id = "abc123xyz456"
        mock_dao.create.return_value = mock_created

        result = service.create_shared_chat(sample_request, user_id=None)

        assert result.share_id == "abc123xyz456"

        created_arg = mock_dao.create.call_args[0][0]
        assert created_arg.created_by is None

    def test_get_shared_chat_success(self, service, mock_dao, sample_messages, sample_model_config):
        """Test successfully getting a shared chat."""
        mock_chat = Mock(spec=SharedChats)
        mock_chat.id = "chat_id_123"
        mock_chat.share_id = "abc123xyz456"
        mock_chat.title = "Test Chat"
        mock_chat.messages = {
            "messages": [msg.model_dump(mode="json") for msg in sample_messages]
        }
        mock_chat.model_config_data = sample_model_config.model_dump(mode="json")
        mock_chat.prompt_meta = None
        mock_chat.total_tokens = 18
        mock_chat.total_cost = 0.001
        mock_chat.created_at = datetime.now(UTC)

        mock_dao.get_by_share_id.return_value = mock_chat

        result = service.get_shared_chat("abc123xyz456")

        assert result.id == "chat_id_123"
        assert result.share_id == "abc123xyz456"
        assert result.title == "Test Chat"
        assert len(result.messages) == 2
        assert result.model_config_data.provider == "openai"
        assert result.model_config_data.model == "gpt-4"
        mock_dao.get_by_share_id.assert_called_once_with("abc123xyz456")

    def test_get_shared_chat_not_found(self, service, mock_dao):
        """Test getting a non-existent shared chat."""
        mock_dao.get_by_share_id.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            service.get_shared_chat("nonexistent")

        assert "nonexistent" in str(exc_info.value.message)

    def test_list_user_shared_chats_success(self, service, mock_dao):
        """Test listing user's shared chats."""
        mock_chat1 = Mock(spec=SharedChats)
        mock_chat1.id = "chat_1"
        mock_chat1.share_id = "share_1"
        mock_chat1.title = "Chat 1"
        mock_chat1.total_tokens = 100
        mock_chat1.total_cost = 0.01
        mock_chat1.created_at = datetime.now(UTC)
        mock_chat1.messages = {"messages": [{"id": "1"}, {"id": "2"}]}

        mock_chat2 = Mock(spec=SharedChats)
        mock_chat2.id = "chat_2"
        mock_chat2.share_id = "share_2"
        mock_chat2.title = "Chat 2"
        mock_chat2.total_tokens = 200
        mock_chat2.total_cost = 0.02
        mock_chat2.created_at = datetime.now(UTC)
        mock_chat2.messages = {"messages": [{"id": "3"}]}

        mock_dao.get_by_user.return_value = [mock_chat1, mock_chat2]

        result = service.list_user_shared_chats("user_123", limit=50, offset=0)

        assert len(result) == 2
        assert result[0].share_id == "share_1"
        assert result[0].message_count == 2
        assert result[1].share_id == "share_2"
        assert result[1].message_count == 1
        mock_dao.get_by_user.assert_called_once_with("user_123", 50, 0)

    def test_list_user_shared_chats_empty(self, service, mock_dao):
        """Test listing shared chats when user has none."""
        mock_dao.get_by_user.return_value = []

        result = service.list_user_shared_chats("user_123")

        assert result == []

    def test_delete_shared_chat_success(self, service, mock_dao):
        """Test successfully deleting a shared chat."""
        mock_dao.delete.return_value = True

        result = service.delete_shared_chat("abc123", "user_123")

        assert result is True
        mock_dao.delete.assert_called_once_with("abc123", "user_123")

    def test_delete_shared_chat_not_found(self, service, mock_dao):
        """Test deleting a non-existent or unauthorized shared chat."""
        mock_dao.delete.return_value = False

        with pytest.raises(NotFoundException) as exc_info:
            service.delete_shared_chat("nonexistent", "user_123")

        assert "nonexistent" in str(exc_info.value.message)


class TestSharedChatDAO:
    """Test cases for SharedChatDAO."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()

    @pytest.fixture
    def dao(self, mock_db):
        """Create DAO instance with mock database."""
        return SharedChatDAO(mock_db)

    def test_generate_share_id(self):
        """Test share ID generation."""
        share_id = SharedChatDAO.generate_share_id()

        assert len(share_id) == 12
        assert share_id.isalnum()
        assert share_id.islower() or any(c.isdigit() for c in share_id)

    def test_generate_share_id_custom_length(self):
        """Test share ID generation with custom length."""
        share_id = SharedChatDAO.generate_share_id(length=20)

        assert len(share_id) == 20

    def test_create_success(self, dao, mock_db):
        """Test creating a shared chat."""
        shared_chat = Mock(spec=SharedChats)
        shared_chat.share_id = "test_share_id"

        result = dao.create(shared_chat)

        assert result == shared_chat
        mock_db.add.assert_called_once_with(shared_chat)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(shared_chat)

    def test_create_failure_rollback(self, dao, mock_db):
        """Test rollback on create failure."""
        shared_chat = Mock(spec=SharedChats)
        mock_db.commit.side_effect = Exception("DB Error")

        with pytest.raises(Exception):
            dao.create(shared_chat)

        mock_db.rollback.assert_called_once()

    def test_get_by_share_id_found(self, dao, mock_db):
        """Test getting shared chat by share_id."""
        mock_chat = Mock(spec=SharedChats)
        mock_exec = Mock()
        mock_exec.first.return_value = mock_chat
        mock_db.exec.return_value = mock_exec

        result = dao.get_by_share_id("test_share_id")

        assert result == mock_chat
        mock_db.exec.assert_called_once()

    def test_get_by_share_id_not_found(self, dao, mock_db):
        """Test getting non-existent shared chat."""
        mock_exec = Mock()
        mock_exec.first.return_value = None
        mock_db.exec.return_value = mock_exec

        result = dao.get_by_share_id("nonexistent")

        assert result is None

    def test_delete_success(self, dao, mock_db):
        """Test soft deleting a shared chat."""
        mock_chat = Mock(spec=SharedChats)
        mock_chat.is_active = True
        mock_exec = Mock()
        mock_exec.first.return_value = mock_chat
        mock_db.exec.return_value = mock_exec

        result = dao.delete("test_share_id", "user_123")

        assert result is True
        assert mock_chat.is_active is False
        mock_db.add.assert_called_once_with(mock_chat)
        mock_db.commit.assert_called_once()

    def test_delete_not_found(self, dao, mock_db):
        """Test deleting non-existent shared chat."""
        mock_exec = Mock()
        mock_exec.first.return_value = None
        mock_db.exec.return_value = mock_exec

        result = dao.delete("nonexistent", "user_123")

        assert result is False
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()

    def test_share_id_exists_true(self, dao, mock_db):
        """Test checking if share_id exists (true case)."""
        mock_exec = Mock()
        mock_exec.first.return_value = Mock(spec=SharedChats)
        mock_db.exec.return_value = mock_exec

        result = dao.share_id_exists("existing_id")

        assert result is True

    def test_share_id_exists_false(self, dao, mock_db):
        """Test checking if share_id exists (false case)."""
        mock_exec = Mock()
        mock_exec.first.return_value = None
        mock_db.exec.return_value = mock_exec

        result = dao.share_id_exists("new_id")

        assert result is False
