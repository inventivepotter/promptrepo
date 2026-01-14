"""
Tests for conversational service models.
"""

import pytest
from pydantic import ValidationError

from services.conversational.models import (
    SimulateConversationRequest,
    SimulateConversationResponse,
)
from services.artifacts.evals.models import (
    Turn,
    TurnRole,
    TestType,
    ConversationalTestConfig,
    TestDefinition,
)


class TestTurnModel:
    """Tests for Turn model."""

    def test_create_user_turn(self):
        """Should create a user turn with content."""
        turn = Turn(role=TurnRole.USER, content="Hello, I need help.")
        assert turn.role == TurnRole.USER
        assert turn.content == "Hello, I need help."
        assert turn.retrieval_context is None
        assert turn.tools_called is None

    def test_create_assistant_turn(self):
        """Should create an assistant turn with content."""
        turn = Turn(role=TurnRole.ASSISTANT, content="Hello! How can I help?")
        assert turn.role == TurnRole.ASSISTANT
        assert turn.content == "Hello! How can I help?"

    def test_turn_with_retrieval_context(self):
        """Should create a turn with retrieval context."""
        turn = Turn(
            role=TurnRole.ASSISTANT,
            content="Based on our records...",
            retrieval_context=["Order #12345 was shipped yesterday."]
        )
        assert turn.retrieval_context == ["Order #12345 was shipped yesterday."]

    def test_turn_with_tools_called(self):
        """Should create a turn with tools called."""
        turn = Turn(
            role=TurnRole.ASSISTANT,
            content="I found your order.",
            tools_called=[{"name": "lookup_order", "args": {"order_id": "12345"}}]
        )
        assert turn.tools_called == [{"name": "lookup_order", "args": {"order_id": "12345"}}]


class TestTestType:
    """Tests for TestType enum."""

    def test_single_turn_value(self):
        """Should have correct single_turn value."""
        assert TestType.SINGLE_TURN.value == "single_turn"

    def test_conversational_value(self):
        """Should have correct conversational value."""
        assert TestType.CONVERSATIONAL.value == "conversational"


class TestConversationalTestConfig:
    """Tests for ConversationalTestConfig model."""

    def test_create_minimal_config(self):
        """Should create config with defaults."""
        config = ConversationalTestConfig()
        assert config.min_turns == 3
        assert config.max_turns == 6
        assert config.user_goal is None

    def test_create_full_config(self):
        """Should create config with all fields."""
        config = ConversationalTestConfig(
            user_goal="Get help with a refund",
            user_persona="Frustrated customer",
            min_turns=2,
            max_turns=10,
            stopping_criteria="When refund is processed",
            expected_outcome="Customer receives refund confirmation",
            chatbot_role="Customer support agent"
        )
        assert config.user_goal == "Get help with a refund"
        assert config.user_persona == "Frustrated customer"
        assert config.min_turns == 2
        assert config.max_turns == 10

    def test_min_turns_validation(self):
        """Should validate min_turns bounds."""
        with pytest.raises(ValidationError):
            ConversationalTestConfig(min_turns=0)

        with pytest.raises(ValidationError):
            ConversationalTestConfig(min_turns=25)

    def test_max_turns_validation(self):
        """Should validate max_turns bounds."""
        with pytest.raises(ValidationError):
            ConversationalTestConfig(max_turns=0)

        with pytest.raises(ValidationError):
            ConversationalTestConfig(max_turns=25)


class TestTestDefinition:
    """Tests for TestDefinition with conversational fields."""

    def test_single_turn_test_definition(self):
        """Should create single-turn test definition."""
        test = TestDefinition(
            name="test-single-turn",
            prompt_reference="file:///.promptrepo/prompts/test.yaml",
            user_message="Hello",
            test_type=TestType.SINGLE_TURN,
        )
        assert test.test_type == TestType.SINGLE_TURN
        assert test.turns is None
        assert test.conversational_config is None

    def test_conversational_test_with_turns(self):
        """Should create conversational test with predefined turns."""
        turns = [
            Turn(role=TurnRole.USER, content="Hi"),
            Turn(role=TurnRole.ASSISTANT, content="Hello!"),
        ]
        test = TestDefinition(
            name="test-conversational",
            prompt_reference="file:///.promptrepo/prompts/test.yaml",
            test_type=TestType.CONVERSATIONAL,
            turns=turns,
        )
        assert test.test_type == TestType.CONVERSATIONAL
        assert len(test.turns) == 2
        assert test.turns[0].role == TurnRole.USER

    def test_conversational_test_with_config(self):
        """Should create conversational test with config for simulation."""
        config = ConversationalTestConfig(
            user_goal="Get a refund",
            min_turns=3,
            max_turns=6,
        )
        test = TestDefinition(
            name="test-simulation",
            prompt_reference="file:///.promptrepo/prompts/test.yaml",
            test_type=TestType.CONVERSATIONAL,
            conversational_config=config,
        )
        assert test.test_type == TestType.CONVERSATIONAL
        assert test.conversational_config.user_goal == "Get a refund"

    def test_conversational_test_requires_turns_or_config(self):
        """Should fail validation if conversational test has neither turns nor config."""
        with pytest.raises(ValidationError) as exc_info:
            TestDefinition(
                name="test-invalid",
                prompt_reference="file:///.promptrepo/prompts/test.yaml",
                test_type=TestType.CONVERSATIONAL,
            )
        assert "must have either 'turns'" in str(exc_info.value)


class TestSimulateConversationRequest:
    """Tests for SimulateConversationRequest model."""

    def test_create_minimal_request(self):
        """Should create request with required fields."""
        request = SimulateConversationRequest(
            prompt_reference="file:///.promptrepo/prompts/test.yaml",
            user_goal="Get a refund",
            provider="openai",
            model="gpt-4",
        )
        assert request.min_turns == 3
        assert request.max_turns == 6
        assert request.user_persona is None

    def test_create_full_request(self):
        """Should create request with all fields."""
        request = SimulateConversationRequest(
            prompt_reference="file:///.promptrepo/prompts/test.yaml",
            user_goal="Get a refund for order #12345",
            user_persona="Frustrated customer who has been waiting 2 weeks",
            min_turns=2,
            max_turns=8,
            stopping_criteria="When refund is confirmed",
            template_variables={"company_name": "Acme Corp"},
            provider="anthropic",
            model="claude-3-opus",
        )
        assert request.user_persona == "Frustrated customer who has been waiting 2 weeks"
        assert request.stopping_criteria == "When refund is confirmed"
        assert request.template_variables == {"company_name": "Acme Corp"}


class TestSimulateConversationResponse:
    """Tests for SimulateConversationResponse model."""

    def test_create_response(self):
        """Should create response with turns and status."""
        turns = [
            Turn(role=TurnRole.USER, content="I need a refund"),
            Turn(role=TurnRole.ASSISTANT, content="I can help with that."),
        ]
        response = SimulateConversationResponse(
            turns=turns,
            goal_achieved=True,
            stopping_reason="Goal was achieved"
        )
        assert len(response.turns) == 2
        assert response.goal_achieved is True
        assert response.stopping_reason == "Goal was achieved"

    def test_create_response_goal_not_achieved(self):
        """Should create response when goal not achieved."""
        turns = [
            Turn(role=TurnRole.USER, content="Hi"),
        ]
        response = SimulateConversationResponse(
            turns=turns,
            goal_achieved=False,
            stopping_reason="Maximum turns reached"
        )
        assert response.goal_achieved is False
