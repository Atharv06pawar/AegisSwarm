"""
Reasoning Engine Configuration settings model.
"""

from pydantic import BaseModel, Field


class ReasoningConfig(BaseModel):
    """Configuration options for the Semantic Reasoning & Strategy Engine."""
    top_k_retrieval: int = Field(default=5, ge=1)
    similarity_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    min_candidates: int = Field(default=5, ge=5)
    confidence_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    storage_dir: str = Field(default="outputs/reasoning")
