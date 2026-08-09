"""
Pydantic v2 data models for the AegisSwarm Provider Abstraction Layer.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    """
    Standard request model for language model generation.
    Supports system prompt, user prompt, multi-turn conversation, temperature, top_p,
    max_tokens, seed, tools, attachments, model, and metadata.
    """
    system_prompt: Optional[str] = Field(default=None, description="System instruction prompt.")
    user_prompt: str = Field(default="", description="Primary user input prompt.")
    conversation: List[Dict[str, Any]] = Field(default_factory=list, description="Prior conversation turn history.")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature.")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="Nucleus sampling top-p parameter.")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Maximum tokens to generate.")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducible generation.")
    tools: List[Dict[str, Any]] = Field(default_factory=list, description="Available tool definitions.")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Multi-modal input attachments (images, PDFs).")
    model: Optional[str] = Field(default=None, description="Target model override.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary execution metadata.")


class GenerationResponse(BaseModel):
    """
    Standard response model for language model generation.
    Contains completion text, provider metadata, usage accounting, timing, and cost metrics.
    """
    completion: str = Field(..., description="Generated text completion.")
    provider: str = Field(..., description="Provider name (e.g. openai, anthropic, ollama).")
    model: str = Field(..., description="Model name executed.")
    finish_reason: str = Field(default="stop", description="Completion finish reason (stop, length, tool_calls).")
    latency_ms: float = Field(default=0.0, ge=0.0, description="Execution latency in milliseconds.")
    tokens_prompt: int = Field(default=0, ge=0, description="Prompt token count.")
    tokens_completion: int = Field(default=0, ge=0, description="Completion token count.")
    cost: float = Field(default=0.0, ge=0.0, description="Estimated execution cost in USD.")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC creation timestamp."
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific response metadata.")


class ProviderHealth(BaseModel):
    """
    Health check status response for a provider adapter.
    """
    status: str = Field(default="ok", description="Health status: 'ok', 'degraded', or 'unavailable'.")
    provider: str = Field(..., description="Provider name.")
    latency_ms: float = Field(default=0.0, ge=0.0, description="Health check round-trip latency in ms.")
    message: str = Field(default="Healthy", description="Status details or error description.")
