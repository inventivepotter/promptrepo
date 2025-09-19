from pydantic import BaseModel, Field
from typing import List

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