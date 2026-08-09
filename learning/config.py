"""
Learning Engine Configuration options model.
"""

from typing import List
from pydantic import BaseModel, Field


class LearningConfig(BaseModel):
    """Configuration settings for the Adaptive Attack Planning & Learning Engine."""
    learning_rate: float = Field(default=0.1, ge=0.01, le=1.0)
    discount_factor: float = Field(default=0.9, ge=0.0, le=1.0)
    memory_capacity: int = Field(default=10000, ge=100)
    mutation_families: List[str] = Field(
        default_factory=lambda: [
            "persona", "encoding", "delimiter", "roleplay", "translation",
            "few_shot", "obfuscation", "typoglycemia", "unicode", "xml",
            "markdown", "json", "code_block", "cot_wrapper", "indirect_injection",
            "tool_injection", "multi_turn"
        ]
    )
    storage_dir: str = Field(default="outputs/learning")
