"""
Test Execution Service

Orchestrates test execution workflow including:
- Executing test suites and individual tests
- Coordinating with prompt service for execution
- Integration with DeepEval adapter for metric evaluation
- Saving execution results to YAML files
"""

import logging
import time
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from middlewares.rest.exceptions import NotFoundException, AppException, ValidationException
from services.prompt.prompt_service import PromptService
from services.llm.completion_service import ChatCompletionService
from services.llm.models import ChatCompletionRequest, ChatMessage

from .test_service import TestService
from .deepeval.deepeval_adapter import DeepEvalAdapter
from .models import (
    UnitTestDefinition,
    UnitTestExecutionResult,
    TestSuiteExecutionResult,
    MetricResult,
    MetricConfig,
    MetricType,
    ActualEvaluationFieldsModel,
    ExpectedEvaluationFieldsModel
)

logger = logging.getLogger(__name__)


class TestExecutionService:
    """
    Service for executing test suites and individual tests.
    
    This service handles:
    - Test suite execution orchestration
    - Single test execution
    - Prompt execution with template variables
    - DeepEval metric evaluation
    - Result aggregation and storage
    """
    
    def __init__(
        self,
        test_service: TestService,
        prompt_service: PromptService,
        deepeval_adapter: DeepEvalAdapter,
        chat_completion_service: ChatCompletionService
    ):
        """
        Initialize TestExecutionService with injected dependencies.
        
        Args:
            test_service: Test service for loading definitions and saving results
            prompt_service: Prompt service for executing prompts
            deepeval_adapter: DeepEval adapter for metric evaluation
            chat_completion_service: Chat completion service for executing prompts
        """
        self.test_service = test_service
        self.prompt_service = prompt_service
        self.deepeval_adapter = deepeval_adapter
        self.chat_completion_service = chat_completion_service
    
    async def execute_test_suite(
        self,
        user_id: str,
        repo_name: str,
        suite_name: str,
        test_names: Optional[List[str]] = None
    ) -> TestSuiteExecutionResult:
        """
        Execute test suite or specific tests within suite.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            suite_name: Test suite name
            test_names: Optional list of specific test names to run (None = run all)
            
        Returns:
            TestSuiteExecutionResult with complete execution results
            
        Raises:
            NotFoundException: If suite doesn't exist
            AppException: If execution fails
        """
        logger.info(f"Executing test suite {suite_name} in {repo_name} for user {user_id}")
        
        start_time = time.time()
        
        # Load test suite definition
        suite_data = await self.test_service.get_test_suite(user_id, repo_name, suite_name)
        
        # Filter tests if specific test names provided
        tests_to_run = suite_data.test_suite.tests
        if test_names:
            tests_to_run = [t for t in tests_to_run if t.name in test_names]
            if not tests_to_run:
                raise NotFoundException(
                    resource="Tests",
                    identifier=", ".join(test_names)
                )
        
        # Filter out disabled tests
        tests_to_run = [t for t in tests_to_run if t.enabled]
        
        # Execute each test with suite-level metrics
        test_results = []
        for test_def in tests_to_run:
            try:
                result = await self._execute_single_test_internal(
                    user_id, repo_name, test_def, suite_data.test_suite.metrics
                )
                test_results.append(result)
            except Exception as e:
                logger.error(f"Failed to execute test {test_def.name}: {e}")
                # Create error result for failed test
                error_result = UnitTestExecutionResult(
                    test_name=test_def.name,
                    prompt_reference=test_def.prompt_reference,
                    template_variables=test_def.template_variables,
                    actual_evaluation_fields=ActualEvaluationFieldsModel(
                        actual_output="",
                        error=str(e)
                    ),
                    expected_evaluation_fields=test_def.evaluation_fields,
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
        execution_result = TestSuiteExecutionResult(
            suite_name=suite_name,
            test_results=test_results,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_execution_time_ms=total_execution_time_ms,
            executed_at=datetime.now(timezone.utc)
        )
        
        # Save execution result
        await self.test_service.save_execution_result(
            user_id, repo_name, suite_name, execution_result
        )
        
        logger.info(
            f"Completed test suite {suite_name}: {passed_tests}/{total_tests} passed "
            f"in {total_execution_time_ms}ms"
        )
        
        return execution_result
    
    async def execute_single_test(
        self,
        user_id: str,
        repo_name: str,
        suite_name: str,
        test_name: str
    ) -> UnitTestExecutionResult:
        """
        Execute single test.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            suite_name: Test suite name
            test_name: Test name
            
        Returns:
            UnitTestExecutionResult with execution results
            
        Raises:
            NotFoundException: If test doesn't exist
        """
        logger.info(f"Executing single test {test_name} from suite {suite_name}")
        
        # Load test suite to get test definition and metrics
        suite_data = await self.test_service.get_test_suite(user_id, repo_name, suite_name)
        
        # Find the specific test
        test_def = None
        for test in suite_data.test_suite.tests:
            if test.name == test_name:
                test_def = test
                break
        
        if not test_def:
            raise NotFoundException(
                resource="Test",
                identifier=test_name
            )
        
        # Execute the test with suite-level metrics
        return await self._execute_single_test_internal(user_id, repo_name, test_def, suite_data.test_suite.metrics)
    
    async def _execute_single_test_internal(
        self,
        user_id: str,
        repo_name: str,
        test_def: UnitTestDefinition,
        suite_metrics: Optional[List[MetricConfig]] = None
    ) -> UnitTestExecutionResult:
        """
        Internal method to execute a single test.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            test_def: Test definition
            suite_metrics: Metrics from test suite level
            
        Returns:
            UnitTestExecutionResult with execution results
        """
        if suite_metrics is None:
            suite_metrics = []
        start_time = time.time()
        
        try:
            # Parse prompt reference to extract file path
            # Expected format: "file:///.promptrepo/prompts/path/to/prompt.yaml"
            prompt_reference = test_def.prompt_reference
            if prompt_reference.startswith("file:///"):
                prompt_file_path = prompt_reference.replace("file:///", "")
            else:
                prompt_file_path = prompt_reference
            
            # Load prompt
            prompt_meta = await self.prompt_service.get_prompt(
                user_id, repo_name, prompt_file_path
            )
            
            if not prompt_meta:
                raise NotFoundException(
                    resource="Prompt",
                    identifier=prompt_file_path
                )
            
            # Apply template variables to prompt
            prompt_text = prompt_meta.prompt.prompt
            
            # Simple template variable substitution
            # Replace {variable_name} with actual values
            for var_name, var_value in test_def.template_variables.items():
                placeholder = f"{{{var_name}}}"
                if placeholder in prompt_text:
                    prompt_text = prompt_text.replace(placeholder, str(var_value))
            
            # Extract input from template variables (typically user_question or similar)
            input_text = test_def.template_variables.get(
                "user_question",
                test_def.template_variables.get("input", prompt_text)
            )
            
            # Execute prompt using ChatCompletionService
            # Check if any metric requires LLM execution
            needs_llm_execution = any(
                metric.provider and metric.model
                for metric in suite_metrics
            )
            
            if not needs_llm_execution:
                raise ValidationException(
                    message="At least one metric must have provider and model configured for test execution",
                    context={"test_name": test_def.name}
                )
            
            # Use the first non-deterministic metric's provider/model for execution
            execution_metric = next(
                (m for m in suite_metrics if m.provider and m.model),
                None
            )
            
            if not execution_metric:
                raise ValidationException(
                    message="No metric found with provider and model configuration",
                    context={"test_name": test_def.name}
                )
            
            # Build chat completion request
            # Use prompt text directly as system message (could be enhanced to parse system/user)
            messages = [
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content=prompt_text)
            ]
            
            # Ensure stop is a list if it's a string
            stop_sequences = None
            if prompt_meta.prompt.stop:
                if isinstance(prompt_meta.prompt.stop, str):
                    stop_sequences = [prompt_meta.prompt.stop]
                else:
                    stop_sequences = prompt_meta.prompt.stop
            
            completion_request = ChatCompletionRequest(
                messages=messages,
                provider=execution_metric.provider,  # type: ignore - already validated above
                model=execution_metric.model,  # type: ignore - already validated above
                stream=False,
                temperature=prompt_meta.prompt.temperature if prompt_meta.prompt.temperature is not None else None,
                max_tokens=prompt_meta.prompt.max_tokens if prompt_meta.prompt.max_tokens else None,
                top_p=prompt_meta.prompt.top_p if prompt_meta.prompt.top_p is not None else None,
                frequency_penalty=prompt_meta.prompt.frequency_penalty if prompt_meta.prompt.frequency_penalty is not None else None,
                presence_penalty=prompt_meta.prompt.presence_penalty if prompt_meta.prompt.presence_penalty is not None else None,
                stop=stop_sequences,
                tools=prompt_meta.prompt.tools if prompt_meta.prompt.tools else None,
                prompt_id=f"{repo_name}:{prompt_file_path}",
                repo_name=repo_name
            )
            
            # Execute completion
            content, finish_reason, usage_stats, inference_time, tool_calls = \
                await self.chat_completion_service.execute_non_streaming_completion(
                    completion_request,
                    user_id
                )
            
            actual_output = content or ""
            tools_called = tool_calls if tool_calls else None
            
            # Create actual evaluation fields
            end_time = time.time()
            execution_time_ms = int((end_time - start_time) * 1000)
            
            actual_fields = ActualEvaluationFieldsModel(
                actual_output=actual_output,
                tools_called=tools_called,
                execution_time_ms=execution_time_ms
            )
            
            # Only evaluate metrics if they are defined at suite level
            metric_results = []
            if suite_metrics:
                # Get expected fields config from test definition
                metric_config = test_def.evaluation_fields.to_metric_config()
                
                # Build test case parameters from metric config and actual fields
                test_case_params: Dict[str, Any] = {
                    "input_text": str(input_text),
                    "actual_output": actual_output
                }
                
                # Add expected fields if they exist in metric config
                if metric_config:
                    # Use model_dump to get dict representation for field checking
                    config_dict = metric_config.model_dump(exclude_none=True)
                    
                    if 'expected_output' in config_dict:
                        test_case_params["expected_output"] = config_dict['expected_output']
                    if 'retrieval_context' in config_dict:
                        # Ensure retrieval_context is a list
                        context = config_dict['retrieval_context']
                        if isinstance(context, str):
                            context = [context]
                        test_case_params["retrieval_context"] = context
                
                test_case = self.deepeval_adapter.create_test_case(**test_case_params)
                
                # Create DeepEval metrics from configs
                metrics = [
                    self.deepeval_adapter.create_metric(metric_config)
                    for metric_config in suite_metrics
                ]
                
                # Evaluate metrics
                metric_results = await self.deepeval_adapter.evaluate_metrics(
                    test_case, metrics, suite_metrics
                )
            
            # Determine overall pass/fail
            # If no metrics, test passes if it executes successfully
            overall_passed = all(result.passed for result in metric_results) if metric_results else True
            
            return UnitTestExecutionResult(
                test_name=test_def.name,
                prompt_reference=test_def.prompt_reference,
                template_variables=test_def.template_variables,
                actual_evaluation_fields=actual_fields,
                expected_evaluation_fields=test_def.evaluation_fields,
                metric_results=metric_results,
                overall_passed=overall_passed,
                executed_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Error executing test {test_def.name}: {e}")
            raise AppException(
                message=f"Failed to execute test {test_def.name}: {str(e)}"
            )