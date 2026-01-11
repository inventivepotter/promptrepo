"""
Chat completion service using ChatAgent.
"""
import json
import logging
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from any_agent import AgentTrace
from fastapi import HTTPException
from services.config.config_service import ConfigService
from services.artifacts.prompt.prompt_meta_service import PromptMetaService
from services.artifacts.prompt.models import PromptMeta
from agents.chat_agent.chat_agent import ChatAgent
from schemas import MessageSchema, UserMessageSchema, AIMessageSchema, SystemMessageSchema, ToolMessageSchema
from services.llm.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    TokenUsage,
    CostInfo,
)
from middlewares.rest.exceptions import (
    BadRequestException,
    ServiceUnavailableException,
    NotFoundException
)
from services.artifacts.tool.tool_execution_service import ToolExecutionService

logger = logging.getLogger(__name__)


class ChatCompletionService:
    """Service class for handling chat completions using ChatAgent."""
    
    def __init__(self, config_service: ConfigService, tool_execution_service: Optional[ToolExecutionService] = None, prompt_service: Optional[PromptMetaService] = None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.config_service = config_service
        self.tool_execution_service = tool_execution_service
        self.prompt_service = prompt_service
    

    def _get_api_details(self, provider: str, model: str, user_id: str) -> tuple[str, str | None]:
        """Get API key and base URL for the specified provider and model."""
        llm_configs = self.config_service.get_llm_configs(user_id=user_id) or []
            
        # Filter llm_configs to find matching provider and model
        matching_config = None
        for config in llm_configs:
            if config.provider == provider and config.model == model:
                matching_config = config
                break
            
        if not matching_config:
            raise HTTPException(
                    status_code=400,
                    detail=f"No configuration found for provider '{provider}' and model '{model}'"
                )
            
        # Get API key and base URL from the matching configuration
        api_key = matching_config.api_key
        api_base_url = matching_config.api_base_url if matching_config.api_base_url else None
        return api_key, api_base_url
    
    def _format_conversation_as_json(self, messages: List[MessageSchema]) -> str:
        """
        Format conversation messages as a JSON string.

        Args:
            messages: List of MessageSchema objects (already filtered to exclude system messages)

        Returns:
            JSON string representation of the conversation
        """
        conversation = []
        for msg in messages:
            conversation.append({
                "role": msg.role,
                "content": msg.content
            })
        return json.dumps(conversation, ensure_ascii=False)

    def _extract_tool_messages_from_trace(self, trace: AgentTrace) -> List[MessageSchema]:
        """
        Extract tool calls and tool messages from agent trace.

        Args:
            trace: The agent trace containing execution details

        Returns:
            List of MessageSchema objects representing tool interactions
        """
        tool_messages: List[MessageSchema] = []

        try:
            all_messages = trace.spans_to_messages()  # type: ignore
            self.logger.info(f"Extracted {len(all_messages) if all_messages else 0} messages from trace")

            for i, msg in enumerate(all_messages or []):
                self.logger.info(f"Message {i}: role={getattr(msg, 'role', 'no_role')}, content={getattr(msg, 'content', 'no_content')[:200]}")
                if hasattr(msg, 'role') and msg.role == 'assistant':
                    content = getattr(msg, 'content', '')
                    self.logger.info(f"Assistant message content type: {type(content)}, value: {content}")

                    # Try to parse tool calls from JSON string
                    if isinstance(content, str) and content.startswith('['):
                        try:
                            parsed = json.loads(content)
                            if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict) and 'tool.name' in parsed[0]:
                                # Tool calls
                                tool_calls = []
                                for item in parsed:
                                    tool_name = item.get('tool.name')
                                    tool_args = item.get('tool.args', {})
                                    if tool_name:
                                        from schemas import ToolCallSchema
                                        tool_call = ToolCallSchema(
                                            id=f"call_{tool_name}_{i}",
                                            name=tool_name,
                                            arguments=tool_args
                                        )
                                        tool_calls.append(tool_call)

                                if tool_calls:
                                    ai_msg = AIMessageSchema(content='', tool_calls=tool_calls)
                                    tool_messages.append(ai_msg)
                                    self.logger.info(f"Found {len(tool_calls)} tool calls")
                        except (json.JSONDecodeError, KeyError, IndexError):
                            pass  # Not tool calls, continue to next check

                    # Check for tool execution results
                    if isinstance(content, str) and content.startswith('[Tool ') and ' executed:' in content:
                        try:
                            import re
                            # Extract tool name and result from content like:
                            # "[Tool temp_tool executed: {"result": 23}]"
                            match = re.search(r'Tool (\w+) executed:\s*(\{.*?\})', content)
                            if match:
                                tool_name = match.group(1)
                                result_str = match.group(2)
                                result_data = json.loads(result_str)

                                tool_msg = ToolMessageSchema(
                                    content=json.dumps(result_data),
                                    tool_call_id=f"call_{tool_name}_{i}",
                                    tool_name=tool_name,
                                    is_error=False
                                )
                                tool_messages.append(tool_msg)
                                self.logger.info(f"Found tool execution result: {tool_msg}")
                        except Exception as e:
                            self.logger.warning(f"Failed to parse tool execution content: {e}")
                    # Skip other assistant messages for tool_calls extraction

        except Exception as e:
            self.logger.warning(f"Failed to extract tool messages from trace: {e}")

        return tool_messages
    
    async def _execute_completion_from_prompt_meta(
        self,
        prompt_meta: PromptMeta,
        user_id: str,
        tool_execution_service: Optional[ToolExecutionService] = None,
        conversation_history: Optional[List[MessageSchema]] = None,
        last_user_message: Optional[str] = None
    ) -> ChatCompletionResponse:
        """
        Private method to execute completion using PromptMeta.
        
        Args:
            prompt_meta: The prompt metadata containing all configuration
            user_id: User ID for API key lookup
            conversation_history: Optional conversation history (excluding last user message)
            last_user_message: The last user message to process (if None, uses prompt as single-turn)
            
        Returns:
            ChatCompletionResponse with content, metadata, and usage information
        """
        prompt_data = prompt_meta.prompt
        
        # Get API details
        api_key, api_base_url = self._get_api_details(
            prompt_data.provider,
            prompt_data.model,
            user_id=user_id
        )
        
        # Load tools from file paths if provided
        loaded_tools: Optional[List[Callable[..., Any]]] = None
        
        # Log tool loading conditions for debugging
        self.logger.info(
            f"Tool loading conditions: repo_name={prompt_meta.repo_name}, "
            f"tools={prompt_data.tools}, tools_count={len(prompt_data.tools) if prompt_data.tools else 0}, "
            f"tool_execution_service={'present' if (tool_execution_service or self.tool_execution_service) else 'missing'}"
        )
        
        # Use provided tool_execution_service or fall back to instance variable
        active_tool_service = tool_execution_service or self.tool_execution_service
        
        if prompt_meta.repo_name and prompt_data.tools and len(prompt_data.tools) > 0 and active_tool_service:
            try:
                self.logger.info(f"Loading {len(prompt_data.tools)} tools from paths: {prompt_data.tools}")
                loaded_tools = await active_tool_service.create_callable_tools(
                    tool_paths=prompt_data.tools,
                    repo_name=prompt_meta.repo_name,
                    user_id=user_id
                )
                if loaded_tools:
                    self.logger.info(f"Successfully loaded {len(loaded_tools)} callable tools")
                else:
                    self.logger.warning("Tool execution service returned empty tool list")
            except Exception as e:
                self.logger.error(f"Failed to create callable tools: {e}", exc_info=True)
                loaded_tools = None
        else:
            self.logger.warning(
                f"Tools not loaded - conditions not met. "
                f"repo_name={'present' if prompt_meta.repo_name else 'missing'}, "
                f"tools={'present' if prompt_data.tools else 'missing'}, "
                f"tool_execution_service={'present' if (tool_execution_service or self.tool_execution_service) else 'missing'}"
            )
        
        try:
            # Build model_args from prompt_data
            model_args: Dict[str, Any] = {}
            if prompt_data.temperature is not None:
                model_args["temperature"] = prompt_data.temperature
            if prompt_data.max_tokens is not None:
                model_args["max_tokens"] = prompt_data.max_tokens
            if prompt_data.top_p is not None:
                model_args["top_p"] = prompt_data.top_p
            if prompt_data.frequency_penalty is not None:
                model_args["frequency_penalty"] = prompt_data.frequency_penalty
            if prompt_data.presence_penalty is not None:
                model_args["presence_penalty"] = prompt_data.presence_penalty
            if prompt_data.stop is not None:
                model_args["stop"] = prompt_data.stop
            
            # Prepare the prompt to send to the agent
            # The system prompt goes in as instructions via ChatAgent's instructions parameter
            # We format conversation history as JSON and combine with the user message
            
            # Filter out system messages from conversation history
            filtered_history: Optional[List[MessageSchema]] = None
            if conversation_history:
                filtered_history = [
                    msg for msg in conversation_history
                    if not isinstance(msg, SystemMessageSchema)
                ]
                filtered_history = filtered_history if filtered_history else None
            
            # Build the final prompt string
            prompt_to_send: str = ""
            
            if filtered_history and last_user_message:
                # We have history and a new user message
                # Format: JSON conversation history + new user message
                history_json = self._format_conversation_as_json(filtered_history)
                prompt_to_send = f"Conversation History:\n{history_json}\n\nUser: {last_user_message}"
            elif last_user_message:
                # Just a single user message without history
                prompt_to_send = last_user_message
            else:
                # No user message provided, use the prompt itself as the query (single-turn)
                prompt_to_send = prompt_data.prompt
            
            # Create ChatAgent instance
            model_identifier = f"{prompt_data.provider}/{prompt_data.model}"
            chat_agent = await ChatAgent.create(
                model_id=model_identifier,
                api_key=api_key,
                api_base=api_base_url,
                instructions=prompt_data.prompt,
                model_args=model_args,
                tools=loaded_tools,
            )
            
            # Run the agent with the formatted prompt
            trace: AgentTrace = await chat_agent.run(prompt_to_send)
            
            # Log trace details for debugging
            self.logger.info(f"Agent trace final_output: {trace.final_output}")
            self.logger.info(f"Agent trace type: {type(trace.final_output)}")
            
            # Extract content from trace
            content = ""
            
            # Try to get content from final_output first
            if trace.final_output:
                if isinstance(trace.final_output, str):
                    content = trace.final_output
                elif isinstance(trace.final_output, dict):
                    content = str(trace.final_output.get("content", trace.final_output))
                else:
                    content = str(trace.final_output)
            
            # If final_output is empty, try to extract from messages in trace
            if not content:
                self.logger.info("final_output is empty, attempting to extract from trace messages")
                try:
                    messages = trace.spans_to_messages()
                    self.logger.info(f"Extracted {len(messages)} messages from trace")

                    # Get the last assistant message with actual content (not empty or tool calls)
                    for msg in reversed(messages):
                        self.logger.info(f"Message role: {msg.role}, content preview: {str(msg.content)[:100] if msg.content else 'empty'}")
                        if msg.role == "assistant":
                            msg_content = msg.content if isinstance(msg.content, str) else str(msg.content) if msg.content else ""
                            # Skip empty content and content that looks like tool call JSON
                            if msg_content and not msg_content.startswith('[{"tool.'):
                                content = msg_content
                                break
                except Exception as e:
                    self.logger.error(f"Failed to extract content from trace messages: {e}")

            # Log final content state for debugging
            self.logger.info(f"Final content extraction result: content_length={len(content) if content else 0}, content_preview={content[:100] if content else 'empty'}")

            # Extract token usage from trace
            token_usage: Optional[TokenUsage] = None
            if trace.tokens:
                token_usage = TokenUsage(
                    input_tokens=trace.tokens.input_tokens,
                    output_tokens=trace.tokens.output_tokens,
                    total_tokens=trace.tokens.total_tokens
                )
            
            # Extract cost information from trace
            cost_info: Optional[CostInfo] = None
            if trace.cost:
                cost_info = CostInfo(
                    input_cost=trace.cost.input_cost,
                    output_cost=trace.cost.output_cost,
                    total_cost=trace.cost.total_cost
                )
            
            # Extract duration from trace
            duration_ms = 0.0
            try:
                duration_ms = trace.duration.total_seconds() * 1000
            except (ValueError, AttributeError) as e:
                self.logger.warning(f"Could not extract duration from trace: {e}")
            
            finish_reason = "stop"
            
            # Extract tool calls and tool messages from trace
            tool_calls_list = self._extract_tool_messages_from_trace(trace)
            
            # Build the full conversation history including the response
            all_messages: Optional[List[MessageSchema]] = None
            if conversation_history:
                all_messages = list(conversation_history)
                if last_user_message:
                    all_messages.append(UserMessageSchema(content=last_user_message))
                # Ensure content is a string for AIMessageSchema
                final_content = content if isinstance(content, str) else str(content)
                all_messages.append(AIMessageSchema(content=final_content))
            
            return ChatCompletionResponse(
                content=content,
                finish_reason=finish_reason,
                usage=token_usage,
                cost=cost_info,
                duration_ms=duration_ms,
                tool_calls=tool_calls_list,
                messages=all_messages
            )
                
        except Exception as e:
            self.logger.error(f"Error in completion from prompt meta: {e}")
            raise ServiceUnavailableException(
                message=f"Completion error: {str(e)}",
                context={"provider": prompt_data.provider, "model": prompt_data.model}
            )
    
    async def execute_completion(
        self,
        request: ChatCompletionRequest,
        user_id: str
    ) -> ChatCompletionResponse:
        """
        Execute completion using PromptMeta from the request.

        Args:
            request: ChatCompletionRequest containing prompt_meta and optional conversation history
            user_id: User ID for API key lookup

        Returns:
            ChatCompletionResponse with content and metadata
        """
        # Extract last user message from conversation history if present
        last_user_msg: Optional[str] = None
        conversation_history: Optional[List[MessageSchema]] = None

        # Debug logging
        self.logger.info(f"[execute_completion] Received {len(request.messages) if request.messages else 0} messages")
        if request.messages:
            for i, msg in enumerate(request.messages):
                self.logger.info(f"[execute_completion] Message {i}: role={msg.role}, content={msg.content[:50] if msg.content else 'empty'}...")

        if request.messages:
            # Filter out system messages from the conversation
            from schemas import SystemMessageSchema
            non_system_messages = [
                msg for msg in request.messages
                if not isinstance(msg, SystemMessageSchema)
            ]
            
            # Find the last user message
            for msg in reversed(non_system_messages):
                if isinstance(msg, UserMessageSchema):
                    last_user_msg = msg.content
                    break
            
            # Get all messages except the last user message for history
            if last_user_msg and len(non_system_messages) > 1:
                conversation_history = [
                    msg for msg in non_system_messages
                    if not (isinstance(msg, UserMessageSchema) and msg.content == last_user_msg)
                ]

        # Debug logging for extracted data
        self.logger.info(f"[execute_completion] Extracted last_user_msg: {last_user_msg[:50] if last_user_msg else 'None'}...")
        self.logger.info(f"[execute_completion] Conversation history count: {len(conversation_history) if conversation_history else 0}")
        if conversation_history:
            for i, msg in enumerate(conversation_history):
                self.logger.info(f"[execute_completion] History {i}: role={msg.role}, content={msg.content[:50] if msg.content else 'empty'}...")

        # Execute using the private method
        return await self._execute_completion_from_prompt_meta(
            prompt_meta=request.prompt_meta,
            user_id=user_id,
            conversation_history=conversation_history,
            last_user_message=last_user_msg,
            tool_execution_service=self.tool_execution_service
        )
    
    async def execute_completion_from_saved_prompt(
        self,
        user_id: str,
        prompt_id: str,
        last_user_message: Optional[str] = None,
        conversation_history: Optional[List[MessageSchema]] = None
    ) -> ChatCompletionResponse:
        """
        Execute completion from a saved prompt by prompt_id.
        
        Args:
            user_id: User ID
            prompt_id: Prompt ID in format "repo_name:file_path"
            last_user_message: Optional last user message (if None, uses prompt as single-turn)
            conversation_history: Optional conversation history
            
        Returns:
            ChatCompletionResponse with content and metadata
            
        Raises:
            NotFoundException: If prompt is not found
            BadRequestException: If prompt_id format is invalid
        """
        if not self.prompt_service:
            raise ServiceUnavailableException(
                message="Prompt service not configured",
                context={"prompt_id": prompt_id}
            )
        
        # Parse prompt_id to extract repo_name and file_path
        try:
            parts = prompt_id.split(":", 1)
            if len(parts) != 2:
                raise BadRequestException(
                    message="Invalid prompt_id format. Expected 'repo_name:file_path'",
                    context={"prompt_id": prompt_id}
                )
            repo_name, file_path = parts
        except Exception as e:
            raise BadRequestException(
                message=f"Failed to parse prompt_id: {str(e)}",
                context={"prompt_id": prompt_id}
            )
        
        # Fetch the prompt using prompt service
        prompt_meta = await self.prompt_service.get(
            user_id=user_id,
            repo_name=repo_name,
            file_path=file_path
        )
        
        if not prompt_meta:
            raise NotFoundException(
                resource="Prompt",
                identifier=prompt_id
            )
        
        # Execute using the private method
        return await self._execute_completion_from_prompt_meta(
            prompt_meta=prompt_meta,
            user_id=user_id,
            conversation_history=conversation_history,
            last_user_message=last_user_message,
            tool_execution_service=self.tool_execution_service
        )

    def validate_provider_and_model(self, provider: str, model: str) -> None:
        """Validate provider and model fields."""
        if not provider or not provider.strip():
            raise BadRequestException(
                message="Provider field is required and cannot be empty"
            )
        
        if not model or not model.strip():
            raise BadRequestException(
                message="Model field is required and cannot be empty"
            )