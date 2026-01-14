"""
Eval Execution Service

Orchestrates eval execution workflow including:
- Executing evals and individual tests
- Coordinating with prompt service for execution
- Integration with DeepEval adapter for metric evaluation
- Saving execution results to YAML files
"""

import logging
import time
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from middlewares.rest.exceptions import NotFoundException, AppException
from services.artifacts.prompt.prompt_meta_service import PromptMetaService
from services.llm.chat_completion_service import ChatCompletionService
from services.config.config_service import ConfigService

from .eval_meta_service import EvalMetaService
from .eval_execution_meta_service import EvalExecutionMetaService
from lib.deepeval.deepeval_adapter import DeepEvalAdapter, LLMConfig
from .models import (
    TestDefinition,
    TestExecutionResult,
    EvalExecutionResult,
    MetricConfig,
    ActualTestFieldsModel,
    TestType,
    Turn,
    TurnRole,
)

logger = logging.getLogger(__name__)


class EvalExecutionService:
    """
    Service for executing evals and individual tests.
    
    This service handles:
    - Eval execution orchestration
    - Single test execution
    - Prompt execution with template variables
    - DeepEval metric evaluation
    - Result aggregation and storage
    """
    
    def __init__(
        self,
        eval_meta_service: EvalMetaService,
        eval_execution_meta_service: EvalExecutionMetaService,
        prompt_service: PromptMetaService,
        deepeval_adapter: DeepEvalAdapter,
        chat_completion_service: ChatCompletionService,
        config_service: ConfigService,
    ):
        """
        Initialize EvalExecutionService with injected dependencies.

        Args:
            eval_meta_service: Eval meta service for loading definitions
            eval_execution_meta_service: Eval execution meta service for saving results
            prompt_service: Prompt service for executing prompts
            deepeval_adapter: DeepEval adapter for metric evaluation
            chat_completion_service: Chat completion service for executing prompts
            config_service: Config service for looking up LLM configurations
        """
        self.eval_meta_service = eval_meta_service
        self.eval_execution_meta_service = eval_execution_meta_service
        self.prompt_service = prompt_service
        self.deepeval_adapter = deepeval_adapter
        self.chat_completion_service = chat_completion_service
        self.config_service = config_service

    def _get_llm_config_for_metric(
        self,
        metric_config: MetricConfig,
        user_id: str
    ) -> Optional[LLMConfig]:
        """
        Get LLM configuration for a metric from user's configured providers.

        Args:
            metric_config: The metric configuration with provider/model info
            user_id: User ID to look up LLM configs

        Returns:
            LLMConfig if found, None otherwise
        """
        if not metric_config.provider or not metric_config.model:
            return None

        llm_configs = self.config_service.get_llm_configs(user_id=user_id) or []

        # First try exact match (provider + model)
        for config in llm_configs:
            if config.provider == metric_config.provider and config.model == metric_config.model:
                if config.api_key:
                    return LLMConfig(
                        provider=config.provider,
                        model=config.model,
                        api_key=config.api_key,
                        api_base=config.api_base_url if config.api_base_url else None,
                    )

        # Then try provider-only match
        for config in llm_configs:
            if config.provider == metric_config.provider:
                if config.api_key:
                    return LLMConfig(
                        provider=config.provider,
                        model=metric_config.model,
                        api_key=config.api_key,
                        api_base=config.api_base_url if config.api_base_url else None,
                    )

        logger.warning(
            f"No API key found for metric provider '{metric_config.provider}'. "
            f"Available providers: {[c.provider for c in llm_configs]}"
        )
        return None
    
    async def execute_eval(
        self,
        user_id: str,
        repo_name: str,
        eval_name: str,
        test_names: Optional[List[str]] = None
    ) -> EvalExecutionResult:
        """
        Execute eval or specific tests within eval.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            eval_name: Eval name
            test_names: Optional list of specific test names to run (None = run all)
            
        Returns:
            EvalExecutionResult with complete execution results
            
        Raises:
            NotFoundException: If eval doesn't exist
            AppException: If execution fails
        """
        logger.info(f"Executing eval {eval_name} in {repo_name} for user {user_id}")
        
        start_time = time.time()
        
        # Load eval definition
        eval_data = await self.eval_meta_service.get(user_id, repo_name, eval_name)
        
        if not eval_data:
            raise NotFoundException(
                resource="Eval",
                identifier=eval_name
            )
        
        # Filter tests if specific test names provided
        tests_to_run = eval_data.eval.tests
        if test_names:
            tests_to_run = [t for t in tests_to_run if t.name in test_names]
            if not tests_to_run:
                raise NotFoundException(
                    resource="Tests",
                    identifier=", ".join(test_names)
                )
        
        # Filter out disabled tests
        tests_to_run = [t for t in tests_to_run if t.enabled]
        
        # Execute each test with eval-level metrics
        test_results = []
        for test_def in tests_to_run:
            try:
                result = await self._execute_single_test_internal(
                    user_id, repo_name, test_def, eval_data.eval.metrics
                )
                test_results.append(result)
            except Exception as e:
                logger.error(f"Failed to execute test {test_def.name}: {e}")
                # Create error result for failed test
                error_result = TestExecutionResult(
                    test_name=test_def.name,
                    prompt_reference=test_def.prompt_reference,
                    template_variables=test_def.template_variables,
                    actual_test_fields=ActualTestFieldsModel(
                        actual_output="",
                        error=str(e)
                    ),
                    expected_test_fields=test_def.test_fields,
                    metric_results=[],
                    overall_passed=False,
                    executed_at=datetime.now(timezone.utc)
                )
                test_results.append(error_result)
        
        # Calculate summary statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.overall_passed)
        failed_tests = total_tests - passed_tests
        
        end_time = time.time()
        total_execution_time_ms = int((end_time - start_time) * 1000)
        
        # Create execution result
        execution_result = EvalExecutionResult(
            eval_name=eval_name,
            test_results=test_results,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_execution_time_ms=total_execution_time_ms,
            executed_at=datetime.now(timezone.utc)
        )
        
        # Save execution result
        await self.eval_execution_meta_service.save_execution_result(
            user_id, repo_name, eval_name, execution_result
        )
        
        logger.info(
            f"Completed eval {eval_name}: {passed_tests}/{total_tests} passed "
            f"in {total_execution_time_ms}ms"
        )
        
        return execution_result
    
    async def execute_single_test(
        self,
        user_id: str,
        repo_name: str,
        eval_name: str,
        test_name: str
    ) -> TestExecutionResult:
        """
        Execute single test.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            eval_name: Eval name
            test_name: Test name
            
        Returns:
            TestExecutionResult with execution results
            
        Raises:
            NotFoundException: If test doesn't exist
        """
        logger.info(f"Executing single test {test_name} from eval {eval_name}")
        
        # Load eval to get test definition and metrics
        eval_data = await self.eval_meta_service.get(user_id, repo_name, eval_name)
        
        if not eval_data:
            raise NotFoundException(
                resource="Eval",
                identifier=eval_name
            )
        
        # Find the specific test
        test_def = None
        for test in eval_data.eval.tests:
            if test.name == test_name:
                test_def = test
                break
        
        if not test_def:
            raise NotFoundException(
                resource="Test",
                identifier=test_name
            )
        
        # Execute the test with eval-level metrics
        return await self._execute_single_test_internal(user_id, repo_name, test_def, eval_data.eval.metrics)
    
    async def _execute_single_test_internal(
        self,
        user_id: str,
        repo_name: str,
        test_def: TestDefinition,
        eval_metrics: Optional[List[MetricConfig]] = None
    ) -> TestExecutionResult:
        """
        Internal method to execute a single test.

        Args:
            user_id: User ID
            repo_name: Repository name
            test_def: Test definition
            eval_metrics: Metrics from eval level

        Returns:
            TestExecutionResult with execution results
        """
        if eval_metrics is None:
            eval_metrics = []

        # Route to appropriate execution method based on test type
        if test_def.test_type == TestType.CONVERSATIONAL:
            return await self._execute_conversational_test(
                user_id, repo_name, test_def, eval_metrics
            )
        else:
            return await self._execute_single_turn_test(
                user_id, repo_name, test_def, eval_metrics
            )

    async def _execute_single_turn_test(
        self,
        user_id: str,
        repo_name: str,
        test_def: TestDefinition,
        eval_metrics: List[MetricConfig]
    ) -> TestExecutionResult:
        """Execute a single-turn test."""
        start_time = time.time()

        try:
            # Parse prompt reference to extract file path
            prompt_reference = test_def.prompt_reference
            if prompt_reference.startswith("file:///"):
                prompt_file_path = prompt_reference.replace("file:///", "")
            else:
                prompt_file_path = prompt_reference

            # Build prompt_id for chat completion service
            prompt_id = f"{repo_name}:{prompt_file_path}"

            # Determine the user message to send
            user_message = test_def.user_message

            # Execute prompt using ChatCompletionService
            completion_response = await self.chat_completion_service.execute_completion_from_saved_prompt(
                user_id=user_id,
                prompt_id=prompt_id,
                last_user_message=user_message,
                conversation_history=None
            )

            actual_output = completion_response.content or ""
            tools_called = [msg.model_dump() for msg in completion_response.tool_calls] if completion_response.tool_calls else None

            # Load the prompt to get the input text for metrics
            prompt_meta = await self.prompt_service.get(
                user_id, repo_name, prompt_file_path
            )

            if not prompt_meta:
                raise NotFoundException(
                    resource="Prompt",
                    identifier=prompt_file_path
                )

            # Apply template variables to prompt for input text
            prompt_text = prompt_meta.prompt.prompt
            for var_name, var_value in test_def.template_variables.items():
                placeholder = f"{{{var_name}}}"
                if placeholder in prompt_text:
                    prompt_text = prompt_text.replace(placeholder, str(var_value))

            input_text = user_message if user_message is not None else prompt_text

            # Create actual test fields
            end_time = time.time()
            execution_time_ms = int((end_time - start_time) * 1000)

            actual_fields = ActualTestFieldsModel(
                actual_output=actual_output,
                tools_called=tools_called,
                execution_time_ms=execution_time_ms
            )

            # Evaluate metrics
            metric_results = []
            if eval_metrics:
                test_case_params: Dict[str, Any] = {
                    "input_text": str(input_text),
                    "actual_output": actual_output
                }

                if test_def.test_fields.config:
                    config_dict = test_def.test_fields.config

                    if 'expected_output' in config_dict:
                        test_case_params["expected_output"] = config_dict['expected_output']
                    if 'retrieval_context' in config_dict:
                        context = config_dict['retrieval_context']
                        if isinstance(context, str):
                            context = [context]
                        test_case_params["retrieval_context"] = context

                test_case = self.deepeval_adapter.create_test_case(**test_case_params)

                metrics = [
                    self.deepeval_adapter.create_metric(
                        metric_config,
                        llm_config=self._get_llm_config_for_metric(metric_config, user_id)
                    )
                    for metric_config in eval_metrics
                ]

                metric_results = await self.deepeval_adapter.evaluate_metrics(
                    test_case, metrics, eval_metrics
                )

            overall_passed = all(result.passed for result in metric_results) if metric_results else True

            return TestExecutionResult(
                test_name=test_def.name,
                prompt_reference=test_def.prompt_reference,
                template_variables=test_def.template_variables,
                actual_test_fields=actual_fields,
                expected_test_fields=test_def.test_fields,
                metric_results=metric_results,
                overall_passed=overall_passed,
                executed_at=datetime.now(timezone.utc),
                test_type=TestType.SINGLE_TURN,
            )

        except Exception as e:
            logger.error(f"Error executing test {test_def.name}: {e}")
            raise AppException(
                message=f"Failed to execute test {test_def.name}: {str(e)}"
            )

    async def _execute_conversational_test(
        self,
        user_id: str,
        repo_name: str,
        test_def: TestDefinition,
        eval_metrics: List[MetricConfig]
    ) -> TestExecutionResult:
        """
        Execute a conversational (multi-turn) test.

        This method handles tests that have predefined conversation turns.
        It executes each turn through the chatbot and collects responses.
        """
        start_time = time.time()

        try:
            # Parse prompt reference
            prompt_reference = test_def.prompt_reference
            if prompt_reference.startswith("file:///"):
                prompt_file_path = prompt_reference.replace("file:///", "")
            else:
                prompt_file_path = prompt_reference

            prompt_id = f"{repo_name}:{prompt_file_path}"

            # Get the predefined turns or empty list
            predefined_turns = test_def.turns or []

            # Execute the conversation
            executed_turns: List[Turn] = []

            # Import message schemas for conversation history
            from schemas.messages import UserMessageSchema, AIMessageSchema

            for turn in predefined_turns:
                if turn.role == TurnRole.USER:
                    # Add user turn to executed turns
                    executed_turns.append(turn)

                    # Build conversation history from previous turns
                    conversation_history = []
                    for prev_turn in executed_turns[:-1]:
                        if prev_turn.role == TurnRole.USER:
                            conversation_history.append(UserMessageSchema(content=prev_turn.content))
                        else:
                            conversation_history.append(AIMessageSchema(content=prev_turn.content))

                    # Get assistant response
                    completion_response = await self.chat_completion_service.execute_completion_from_saved_prompt(
                        user_id=user_id,
                        prompt_id=prompt_id,
                        last_user_message=turn.content,
                        conversation_history=conversation_history if conversation_history else None,
                    )

                    assistant_content = completion_response.content or ""
                    tools_called = [tc.model_dump() for tc in completion_response.tool_calls] if completion_response.tool_calls else None

                    # Add assistant response
                    executed_turns.append(Turn(
                        role=TurnRole.ASSISTANT,
                        content=assistant_content,
                        tools_called=tools_called,
                    ))

            # Create actual test fields - for conversational tests, actual_output is the full conversation
            end_time = time.time()
            execution_time_ms = int((end_time - start_time) * 1000)

            # Build actual output as conversation summary
            conversation_text = "\n".join([
                f"{t.role.value}: {t.content}" for t in executed_turns
            ])

            actual_fields = ActualTestFieldsModel(
                actual_output=conversation_text,
                execution_time_ms=execution_time_ms
            )

            # Evaluate conversational metrics
            metric_results = []
            if eval_metrics:
                # For conversational metrics, we need to create a conversational test case
                # This will be evaluated with DeepEval's conversational metrics
                metric_results = await self._evaluate_conversational_metrics(
                    executed_turns, eval_metrics, test_def, user_id
                )

            overall_passed = all(result.passed for result in metric_results) if metric_results else True

            return TestExecutionResult(
                test_name=test_def.name,
                prompt_reference=test_def.prompt_reference,
                template_variables=test_def.template_variables,
                actual_test_fields=actual_fields,
                expected_test_fields=test_def.test_fields,
                metric_results=metric_results,
                overall_passed=overall_passed,
                executed_at=datetime.now(timezone.utc),
                test_type=TestType.CONVERSATIONAL,
                executed_turns=executed_turns,
            )

        except Exception as e:
            logger.error(f"Error executing conversational test {test_def.name}: {e}")
            raise AppException(
                message=f"Failed to execute conversational test {test_def.name}: {str(e)}"
            )

    async def _evaluate_conversational_metrics(
        self,
        turns: List[Turn],
        eval_metrics: List[MetricConfig],
        test_def: TestDefinition,
        user_id: str
    ) -> List:
        """
        Evaluate conversational metrics on executed turns.

        This method handles both standard metrics (applied to each turn)
        and conversational-specific metrics (applied to the whole conversation).
        """
        from lib.deepeval.models import MetricType, MetricResult

        metric_results = []

        for metric_config in eval_metrics:
            try:
                # Check if this is a conversational metric
                if MetricType.is_conversational(metric_config.type):
                    # TODO: Implement full DeepEval conversational metric evaluation
                    # For now, we'll create a placeholder result
                    # This requires DeepEval's ConversationalTestCase which needs special handling
                    logger.warning(
                        f"Conversational metric {metric_config.type.value} evaluation not fully implemented yet"
                    )
                    metric_results.append(MetricResult(
                        type=metric_config.type,
                        score=0.0,
                        passed=False,
                        threshold=metric_config.threshold or 0.5,
                        reason="Conversational metric evaluation not fully implemented yet"
                    ))
                else:
                    # For standard metrics, evaluate on the last assistant response
                    last_assistant_turn = None
                    last_user_turn = None
                    for turn in reversed(turns):
                        if turn.role == TurnRole.ASSISTANT and last_assistant_turn is None:
                            last_assistant_turn = turn
                        elif turn.role == TurnRole.USER and last_user_turn is None:
                            last_user_turn = turn
                        if last_assistant_turn and last_user_turn:
                            break

                    if last_assistant_turn and last_user_turn:
                        test_case_params: Dict[str, Any] = {
                            "input_text": last_user_turn.content,
                            "actual_output": last_assistant_turn.content
                        }

                        # Add expected fields if provided
                        if test_def.test_fields.config:
                            config_dict = test_def.test_fields.config
                            if 'expected_output' in config_dict:
                                test_case_params["expected_output"] = config_dict['expected_output']
                            if 'retrieval_context' in config_dict:
                                context = config_dict['retrieval_context']
                                if isinstance(context, str):
                                    context = [context]
                                test_case_params["retrieval_context"] = context

                        test_case = self.deepeval_adapter.create_test_case(**test_case_params)
                        metric = self.deepeval_adapter.create_metric(
                            metric_config,
                            llm_config=self._get_llm_config_for_metric(metric_config, user_id)
                        )

                        results = await self.deepeval_adapter.evaluate_metrics(
                            test_case, [metric], [metric_config]
                        )
                        metric_results.extend(results)

            except Exception as e:
                logger.error(f"Error evaluating metric {metric_config.type.value}: {e}")
                metric_results.append(MetricResult(
                    type=metric_config.type,
                    score=0.0,
                    passed=False,
                    threshold=metric_config.threshold or 0.5,
                    error=str(e)
                ))

        return metric_results