"""
Tool execution service for handling tool calls and responses.
"""
import json
import logging
from typing import List, Optional, Dict, Any

from services.tool.tool_service import ToolService
from services.llm.models import ChatMessage, ChatCompletionRequest
from services.llm.completion_service import ChatCompletionService

logger = logging.getLogger(__name__)


class ToolExecutionService:
    """Service for executing tool calls and generating responses."""
    
    def __init__(
        self,
        tool_service: ToolService,
        chat_completion_service: ChatCompletionService
    ):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.tool_service = tool_service
        self.chat_completion_service = chat_completion_service
    
    async def execute_tool_call_loop(
        self,
        initial_tool_calls: List[Dict[str, Any]],
        request_body: ChatCompletionRequest,
        assistant_message: ChatMessage,
        user_id: str,
        request_id: Optional[str] = None
    ) -> tuple[ChatMessage, List[ChatMessage]]:
        """
        Execute the automatic tool call loop:
        1. Generate tool responses from mock data
        2. Send tool responses back to AI
        3. Get final answer from AI
        
        Args:
            initial_tool_calls: List of tool calls from the initial AI response
            request_body: Original chat completion request
            assistant_message: Initial assistant message with tool_calls
            user_id: Current user ID
            request_id: Request ID for logging
            
        Returns:
            Tuple of (final_assistant_message, tool_responses_list)
        """
        tool_responses_list: List[ChatMessage] = []
        
        # Extract repo_name from request (try repo_name field first, then prompt_id)
        repo_name = request_body.repo_name
        if not repo_name and request_body.prompt_id and ':' in request_body.prompt_id:
            repo_name = request_body.prompt_id.split(':')[0]
        
        # Generate tool responses
        tool_responses_list = self._generate_tool_responses(
            initial_tool_calls,
            repo_name,
            user_id,
            request_id
        )
        
        # If we have tool responses, send them back to the AI to get the final answer
        if tool_responses_list:
            self.logger.info(
                "Sending tool responses back to AI for final answer",
                extra={
                    "request_id": request_id,
                    "tool_response_count": len(tool_responses_list)
                }
            )
            
            # Get final answer from AI
            final_assistant_message = await self._get_final_answer(
                request_body,
                assistant_message,
                tool_responses_list,
                user_id,
                request_id
            )
            
            return final_assistant_message, tool_responses_list
        
        # No tool responses generated, return original assistant message
        return assistant_message, tool_responses_list
    
    def _generate_tool_responses(
        self,
        tool_calls: List[Dict[str, Any]],
        repo_name: Optional[str],
        user_id: str,
        request_id: Optional[str] = None
    ) -> List[ChatMessage]:
        """
        Generate tool response messages using mock data from tool definitions.
        
        Args:
            tool_calls: List of tool calls to process
            repo_name: Repository name to load tools from
            user_id: Current user ID
            request_id: Request ID for logging
            
        Returns:
            List of tool response messages
        """
        tool_responses: List[ChatMessage] = []
        
        for tool_call in tool_calls:
            tool_name = None
            tool_call_id = None
            
            try:
                tool_name = tool_call.get("function", {}).get("name")
                tool_call_id = tool_call.get("id")
                
                if not tool_name or not tool_call_id:
                    self.logger.warning(
                        f"Skipping tool call - missing name or ID",
                        extra={"request_id": request_id}
                    )
                    continue
                
                # Try to load the tool definition from the tool service
                mock_response = None
                if repo_name:
                    try:
                        tool_def = self.tool_service.load_tool(tool_name, repo_name, user_id)
                        
                        # Extract tool call arguments
                        tool_arguments = {}
                        arguments_str = tool_call.get("function", {}).get("arguments", "{}")
                        try:
                            tool_arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
                        except json.JSONDecodeError:
                            self.logger.warning(
                                f"Failed to parse tool call arguments for {tool_name}",
                                extra={"request_id": request_id}
                            )
                        
                        # Fill in missing parameters with defaults from tool definition
                        complete_arguments = self._apply_default_parameters(tool_def, tool_arguments, request_id)
                        
                        # Get mock response (could use complete_arguments for conditional mocks in the future)
                        mock_response = self.tool_service.get_mock_response(tool_def)
                        
                        if mock_response:
                            self.logger.info(
                                f"Loaded mock response from tool definition for {tool_name}",
                                extra={
                                    "request_id": request_id,
                                    "tool_name": tool_name,
                                    "tool_call_id": tool_call_id,
                                    "provided_args": list(tool_arguments.keys()),
                                    "complete_args": list(complete_arguments.keys())
                                }
                            )
                    except Exception as tool_load_error:
                        self.logger.warning(
                            f"Could not load tool definition for {tool_name}: {tool_load_error}",
                            extra={"request_id": request_id}
                        )
                
                # If we have a mock response, create tool response message
                if mock_response:
                    tool_response = ChatMessage(
                        role="tool",
                        content=mock_response,
                        tool_call_id=tool_call_id
                    )
                    tool_responses.append(tool_response)
                else:
                    self.logger.warning(
                        f"No mock response available for tool: {tool_name}",
                        extra={
                            "request_id": request_id,
                            "tool_name": tool_name,
                            "repo_name": repo_name
                        }
                    )
                    
            except Exception as tool_error:
                error_context = {
                    "request_id": request_id,
                    "error": str(tool_error)
                }
                if tool_name:
                    error_context["tool_name"] = tool_name
                
                self.logger.warning(
                    f"Error processing tool call for mock data: {tool_error}",
                    extra=error_context
                )
                continue
        
        return tool_responses
    
    def _apply_default_parameters(
        self,
        tool_def,
        provided_arguments: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply default parameter values for any missing parameters in the tool call.
        
        Args:
            tool_def: Tool definition with parameter schemas
            provided_arguments: Arguments provided in the tool call
            request_id: Request ID for logging
            
        Returns:
            Complete arguments dict with defaults applied for missing parameters
        """
        complete_arguments = provided_arguments.copy()
        
        # Iterate through all defined parameters
        for param_name, param_schema in tool_def.parameters.properties.items():
            # If parameter is missing from provided arguments
            if param_name not in complete_arguments:
                # Check if parameter has a default value
                if param_schema.default is not None:
                    complete_arguments[param_name] = param_schema.default
                    self.logger.debug(
                        f"Applied default value for parameter '{param_name}'",
                        extra={
                            "request_id": request_id,
                            "tool_name": tool_def.name,
                            "param_name": param_name,
                            "default_value": param_schema.default
                        }
                    )
                # If no default but parameter is not required, skip it
                elif param_name not in tool_def.parameters.required:
                    self.logger.debug(
                        f"Optional parameter '{param_name}' not provided and has no default",
                        extra={
                            "request_id": request_id,
                            "tool_name": tool_def.name,
                            "param_name": param_name
                        }
                    )
                # If required but no default, log warning
                else:
                    self.logger.warning(
                        f"Required parameter '{param_name}' not provided and has no default",
                        extra={
                            "request_id": request_id,
                            "tool_name": tool_def.name,
                            "param_name": param_name
                        }
                    )
        
        return complete_arguments
    
    async def _get_final_answer(
        self,
        request_body: ChatCompletionRequest,
        assistant_message: ChatMessage,
        tool_responses: List[ChatMessage],
        user_id: str,
        request_id: Optional[str] = None
    ) -> ChatMessage:
        """
        Send tool responses back to AI and get final answer.
        
        Args:
            request_body: Original chat completion request
            assistant_message: Initial assistant message with tool_calls
            tool_responses: List of tool response messages
            user_id: Current user ID
            request_id: Request ID for logging
            
        Returns:
            Final assistant message with answer
        """
        # Build new messages list: original messages + assistant message + tool responses
        follow_up_messages = request_body.messages + [assistant_message] + tool_responses
        
        # Create a new request for the follow-up completion (without tools to avoid loops)
        follow_up_request = ChatCompletionRequest(
            messages=follow_up_messages,
            provider=request_body.provider,
            model=request_body.model,
            prompt_id=request_body.prompt_id,
            repo_name=request_body.repo_name,
            stream=False,
            temperature=request_body.temperature,
            max_tokens=request_body.max_tokens,
            top_p=request_body.top_p,
            frequency_penalty=request_body.frequency_penalty,
            presence_penalty=request_body.presence_penalty,
            stop=request_body.stop,
            tools=None  # Don't include tools in follow-up to avoid infinite loops
        )
        
        try:
            # Get final answer from AI
            final_content, _, _, _, _ = await self.chat_completion_service.execute_non_streaming_completion(
                follow_up_request,
                user_id
            )
            
            # Create final assistant message
            final_assistant_message = ChatMessage(
                role="assistant",
                content=final_content,
                tool_calls=None  # Final answer shouldn't have tool calls
            )
            
            self.logger.info(
                "Final answer received from AI after tool responses",
                extra={
                    "request_id": request_id,
                    "final_content_length": len(final_content) if final_content else 0
                }
            )
            
            return final_assistant_message
            
        except Exception as follow_up_error:
            self.logger.error(
                f"Error getting final answer after tool responses: {follow_up_error}",
                exc_info=True,
                extra={"request_id": request_id}
            )
            # If follow-up fails, return the original assistant message with tool calls
            # (frontend will at least see the tool calls)
            raise