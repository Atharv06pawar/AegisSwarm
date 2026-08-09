"""
Configuration settings model for Orchestrator subsystem.
"""

from pydantic import BaseModel, Field


class OrchestratorConfig(BaseModel):
    """Configuration options for the Master Autonomous Orchestrator."""
    max_parallel_tasks: int = Field(default=10, ge=1)
    max_retries: int = Field(default=3, ge=0)
    checkpoint_interval_sec: float = Field(default=5.0, ge=0.1)
    storage_dir: str = Field(default="outputs/orchestrator")
