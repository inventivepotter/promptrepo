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

from middlewares.rest.exceptions import NotFoundException, AppException
from services.prompt.prompt_service import PromptService

from .test_service import TestService
from .deepeval_adapter import DeepEvalAdapter
from .models import (
    UnitTestDefinition,
    UnitTestExecutionResult,
    TestSuiteExecutionResult,
    MetricResult
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
        deepeval_adapter: DeepEvalAdapter
    ):
        """
        Initialize TestExecutionService with injected dependencies.
        
        Args:
            test_service: Test service for loading definitions and saving results
            prompt_service: Prompt service for executing prompts
            deepeval_adapter: DeepEval adapter for metric evaluation
        """
        self.test_service = test_service
        self.prompt_service = prompt_service
        self.deepeval_adapter = deepeval_adapter
    
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
        
        # Execute each test
        test_results = []
        for test_def in tests_to_run:
            try:
                result = await self._execute_single_test_internal(
                    user_id, repo_name, test_def
                )
                test_results.append(result)
            except Exception as e:
                logger.error(f"Failed to execute test {test_def.name}: {e}")
                # Create error result for failed test
                error_result = UnitTestExecutionResult(
                    test_name=test_def.name,
                    prompt_reference=test_def.prompt_reference,
                    template_variables=test_def.template_variables,
                    actual_output="",
                    expected_output=test_def.expected_output,
                    metric_results=[],
                    overall_passed=False,
                    execution_time_ms=0,
                    executed_at=datetime.now(timezone.utc),
                    error=str(e)
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
        
        # Load test suite to get test definition
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
        
        # Execute the test
        return await self._execute_single_test_internal(user_id, repo_name, test_def)
    
    async def _execute_single_test_internal(
        self,
        user_id: str,
        repo_name: str,
        test_def: UnitTestDefinition
    ) -> UnitTestExecutionResult:
        """
        Internal method to execute a single test.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            test_def: Test definition
            
        Returns:
            UnitTestExecutionResult with execution results
        """
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
            
            # For now, we'll use the prompt_text as input to DeepEval
            # In a real implementation, you would execute the prompt using ChatCompletionService
            # and get the actual_output from the LLM
            
            # TODO: Execute prompt using ChatCompletionService
            # For now, we'll create a placeholder actual_output
            actual_output = f"[Simulated LLM output for: {prompt_text[:100]}...]"
            
            # Create DeepEval test case
            # Extract input from template variables (typically user_question or similar)
            input_text = test_def.template_variables.get(
                "user_question",
                test_def.template_variables.get("input", prompt_text)
            )
            
            # Only evaluate metrics if they are defined
            metric_results = []
            if test_def.metrics:
                # Extract retrieval_context from template_variables if present
                retrieval_context = test_def.template_variables.get("retrieval_context")
                
                test_case = self.deepeval_adapter.create_test_case(
                    input_text=str(input_text),
                    actual_output=actual_output,
                    expected_output=test_def.expected_output,
                    retrieval_context=retrieval_context
                )
                
                # Create DeepEval metrics from configs
                metrics = [
                    self.deepeval_adapter.create_metric(metric_config)
                    for metric_config in test_def.metrics
                ]
                
                # Evaluate metrics
                metric_results = await self.deepeval_adapter.evaluate_metrics(
                    test_case, metrics, test_def.metrics
                )
            
            # Determine overall pass/fail
            # If no metrics, test passes if it executes successfully
            overall_passed = all(result.passed for result in metric_results) if metric_results else True
            
            end_time = time.time()
            execution_time_ms = int((end_time - start_time) * 1000)
            
            return UnitTestExecutionResult(
                test_name=test_def.name,
                prompt_reference=test_def.prompt_reference,
                template_variables=test_def.template_variables,
                actual_output=actual_output,
                expected_output=test_def.expected_output,
                metric_results=metric_results,
                overall_passed=overall_passed,
                execution_time_ms=execution_time_ms,
                executed_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Error executing test {test_def.name}: {e}")
            raise AppException(
                message=f"Failed to execute test {test_def.name}: {str(e)}"
            )