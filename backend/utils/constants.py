"""
Constants for the PromptRepo backend application.
Contains shared constants used across multiple modules.
"""

from typing import Any


PROVIDER_NAMES_MAP: dict[str, dict[str, Any]] = {
    "anthropic": {"name": "Anthropic", "custom_api_base": False},
    "azure": {"name": "Azure", "custom_api_base": True},
    "azureopenai": {"name": "Azure OpenAI", "custom_api_base": False},
    "bedrock": {"name": "AWS Bedrock", "custom_api_base": False},
    "cerebras": {"name": "Cerebras", "custom_api_base": False},
    "cohere": {"name": "Cohere", "custom_api_base": False},
    "databricks": {"name": "Databricks", "custom_api_base": False},
    "deepseek": {"name": "DeepSeek", "custom_api_base": False},
    "fireworks": {"name": "Fireworks", "custom_api_base": False},
    "gemini": {"name": "Google Gemini", "custom_api_base": False},
    "groq": {"name": "Groq", "custom_api_base": False},
    "huggingface": {"name": "Hugging Face", "custom_api_base": False},
    "inception": {"name": "Inception", "custom_api_base": False},
    "llama": {"name": "Llama", "custom_api_base": True},
    "lmstudio": {"name": "LM Studio", "custom_api_base": True},
    "llamafile": {"name": "Llama File", "custom_api_base": True},
    "llamacpp": {"name": "Llama CPP", "custom_api_base": True},
    "mistral": {"name": "Mistral", "custom_api_base": False},
    "moonshot": {"name": "Moonshot", "custom_api_base": False},
    "nebius": {"name": "Nebius", "custom_api_base": False},
    "ollama": {"name": "Ollama", "custom_api_base": True},
    "openai": {"name": "OpenAI", "custom_api_base": False},
    "openrouter": {"name": "OpenRouter", "custom_api_base": False},
    "perplexity": {"name": "Perplexity", "custom_api_base": False},
    "portkey": {"name": "PortKey", "custom_api_base": False},
    "sagemaker": {"name": "SageMaker", "custom_api_base": False},
    "sambanova": {"name": "SambaNova", "custom_api_base": False},
    "together": {"name": "Together", "custom_api_base": False},
    "vertexai": {"name": "Vertex AI", "custom_api_base": False},
    "voyage": {"name": "Voyage", "custom_api_base": False},
    "watsonx": {"name": "WatsonX", "custom_api_base": False},
    "xai": {"name": "XAI", "custom_api_base": False},
    "zai": {"name": "Z.AI", "custom_api_base": False},
    "litellm": {"name": "LiteLLM", "custom_api_base": True},
    "syntheticsnew": {"name": "Synthetics.New", "custom_api_base": False}
}