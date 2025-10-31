# AnyLLM Wrapper Documentation

## Overview

The `any_llm_wrapper` module provides a unified interface for working with both built-in AnyLLM providers and custom providers (ZAI and LiteLLM). This wrapper eliminates the need for special if-conditions when using custom providers.

## Architecture

### Key Components

1. **`services/llm/any_llm_wrapper.py`** - Main wrapper module
2. **`services/llm/providers/zai_llm_provider.py`** - ZAI custom provider
3. **`services/llm/providers/litellm_provider.py`** - LiteLLM custom provider

### Design Pattern

Both custom providers extend the `AnyLLM` base class from the `any_llm` library, following the same pattern as built-in providers like Ollama. This ensures:

- **Unified Interface**: All providers use the same `acompletion()` and `alist_models()` methods
- **No Special Conditions**: Services don't need provider-specific logic
- **Easy Extension**: New providers can be added by extending `AnyLLM`

## Usage

### Basic Completion

```python
from services.llm.any_llm_wrapper import acompletion

# Using a custom provider (ZAI)
response = await acompletion(
    model="zai/glm-4.6",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    api_key="your-api-key",
    api_base="https://api.z.ai/api/coding/paas/v4"
)

# Using a built-in provider (OpenAI)
response = await acompletion(
    model="openai/gpt-4",
    messages=[...],
    api_key="your-openai-key"
)
```

### List Models

```python
from services.llm.any_llm_wrapper import alist_models

# List models from custom provider
models = await alist_models(
    provider="zai",
    api_key="your-api-key",
    api_base="https://api.z.ai/api/coding/paas/v4"
)

# List models from built-in provider
models = await alist_models(
    provider="openai",
    api_key="your-openai-key"
)
```

### Streaming Completions

```python
# Streaming works the same way for all providers
stream = await acompletion(
    model="zai/glm-4.6",
    messages=[...],
    api_key="your-api-key",
    stream=True
)

async for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## Supported Providers

### Built-in Providers (via any_llm)
- OpenAI
- Anthropic
- Google (Gemini)
- Ollama
- Groq
- And many more...

### Custom Providers
- **ZAI** (`zai`) - Z.AI language models
- **LiteLLM** (`litellm`) - LiteLLM proxy server

## Helper Functions

### `get_supported_providers()`
Returns a list of all supported providers (built-in + custom).

```python
from services.llm.any_llm_wrapper import get_supported_providers

providers = get_supported_providers()
# Returns: ['openai', 'anthropic', ..., 'zai', 'litellm']
```

### `is_custom_provider(provider)`
Checks if a provider is a custom provider.

```python
from services.llm.any_llm_wrapper import is_custom_provider

is_custom_provider("zai")      # True
is_custom_provider("openai")   # False
```

## Adding New Custom Providers

To add a new custom provider:

1. **Create Provider Class**
   ```python
   # services/llm/providers/my_provider.py
   from any_llm.any_llm import AnyLLM
   
   class MyProvider(AnyLLM):
       PROVIDER_NAME = "myprovider"
       # Implement required methods
       def _init_client(self, api_key, api_base, **kwargs):
           ...
       
       async def _acompletion(self, params, **kwargs):
           ...
       
       async def _alist_models(self, **kwargs):
           ...
   ```

2. **Register in Wrapper**
   ```python
   # services/llm/any_llm_wrapper.py
   from services.llm.providers.my_provider import MyProvider
   
   CUSTOM_PROVIDERS = {
       "zai": ZAILlmProvider,
       "litellm": LiteLLMProvider,
       "myprovider": MyProvider,  # Add here
   }
   ```

3. **Use It**
   ```python
   response = await acompletion(
       model="myprovider/model-name",
       messages=[...],
       api_key="key"
   )
   ```

## Integration with Services

### Completion Service
The `ChatCompletionService` uses the wrapper transparently:

```python
# services/llm/completion_service.py
from services.llm.any_llm_wrapper import acompletion

# Works for all providers without special conditions
completion_result = await acompletion(**completion_params)
```

### LLM Provider Service  
The `LLMProviderService` uses the wrapper for model listing:

```python
# services/llm/llm_provider_service.py
from services.llm.any_llm_wrapper import alist_models

# Works for all providers
raw_models = await alist_models(provider_id, api_key, api_base=api_base)
```

## Benefits

1. **Simplified Code**: No provider-specific if-conditions in service layer
2. **Maintainability**: Consistent interface across all providers
3. **Extensibility**: Easy to add new providers
4. **Type Safety**: Full type hints and Pydantic models
5. **Testing**: Unified mocking and testing approach

## Testing

Run the wrapper tests:

```bash
cd backend
uv run pytest tests/services/llm/test_any_llm_wrapper.py -v
```

Manual testing with ZAI provider:

```bash
cd backend
# Edit test_zai_manual.py to add your API key
python test_zai_manual.py
```

## Migration from Direct any_llm Usage

### Before
```python
from any_llm import acompletion

# Had to check provider type
if provider == "zai":
    # Special ZAI logic
    ...
elif provider == "litellm":
    # Special LiteLLM logic
    ...
else:
    # Use any_llm
    response = await acompletion(...)
```

### After
```python
from services.llm.any_llm_wrapper import acompletion

# Works for all providers
response = await acompletion(
    model=f"{provider}/{model}",
    messages=messages,
    api_key=api_key
)
```

## Implementation Details

### Provider Detection
The wrapper extracts the provider from the model string:
- `"zai/glm-4.6"` → provider: `zai`, model: `glm-4.6`
- `"openai/gpt-4"` → provider: `openai`, model: `gpt-4`

### Custom Provider Flow
1. User calls `acompletion(model="zai/glm-4.6", ...)`
2. Wrapper detects `zai` is a custom provider
3. Instantiates `ZAILlmProvider` with provided credentials
4. Calls provider's `acompletion()` method
5. Provider converts response to OpenAI format
6. Returns unified response

### Built-in Provider Flow
1. User calls `acompletion(model="openai/gpt-4", ...)`
2. Wrapper detects `openai` is not a custom provider
3. Delegates to `any_llm.api.acompletion()`
4. Returns response from any_llm

## Error Handling

The wrapper preserves error handling from underlying providers:

```python
try:
    response = await acompletion(...)
except Exception as e:
    # Errors propagate from the provider
    logger.error(f"Completion error: {e}")
```

## Performance Considerations

- **No Overhead**: Direct delegation to providers, no intermediate processing
- **Connection Reuse**: Providers manage their own client connections
- **Async Support**: Full async/await support for all operations