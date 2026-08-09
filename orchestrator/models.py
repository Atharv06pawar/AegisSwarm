"""
Pydantic v2 Data Models and Enums for AegisSwarm Master Autonomous Orchestrator.
"""

from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MissionState(str, Enum):
    """Lifecycle states for autonomous orchestrator missions."""
    CREATED = "CREATED"
    READY = "READY"
    PLANNING = "PLANNING"
    SCHEDULED = "SCHEDULED"
    EXECUTING = "EXECUTING"
    EVALUATING = "EVALUATING"
    LEARNING = "LEARNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"
    CANCELLED = "CANCELLED"


class MissionRequest(BaseModel):
    """Payload initiating a new master orchestrator mission."""
    mission_id: UUID = Field(default_factory=uuid4)
    objective: str = Field(...)
    target_provider: str = Field(default="openai")
    target_model: str = Field(default="gpt-4o")
    budget_usd: float = Field(default=25.0, ge=0.0)
    max_attacks: int = Field(default=10, ge=1)
    parallelism: int = Field(default=4, ge=1)


class MissionGraphNode(BaseModel):
    """Node in mission DAG representation."""
    node_id: str = Field(...)
    stage_name: str = Field(...) # e.g. reasoning, campaign, execution, evaluation, learning
    status: str = Field(default="PENDING")
    details: Dict[str, Any] = Field(default_factory=dict)


class MissionGraphEdge(BaseModel):
    """Directed edge in mission DAG."""
    source_id: str = Field(...)
    target_id: str = Field(...)
    edge_type: str = Field(default="dependency")


class MissionExecutionGraph(BaseModel):
    """DAG representation of mission stages."""
    mission_id: UUID = Field(...)
    nodes: List[MissionGraphNode] = Field(default_factory=list)
    edges: List[MissionGraphEdge] = Field(default_factory=list)


class MissionCheckpoint(BaseModel):
    """State snapshot for checkpointing and recovery."""
    checkpoint_id: UUID = Field(default_factory=uuid4)
    mission_id: UUID = Field(...)
    state: MissionState = Field(...)
    step_index: int = Field(default=0)
    completed_stages: List[str] = Field(default_factory=list)
    results_summary: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MissionModel(BaseModel):
    """Master record representing an autonomous mission."""
    mission_id: UUID = Field(default_factory=uuid4)
    objective: str = Field(...)
    state: MissionState = Field(default=MissionState.CREATED)
    target_provider: str = Field(default="openai")
    target_model: str = Field(default="gpt-4o")
    budget_usd: float = Field(default=25.0)
    attack_count: int = Field(default=0)
    successful_attacks: int = Field(default=0)
    failed_attacks: int = Field(default=0)
    cost_usd: float = Field(default=0.0)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MissionReportModel(BaseModel):
    """Summary report model for completed or failed missions."""
    mission_id: UUID = Field(...)
    objective: str = Field(...)
    state: MissionState = Field(...)
    providers_used: List[str] = Field(default_factory=list)
    attack_count: int = Field(default=0)
    success_rate: float = Field(default=0.0)
    failures: int = Field(default=0)
    retries: int = Field(default=0)
    learning_updates: int = Field(default=0)
    reasoning_summary: str = Field(default="")
    telemetry_summary: str = Field(default="")
    execution_graph_summary: str = Field(default="")
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class OrchestratorStatistics(BaseModel):
    """Summary metrics for the Orchestrator service."""
    total_missions: int = Field(default=0)
    active_missions: int = Field(default=0)
    completed_missions: int = Field(default=0)
    failed_missions: int = Field(default=0)
    avg_success_rate: float = Field(default=0.0)
