from pydantic import BaseModel
from typing import List, Literal


class LlmConfig(BaseModel):
    """Configuration for an individual LLM provider"""
    provider: str
    model: str
    apiKey: str
    apiBaseUrl: str | None = None


class AppConfig(BaseModel):
    """Main application configuration"""
    hostingType: Literal["individual", "organization", "multi-tenant"]
    githubClientId: str
    githubClientSecret: str
    llmConfigs: List[LlmConfig]


# Schemas for LLM Providers endpoint
class ModelInfo(BaseModel):
    """Information about a specific model"""
    id: str
    name: str


class ProviderInfo(BaseModel):
    """Information about an LLM provider"""
    id: str
    name: str
    models: List[ModelInfo]


class ProvidersResponse(BaseModel):
    """Response for available providers endpoint"""
    providers: List[ProviderInfo]