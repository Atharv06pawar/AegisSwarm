"""
Pydantic v2 Data Models for AegisSwarm Distributed Worker Cluster.
"""

from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class WorkerState(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    STARTING = "STARTING"
    STOPPING = "STOPPING"
    DRAINING = "DRAINING"
    FAILED = "FAILED"


class WorkerNode(BaseModel):
    """
    Data model representing a physical or virtual worker node in the AegisSwarm cluster.
    """
    worker_id: UUID = Field(default_factory=uuid4, description="Unique worker node UUID4.")
    hostname: str = Field(default="localhost")
    ip_address: str = Field(default="127.0.0.1")
    provider_capabilities: List[str] = Field(default_factory=lambda: ["openai", "anthropic", "gemini", "ollama", "openrouter"])
    gpu_available: bool = Field(default=False)
    cpu_cores: int = Field(default=8)
    memory_gb: float = Field(default=16.0)
    current_load: int = Field(default=0, ge=0)
    maximum_capacity: int = Field(default=10, ge=1)
    status: WorkerState = Field(default=WorkerState.ONLINE)
    last_heartbeat: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    active_campaigns: List[str] = Field(default_factory=list)
    active_executions: List[str] = Field(default_factory=list)
    version: str = Field(default="2.0.0")


class ClusterTask(BaseModel):
    """Execution unit wrapper managed by DistributedScheduler and Dispatcher."""
    task_id: UUID = Field(default_factory=uuid4)
    campaign_id: Optional[str] = Field(default=None)
    session_id: Optional[str] = Field(default=None)
    attack_record_id: str = Field(...)
    provider: str = Field(...)
    model: str = Field(...)
    priority: int = Field(default=1, ge=1, le=10)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = Field(default="QUEUED")  # QUEUED, DISPATCHED, COMPLETED, FAILED, RETRYING
    assigned_worker_id: Optional[UUID] = Field(default=None)


class HeartbeatPayload(BaseModel):
    """Heartbeat telemetry update payload emitted periodically by worker processes."""
    worker_id: UUID = Field(...)
    cpu_usage_pct: float = Field(default=15.0)
    memory_usage_pct: float = Field(default=40.0)
    gpu_usage_pct: Optional[float] = Field(default=None)
    active_attacks: int = Field(default=0)
    queue_size: int = Field(default=0)
    provider_utilization: Dict[str, int] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ClusterStateModel(BaseModel):
    """Complete snapshot state of the worker cluster."""
    cluster_name: str = Field(default="aegisswarm-cluster-main")
    total_workers: int = Field(default=0)
    online_workers: int = Field(default=0)
    total_capacity: int = Field(default=0)
    active_executions: int = Field(default=0)
    queued_tasks: int = Field(default=0)
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
