"""
Constants for the PromptRepo backend application.
Contains shared constants used across multiple modules.
"""

PROVIDER_NAMES_MAP: dict[str, str] = {
    "anthropic": "Anthropic",
    "aws": "AWS",
    "azure": "Azure",
    "azureopenai": "Azure OpenAI",
    "cerebras": "Cerebras",
    "cohere": "Cohere",
    "databricks": "Databricks",
    "deepseek": "DeepSeek",
    "fireworks": "Fireworks",
    "google": "Google",
    "groq": "Groq",
    "huggingface": "Hugging Face",
    "inception": "Inception",
    "llama": "Llama",
    "lmstudio": "LM Studio",
    "llamafile": "Llama File",
    "llamacpp": "Llama CPP",
    "mistral": "Mistral",
    "moonshot": "Moonshot",
    "nebius": "Nebius",
    "ollama": "Ollama",
    "openai": "OpenAI",
    "openrouter": "OpenRouter",
    "portkey": "PortKey",
    "sambanova": "SambaNova",
    "together": "Together",
    "voyage": "Voyage",
    "watsonx": "WatsonX",
    "xai": "XAI",
    "perplexity": "Perplexity"
}