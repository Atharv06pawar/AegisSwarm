"""
Cluster Configuration model for AegisSwarm Distributed Executions.
"""

from pydantic import BaseModel, Field


class ClusterConfig(BaseModel):
    """Configuration options for the Distributed Worker Cluster."""
    heartbeat_interval_seconds: float = Field(default=5.0, ge=1.0)
    heartbeat_timeout_seconds: float = Field(default=15.0, ge=3.0)
    max_retries: int = Field(default=3, ge=0)
    retry_backoff_factor: float = Field(default=2.0, ge=1.0)
    default_worker_capacity: int = Field(default=10, ge=1)
    scheduling_strategy: str = Field(default="least_loaded", description="Strategy: round_robin, least_loaded, capability_aware, priority")
    storage_dir: str = Field(default="outputs/cluster")
