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

from middlewares.rest.exceptions import NotFoundException, AppException, ValidationException
from services.prompt.prompt_service import PromptService
from services.llm.chat_completion_service import ChatCompletionService

from .eval_meta_service import EvalMetaService
from lib.deepeval.deepeval_adapter import DeepEvalAdapter
from .models import (
    TestDefinition,
    TestExecutionResult,
    EvalExecutionResult,
    MetricConfig,
    MetricType,
    ActualTestFieldsModel,
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
        prompt_service: PromptService,
        deepeval_adapter: DeepEvalAdapter,
        chat_completion_service: ChatCompletionService
    ):
        """
        Initialize EvalExecutionService with injected dependencies.
        
        Args:
            eval_meta_service: Eval meta service for loading definitions and saving results
            prompt_service: Prompt service for executing prompts
            deepeval_adapter: DeepEval adapter for metric evaluation
            chat_completion_service: Chat completion service for executing prompts
        """
        self.eval_meta_service = eval_meta_service
        self.prompt_service = prompt_service
        self.deepeval_adapter = deepeval_adapter
        self.chat_completion_service = chat_completion_service
    
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
        eval_data = await self.eval_meta_service.get_eval(user_id, repo_name, eval_name)
        
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
        await self.eval_meta_service.save_execution_result(
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
        eval_data = await self.eval_meta_service.get_eval(user_id, repo_name, eval_name)
        
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
        start_time = time.time()
        
        try:
            # Parse prompt reference to extract file path
            # Expected format: "file:///.promptrepo/prompts/path/to/prompt.yaml"
            prompt_reference = test_def.prompt_reference
            if prompt_reference.startswith("file:///"):
                prompt_file_path = prompt_reference.replace("file:///", "")
            else:
                prompt_file_path = prompt_reference
            
            # Build prompt_id for chat completion service
            prompt_id = f"{repo_name}:{prompt_file_path}"
            
            # Determine the user message to send
            # If user_message is provided in test, use it; otherwise use None for single-turn
            user_message = test_def.user_message
            
            # Execute prompt using ChatCompletionService's execute_completion_from_saved_prompt
            completion_response = await self.chat_completion_service.execute_completion_from_saved_prompt(
                user_id=user_id,
                prompt_id=prompt_id,
                last_user_message=user_message,
                conversation_history=None  # Tests don't use conversation history
            )
            
            actual_output = completion_response.content or ""
            tools_called = [msg.model_dump() for msg in completion_response.tool_calls] if completion_response.tool_calls else None
            
            # Extract input text for metrics (use user_message if provided, otherwise use the prompt text)
            # We need to load the prompt to get the input text for metrics
            prompt_meta = await self.prompt_service.get_prompt(
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
            
            # Only evaluate metrics if they are defined at eval level
            metric_results = []
            if eval_metrics:
                # Build test case parameters from metric config and actual fields
                test_case_params: Dict[str, Any] = {
                    "input_text": str(input_text),
                    "actual_output": actual_output
                }
                
                # Add expected fields from test_fields config
                # The test_fields.config contains the raw expected values
                if test_def.test_fields.config:
                    config_dict = test_def.test_fields.config
                    
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
                    for metric_config in eval_metrics
                ]
                
                # Evaluate metrics
                metric_results = await self.deepeval_adapter.evaluate_metrics(
                    test_case, metrics, eval_metrics
                )
            
            # Determine overall pass/fail
            # If no metrics, test passes if it executes successfully
            overall_passed = all(result.passed for result in metric_results) if metric_results else True
            
            return TestExecutionResult(
                test_name=test_def.name,
                prompt_reference=test_def.prompt_reference,
                template_variables=test_def.template_variables,
                actual_test_fields=actual_fields,
                expected_test_fields=test_def.test_fields,
                metric_results=metric_results,
                overall_passed=overall_passed,
                executed_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Error executing test {test_def.name}: {e}")
            raise AppException(
                message=f"Failed to execute test {test_def.name}: {str(e)}"
            )