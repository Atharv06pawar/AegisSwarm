"""
Immutable Pydantic v2 Data Models for the AegisSwarm Distributed Campaign Engine.
"""

from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from core.schema import AttackRecord


class CampaignStatus(str, Enum):
    """Execution status enum for campaigns."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class CampaignObjective(BaseModel):
    """Specification of a campaign objective."""
    name: str = Field(..., description="Short title of the campaign objective.")
    description: str = Field(default="", description="Detailed description of campaign goal.")
    target_taxonomies: List[str] = Field(default_factory=list, description="Target AUAO taxonomy nodes.")
    target_success_rate: float = Field(default=0.8, ge=0.0, le=1.0, description="Target attack success threshold.")


class CampaignTarget(BaseModel):
    """Target provider and model specification for worker dispatching."""
    provider: str = Field(..., description="LLM provider name (e.g. 'openai', 'anthropic').")
    model: Optional[str] = Field(default=None, description="Optional target model override.")
    max_concurrency: int = Field(default=4, ge=1, description="Worker pool concurrency limit for this target.")


class CampaignBudget(BaseModel):
    """Budget limits and expenditure tracker for a campaign."""
    max_cost_usd: float = Field(default=100.0, ge=0.0, description="Maximum total USD cost limit.")
    max_tokens: int = Field(default=1_000_000, ge=0, description="Maximum total token expenditure.")
    current_cost_usd: float = Field(default=0.0, ge=0.0, description="Accumulated cost in USD.")
    current_tokens: int = Field(default=0, ge=0, description="Accumulated tokens consumed.")
    daily_limit_usd: float = Field(default=50.0, ge=0.0, description="Daily USD spending limit.")


class CampaignWorker(BaseModel):
    """State tracking model for an individual campaign worker node."""
    worker_id: UUID = Field(default_factory=uuid4, description="Unique worker UUID.")
    provider: str = Field(..., description="Target provider assigned to this worker.")
    model: str = Field(default="default", description="Target model assigned.")
    status: str = Field(default="idle", description="Status: 'idle', 'busy', 'offline', 'error'.")
    current_attack: Optional[str] = Field(default=None, description="Currently executing attack ID.")
    current_campaign: str = Field(..., description="Parent campaign UUID.")
    last_heartbeat: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC heartbeat timestamp."
    )


class CampaignConfig(BaseModel):
    """Configuration specification describing a full campaign run."""
    campaign_id: UUID = Field(default_factory=uuid4, description="Unique campaign UUID4.")
    name: str = Field(..., description="Human-readable campaign title.")
    creation_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC creation timestamp."
    )
    objective: CampaignObjective = Field(..., description="Campaign objective specification.")
    targets: List[CampaignTarget] = Field(default_factory=list, description="Target providers and models.")
    selected_datasets: List[str] = Field(default_factory=list, description="Target dataset names.")
    swarm_agents: List[str] = Field(default_factory=list, description="Selected attacker agent names.")
    maximum_attacks: int = Field(default=100, ge=1, description="Maximum attack count ceiling.")
    parallel_workers: int = Field(default=4, ge=1, description="Total parallel worker worker pool count.")
    budget: CampaignBudget = Field(default_factory=CampaignBudget, description="Campaign budget settings.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata dictionary.")


class CampaignProgress(BaseModel):
    """Live progress counter model."""
    total_attacks: int = Field(default=0, ge=0)
    completed_attacks: int = Field(default=0, ge=0)
    failed_attacks: int = Field(default=0, ge=0)
    running_attacks: int = Field(default=0, ge=0)
    queued_attacks: int = Field(default=0, ge=0)
    percentage: float = Field(default=0.0, ge=0.0, le=100.0)


class CampaignEvent(BaseModel):
    """Event model for campaign audit timelines."""
    event_id: UUID = Field(default_factory=uuid4)
    campaign_id: UUID = Field(...)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str = Field(...)
    details: Dict[str, Any] = Field(default_factory=dict)


class CampaignMetrics(BaseModel):
    """Comprehensive performance telemetry metrics model."""
    total_attacks: int = Field(default=0, ge=0)
    completed_attacks: int = Field(default=0, ge=0)
    failed_attacks: int = Field(default=0, ge=0)
    running_attacks: int = Field(default=0, ge=0)
    queued_attacks: int = Field(default=0, ge=0)
    provider_usage: Dict[str, int] = Field(default_factory=dict)
    average_latency: float = Field(default=0.0, ge=0.0)
    p95_latency: float = Field(default=0.0, ge=0.0)
    p99_latency: float = Field(default=0.0, ge=0.0)
    average_cost: float = Field(default=0.0, ge=0.0)
    tokens_consumed: int = Field(default=0, ge=0)
    attacks_per_minute: float = Field(default=0.0, ge=0.0)
    campaign_duration_ms: float = Field(default=0.0, ge=0.0)
    retry_count: int = Field(default=0, ge=0)
    mutation_count: int = Field(default=0, ge=0)
    evaluation_count: int = Field(default=0, ge=0)
    learning_gain: float = Field(default=0.0, ge=0.0)


class CampaignCheckpoint(BaseModel):
    """Snapshot model for campaign state recovery."""
    campaign_id: UUID = Field(...)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: CampaignStatus = Field(...)
    completed_attack_ids: List[str] = Field(default_factory=list)
    remaining_attack_ids: List[str] = Field(default_factory=list)
    current_budget: CampaignBudget = Field(default_factory=CampaignBudget)
    worker_states: List[Dict[str, Any]] = Field(default_factory=list)


class CampaignResult(BaseModel):
    """Structured campaign output model."""
    campaign_id: UUID = Field(...)
    started_at: str = Field(...)
    completed_at: str = Field(...)
    status: CampaignStatus = Field(...)
    progress: CampaignProgress = Field(...)
    metrics: CampaignMetrics = Field(...)
    budget: CampaignBudget = Field(...)


class CampaignSummary(BaseModel):
    """High-level statistical summary model."""
    campaign_id: UUID = Field(...)
    name: str = Field(...)
    status: CampaignStatus = Field(...)
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    total_cost: float = Field(default=0.0, ge=0.0)
    total_tokens: int = Field(default=0, ge=0)
    duration_ms: float = Field(default=0.0, ge=0.0)
