"""
Eval Execution Service

Orchestrates eval execution workflow including:
- Executing eval suites and individual evals
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
    EvalDefinition,
    EvalExecutionResult,
    EvalSuiteExecutionResult,
    MetricConfig,
    MetricType,
    ActualEvaluationFieldsModel,
)

logger = logging.getLogger(__name__)


class EvalExecutionService:
    """
    Service for executing eval suites and individual evals.
    
    This service handles:
    - Eval suite execution orchestration
    - Single eval execution
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
            eval_meta_service: Eval service for loading definitions and saving results
            prompt_service: Prompt service for executing prompts
            deepeval_adapter: DeepEval adapter for metric evaluation
            chat_completion_service: Chat completion service for executing prompts
        """
        self.eval_meta_service = eval_meta_service
        self.prompt_service = prompt_service
        self.deepeval_adapter = deepeval_adapter
        self.chat_completion_service = chat_completion_service
    
    async def execute_eval_suite(
        self,
        user_id: str,
        repo_name: str,
        suite_name: str,
        eval_names: Optional[List[str]] = None
    ) -> EvalSuiteExecutionResult:
        """
        Execute eval suite or specific evals within suite.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            suite_name: Eval suite name
            eval_names: Optional list of specific eval names to run (None = run all)
            
        Returns:
            EvalSuiteExecutionResult with complete execution results
            
        Raises:
            NotFoundException: If suite doesn't exist
            AppException: If execution fails
        """
        logger.info(f"Executing eval suite {suite_name} in {repo_name} for user {user_id}")
        
        start_time = time.time()
        
        # Load test suite definition
        suite_data = await self.eval_meta_service.get_eval_suite(user_id, repo_name, suite_name)
        
        # Filter evals if specific eval names provided
        evals_to_run = suite_data.eval_suite.evals
        if eval_names:
            evals_to_run = [t for t in evals_to_run if t.name in eval_names]
            if not evals_to_run:
                raise NotFoundException(
                    resource="Evals",
                    identifier=", ".join(eval_names)
                )
        
        # Filter out disabled evals
        evals_to_run = [t for t in evals_to_run if t.enabled]
        
        # Execute each eval with suite-level metrics
        eval_results = []
        for test_def in evals_to_run:
            try:
                result = await self._execute_single_eval_internal(
                    user_id, repo_name, test_def, suite_data.eval_suite.metrics
                )
                eval_results.append(result)
            except Exception as e:
                logger.error(f"Failed to execute eval {test_def.name}: {e}")
                # Create error result for failed eval
                error_result = EvalExecutionResult(
                    eval_name=test_def.name,
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
                eval_results.append(error_result)
        
        # Calculate summary statistics
        total_evals = len(eval_results)
        passed_evals = sum(1 for r in eval_results if r.overall_passed)
        failed_evals = total_evals - passed_evals
        
        end_time = time.time()
        total_execution_time_ms = int((end_time - start_time) * 1000)
        
        # Create execution result
        execution_result = EvalSuiteExecutionResult(
            suite_name=suite_name,
            eval_results=eval_results,
            total_evals=total_evals,
            passed_evals=passed_evals,
            failed_evals=failed_evals,
            total_execution_time_ms=total_execution_time_ms,
            executed_at=datetime.now(timezone.utc)
        )
        
        # Save execution result
        await self.eval_meta_service.save_execution_result(
            user_id, repo_name, suite_name, execution_result
        )
        
        logger.info(
            f"Completed eval suite {suite_name}: {passed_evals}/{total_evals} passed "
            f"in {total_execution_time_ms}ms"
        )
        
        return execution_result
    
    async def execute_single_eval(
        self,
        user_id: str,
        repo_name: str,
        suite_name: str,
        eval_name: str
    ) -> EvalExecutionResult:
        """
        Execute single eval.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            suite_name: Eval suite name
            eval_name: Eval name
            
        Returns:
            EvalExecutionResult with execution results
            
        Raises:
            NotFoundException: If eval doesn't exist
        """
        logger.info(f"Executing single eval {eval_name} from suite {suite_name}")
        
        # Load test suite to get test definition and metrics
        suite_data = await self.eval_meta_service.get_eval_suite(user_id, repo_name, suite_name)
        
        # Find the specific eval
        eval_def = None
        for test in suite_data.eval_suite.evals:
            if test.name == eval_name:
                eval_def = test
                break
        
        if not eval_def:
            raise NotFoundException(
                resource="Eval",
                identifier=eval_name
            )
        
        # Execute the eval with suite-level metrics
        return await self._execute_single_eval_internal(user_id, repo_name, eval_def, suite_data.eval_suite.metrics)
    
    async def _execute_single_eval_internal(
        self,
        user_id: str,
        repo_name: str,
        eval_def: EvalDefinition,
        suite_metrics: Optional[List[MetricConfig]] = None
    ) -> EvalExecutionResult:
        """
        Internal method to execute a single eval.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            eval_def: Eval definition
            suite_metrics: Metrics from eval suite level
            
        Returns:
            EvalExecutionResult with execution results
        """
        if suite_metrics is None:
            suite_metrics = []
        start_time = time.time()
        
        try:
            # Parse prompt reference to extract file path
            # Expected format: "file:///.promptrepo/prompts/path/to/prompt.yaml"
            prompt_reference = eval_def.prompt_reference
            if prompt_reference.startswith("file:///"):
                prompt_file_path = prompt_reference.replace("file:///", "")
            else:
                prompt_file_path = prompt_reference
            
            # Build prompt_id for chat completion service
            prompt_id = f"{repo_name}:{prompt_file_path}"
            
            # Determine the user message to send
            # If user_message is provided in eval, use it; otherwise use None for single-turn
            user_message = eval_def.user_message
            
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
            for var_name, var_value in eval_def.template_variables.items():
                placeholder = f"{{{var_name}}}"
                if placeholder in prompt_text:
                    prompt_text = prompt_text.replace(placeholder, str(var_value))
            
            input_text = user_message if user_message is not None else prompt_text
            
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
                # Build test case parameters from metric config and actual fields
                test_case_params: Dict[str, Any] = {
                    "input_text": str(input_text),
                    "actual_output": actual_output
                }
                
                # Add expected fields from evaluation_fields config
                # The evaluation_fields.config contains the raw expected values
                if eval_def.evaluation_fields.config:
                    config_dict = eval_def.evaluation_fields.config
                    
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
            
            return EvalExecutionResult(
                eval_name=eval_def.name,
                prompt_reference=eval_def.prompt_reference,
                template_variables=eval_def.template_variables,
                actual_evaluation_fields=actual_fields,
                expected_evaluation_fields=eval_def.evaluation_fields,
                metric_results=metric_results,
                overall_passed=overall_passed,
                executed_at=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Error executing eval {eval_def.name}: {e}")
            raise AppException(
                message=f"Failed to execute eval {eval_def.name}: {str(e)}"
            )