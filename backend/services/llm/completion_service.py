"""
Chat completion service with class-based architecture.
"""
import time
import logging
from typing import AsyncGenerator, cast, AsyncIterator, Optional, List, Dict, Any
from any_llm import acompletion
from any_llm.types.completion import ChatCompletion, ChatCompletionChunk
from fastapi import HTTPException
from services.config.config_service import ConfigService
from services.llm.models import (
    ChatCompletionRequest,
    ChatCompletionStreamResponse,
    ChatCompletionStreamChoice,
    ChatMessage,
    UsageStats,
    PromptTokensDetails,
    CompletionTokensDetails
)
from services.llm.providers.zai_llm_provider import ZAILlmProvider
from services.llm.providers.litellm_provider import LiteLLMProvider
from middlewares.rest.exceptions import (
    BadRequestException,
    ServiceUnavailableException
)

logger = logging.getLogger(__name__)


class ChatCompletionService:
    """Service class for handling chat completions with any-llm."""
    
    def __init__(self, config_service: ConfigService, tool_service=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.config_service = config_service
        self.tool_service = tool_service
    
    def _load_tools_from_paths(self, tool_paths: List[str], repo_name: Optional[str], user_id: str) -> List[Dict[str, Any]]:
        """Load tool definitions from file paths and convert to OpenAI function format."""
        if not self.tool_service or not tool_paths:
            return []
        
        tools = []
        for tool_path in tool_paths:
            try:
                # Extract tool name from file path
                # file:///.promptrepo/mock_tools/temp_tool.tool.yaml -> temp_tool
                tool_name = tool_path.split('/')[-1].replace('.tool.yaml', '').replace('.tool.yml', '')
                
                # Load tool definition from tool service
                tool_def = self.tool_service.load_tool(
                    tool_name=tool_name,
                    repo_name=repo_name or "default",
                    user_id=user_id
                )
                
                # Convert to OpenAI function format
                tool_dict = {
                    "type": "function",
                    "function": {
                        "name": tool_def.name,
                        "description": tool_def.description,
                        "parameters": tool_def.parameters.model_dump(exclude_none=True)
                    }
                }
                
                # Add mock_data if available for tool execution service
                if tool_def.mock and tool_def.mock.enabled:
                    tool_dict["mock_data"] = tool_def.mock.model_dump(exclude_none=True)
                
                tools.append(tool_dict)
                
            except Exception as e:
                self.logger.warning(f"Failed to load tool from path {tool_path}: {e}")
                continue
        
        return tools
    
    def build_completion_params(
        self,
        request: ChatCompletionRequest,
        api_key: str,
        api_base_url: str | None,
        stream: bool = False
    ) -> dict:
        """Build completion parameters for any-llm API call."""
        model_identifier = f"{request.provider}/{request.model}"
        completion_params = {
            "model": model_identifier,
            "messages": self._convert_to_any_llm_messages(request.messages),
            "api_key": api_key
        }
        
        if stream:
            completion_params["stream"] = True
        
        # Add API base URL if configured
        if api_base_url:
            completion_params["api_base"] = api_base_url
        
        # Add optional parameters if provided
        if request.temperature is not None:
            completion_params["temperature"] = request.temperature
        if request.max_tokens is not None:
            completion_params["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            completion_params["top_p"] = request.top_p
        if request.frequency_penalty is not None:
            completion_params["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            completion_params["presence_penalty"] = request.presence_penalty
        if request.stop is not None:
            completion_params["stop"] = request.stop
        
        return completion_params
    
    async def stream_completion(
        self,
        request: ChatCompletionRequest,
        user_id: str,
        completion_id: str
    ) -> AsyncGenerator[str, None]:
        """Generate streaming chat completion responses."""
        async for chunk in self._stream_completion_internal(request, user_id, completion_id):
            yield chunk
    
    async def _stream_completion_internal(
        self,
        request: ChatCompletionRequest,
        user_id: str,
        completion_id: str
    ) -> AsyncGenerator[str, None]:
        """Generate streaming chat completion responses."""
        # Validate system message is present
        self._validate_system_message(request.messages)

        api_key, api_base_url = self._get_api_details(request.provider, request.model, user_id=user_id)

        # Load tools from file paths if provided
        loaded_tools: Optional[List[Dict[str, Any]]] = None
        if request.tools and len(request.tools) > 0:
            repo_for_tools = request.repo_name
            if not repo_for_tools and request.prompt_id and ":" in request.prompt_id:
                repo_for_tools = request.prompt_id.split(":", 1)[0]
            loaded_tools = self._load_tools_from_paths(request.tools, repo_for_tools, user_id)

        try:
            # Handle Z.AI provider separately
            if request.provider == "zai":
                zai_service = ZAILlmProvider(
                    api_key=api_key,
                    api_base=api_base_url or "https://api.z.ai/api/coding/paas/v4"
                )
                async for chunk in zai_service.create_streaming_completion(request):
                    yield chunk
            elif request.provider == "litellm":
                # Handle LiteLLM provider separately
                if not api_base_url:
                    raise ServiceUnavailableException(
                        message="API base URL is required for LiteLLM provider",
                        context={"provider": request.provider}
                    )
                litellm_service = LiteLLMProvider(
                    api_key=api_key,
                    api_base=api_base_url
                )
                async for chunk in litellm_service.create_streaming_completion(request):
                    yield chunk
            else:
                # Handle other providers with any-llm
                # Add tools to completion params if available
                completion_params = self.build_completion_params(request, api_key, api_base_url, stream=True)
                if loaded_tools and len(loaded_tools) > 0:
                    completion_params["tools"] = loaded_tools
                stream_response = await acompletion(**completion_params)
                stream_iterator = cast(AsyncIterator[ChatCompletionChunk], stream_response)
                
                async for chunk in stream_iterator:
                    processed_chunk = await self._process_streaming_chunk(chunk, completion_id, request.model)
                    if processed_chunk:  # Only yield non-empty chunks
                        yield processed_chunk
                    
        except Exception as e:
            self.logger.error(f"Error in streaming completion: {e}")
            raise ServiceUnavailableException(
                message=f"Completion error: {str(e)}",
                context={"provider": request.provider, "model": request.model}
            )

    def _get_api_details(self, provider: str, model: str, user_id: str) -> tuple[str, str | None]:
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
    
    async def _process_streaming_chunk(
        self, 
        chunk, 
        completion_id: str, 
        model: str
    ) -> str:
        """Process a single streaming chunk."""
        try:
            # Extract content from chunk - any-llm streaming format may vary
            delta_content = ""
            finish_reason = None
            
            try:
                if hasattr(chunk, 'choices'):
                    choices = getattr(chunk, 'choices', None)
                    if choices and len(choices) > 0:
                        choice = choices[0]
                        if hasattr(choice, 'delta') and choice.delta:
                            delta_content = getattr(choice.delta, 'content', '') or ""
                        finish_reason = getattr(choice, 'finish_reason', None)
                elif hasattr(chunk, 'content'):
                    # Some streaming APIs return content directly
                    delta_content = getattr(chunk, 'content', '') or ""
            except (AttributeError, IndexError, TypeError):
                # Skip malformed chunks
                return ""
            
            # Create streaming response
            stream_response_chunk = ChatCompletionStreamResponse(
                id=completion_id,
                created=int(time.time()),
                model=model,
                choices=[
                    ChatCompletionStreamChoice(
                        index=0,
                        delta=ChatMessage(
                            role="assistant",
                            content=delta_content
                        ),
                        finish_reason=finish_reason
                    )
                ]
            )
            
            # Return the chunk as server-sent event
            return f"data: {stream_response_chunk.model_dump_json()}\n\n"
            
        except Exception as chunk_error:
            self.logger.warning(f"Error processing streaming chunk: {chunk_error}")
            return ""
    
    def process_usage_stats(self, usage_data) -> UsageStats | None:
        """Process usage statistics from any-llm response."""
        if not usage_data:
            return None
        
        try:
            # Convert prompt_tokens_details
            prompt_details = None
            if usage_data.prompt_tokens_details:
                prompt_details = PromptTokensDetails(
                    audio_tokens=getattr(usage_data.prompt_tokens_details, 'audio_tokens', None),
                    cached_tokens=getattr(usage_data.prompt_tokens_details, 'cached_tokens', None)
                )
            
            # Convert completion_tokens_details
            completion_details = None
            if usage_data.completion_tokens_details:
                completion_details = CompletionTokensDetails(
                    accepted_prediction_tokens=getattr(usage_data.completion_tokens_details, 'accepted_prediction_tokens', None),
                    audio_tokens=getattr(usage_data.completion_tokens_details, 'audio_tokens', None),
                    reasoning_tokens=getattr(usage_data.completion_tokens_details, 'reasoning_tokens', None),
                    rejected_prediction_tokens=getattr(usage_data.completion_tokens_details, 'rejected_prediction_tokens', None)
                )
            
            # Create UsageStats with proper types
            return UsageStats(
                prompt_tokens=usage_data.prompt_tokens,
                completion_tokens=usage_data.completion_tokens,
                total_tokens=usage_data.total_tokens,
                prompt_tokens_details=prompt_details,
                completion_tokens_details=completion_details
            )
        except Exception as usage_error:
            self.logger.warning(f"Error processing usage statistics: {usage_error}")
            return None
    
    async def execute_non_streaming_completion(
        self,
        request: ChatCompletionRequest,
        user_id: str
    ) -> tuple[str, str | None, UsageStats | None, float, Optional[List[Dict[str, Any]]]]:
        """Execute non-streaming completion and return content, finish_reason, usage stats, inference time, and tool_calls."""
        return await self._execute_non_streaming_completion_internal(request, user_id)
    
    async def _execute_non_streaming_completion_internal(
        self,
        request: ChatCompletionRequest,
        user_id: str
    ) -> tuple[str, str | None, UsageStats | None, float, Optional[List[Dict[str, Any]]]]:
        """Internal method for non-streaming completion."""
        # Validate system message is present
        self._validate_system_message(request.messages)

        api_key, api_base_url = self._get_api_details(request.provider, request.model, user_id=user_id)
        
        # Load tools from file paths if provided
        loaded_tools: Optional[List[Dict[str, Any]]] = None
        if request.tools and len(request.tools) > 0:
            repo_for_tools = request.repo_name
            if not repo_for_tools and request.prompt_id and ":" in request.prompt_id:
                repo_for_tools = request.prompt_id.split(":", 1)[0]
            loaded_tools = self._load_tools_from_paths(request.tools, repo_for_tools, user_id)
        
        try:
            # Handle Z.AI provider separately
            if request.provider == "zai":
                zai_service = ZAILlmProvider(
                    api_key=api_key,
                    api_base=api_base_url or "https://api.z.ai/api/coding/paas/v4"
                )
                response = await zai_service.create_completion(request, stream=False)
                
                # Extract content, finish reason, and tool_calls from Z.AI response
                content = ""
                finish_reason = None
                tool_calls_list: Optional[List[Dict[str, Any]]] = None
                
                if response.choices and len(response.choices) > 0:
                    choice = response.choices[0]
                    content = choice.message.content or ""
                    finish_reason = choice.finish_reason
                    # Convert tool_calls to dict format
                    if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                        tool_calls_list = []
                        for tc in choice.message.tool_calls:
                            if hasattr(tc, 'model_dump'):
                                tool_calls_list.append(tc.model_dump())  # type: ignore
                            else:
                                tool_calls_list.append(dict(tc))  # type: ignore
                
                if not content and not tool_calls_list:
                    self.logger.error(f"No content or tool_calls extracted from Z.AI response")
                    raise HTTPException(
                        status_code=500,
                        detail="Unexpected response format from Z.AI completion API"
                    )
                
                return content, finish_reason, response.usage, response.inference_time_ms or 0.0, tool_calls_list
            elif request.provider == "litellm":
                # Handle LiteLLM provider separately
                if not api_base_url:
                    raise ServiceUnavailableException(
                        message="API base URL is required for LiteLLM provider",
                        context={"provider": request.provider}
                    )
                litellm_service = LiteLLMProvider(
                    api_key=api_key,
                    api_base=api_base_url
                )
                response = await litellm_service.create_completion(request, stream=False)
                
                # Extract content, finish reason, and tool_calls from LiteLLM response
                content = ""
                finish_reason = None
                tool_calls_list: Optional[List[Dict[str, Any]]] = None
                
                if response.choices and len(response.choices) > 0:
                    choice = response.choices[0]
                    content = choice.message.content or ""
                    finish_reason = choice.finish_reason
                    # Convert tool_calls to dict format
                    if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                        tool_calls_list = []
                        for tc in choice.message.tool_calls:
                            if hasattr(tc, 'model_dump'):
                                tool_calls_list.append(tc.model_dump())  # type: ignore
                            else:
                                tool_calls_list.append(dict(tc))  # type: ignore
                
                if not content and not tool_calls_list:
                    self.logger.error(f"No content or tool_calls extracted from LiteLLM response")
                    raise HTTPException(
                        status_code=500,
                        detail="Unexpected response format from LiteLLM completion API"
                    )
                
                return content, finish_reason, response.usage, response.inference_time_ms or 0.0, tool_calls_list
            else:
                # Handle other providers with any-llm
                completion_params = self.build_completion_params(request, api_key, api_base_url, stream=False)
                # Add tools to completion params if available
                if loaded_tools and len(loaded_tools) > 0:
                    completion_params["tools"] = loaded_tools
                
                # Track inference timing
                start_time = time.time()
                
                # Call any-llm completion (non-streaming)
                completion_result = await acompletion(**completion_params)
                
                # Calculate inference time in milliseconds
                inference_time_ms = (time.time() - start_time) * 1000
                
                response = cast(ChatCompletion, completion_result)  # Safe because stream=False
                
                # Handle response - any-llm follows OpenAI format for non-streaming
                content = ""
                finish_reason = None
                tool_calls_list: Optional[List[Dict[str, Any]]] = None
                
                # any-llm returns ChatCompletion object with choices[0].message.content
                if hasattr(response, 'choices') and response.choices and len(response.choices) > 0:
                    choice = response.choices[0]
                    
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        content = choice.message.content or ""
                    
                    if hasattr(choice, 'message') and hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                        # Convert tool_calls to dict format
                        tool_calls_list = []
                        for tc in choice.message.tool_calls:
                            if hasattr(tc, 'model_dump'):
                                tool_calls_list.append(tc.model_dump())  # type: ignore
                            else:
                                tool_calls_list.append(dict(tc))  # type: ignore
                        
                    if hasattr(choice, 'finish_reason'):
                        finish_reason = choice.finish_reason
                else:
                    self.logger.error(f"No choices in response or choices is empty. Response: {response}")
                
                if not content and not tool_calls_list:
                    self.logger.error(f"No content or tool_calls extracted from response")
                    raise HTTPException(
                        status_code=500,
                        detail="Unexpected response format from completion API"
                    )
                
                # Process usage statistics
                usage_stats = self.process_usage_stats(response.usage)
                
                return content, finish_reason, usage_stats, inference_time_ms, tool_calls_list
                
        except Exception as e:
            self.logger.error(f"Error in non-streaming completion: {e}")
            raise ServiceUnavailableException(
                message=f"Completion error: {str(e)}",
                context={"provider": request.provider, "model": request.model}
            )

    def _validate_system_message(self, messages: list[ChatMessage]) -> None:
        """Validate that the first message is a system message."""
        if not messages:
            raise BadRequestException(
                message="Messages array cannot be empty. A system message is required to define the AI assistant's behavior."
            )
        
        if messages[0].role != "system":
            raise BadRequestException(
                message="First message must be a system message with role 'system'. Please provide a system prompt to define the AI assistant's behavior."
            )
            
        if not messages[0].content or not messages[0].content.strip():
            raise BadRequestException(
                message="System message content cannot be empty. Please provide a valid system prompt."
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

    def _convert_to_any_llm_messages(self, messages: list[ChatMessage]) -> list[dict]:
        """Convert our ChatMessage format to any-llm format."""
        converted_messages = []
        for msg in messages:
            any_llm_msg: dict = {
                "role": msg.role,
                "content": msg.content
            }
            if msg.tool_call_id:
                any_llm_msg["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls:
                any_llm_msg["tool_calls"] = msg.tool_calls
            converted_messages.append(any_llm_msg)
        return converted_messages