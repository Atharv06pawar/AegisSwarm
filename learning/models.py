"""
Pydantic v2 Data Models for AegisSwarm Adaptive Attack Planning & Learning Engine.
"""

from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class LearningMemoryRecord(BaseModel):
    """
    Historical execution record stored in LearningMemory for adaptive optimization.
    """
    record_id: UUID = Field(default_factory=uuid4)
    attack_id: str = Field(...)
    dataset: str = Field(default="unknown")
    provider: str = Field(...)
    model: str = Field(...)
    taxonomy_node: str = Field(default="AUAO-GENERIC")
    agent: str = Field(default="direct_injection")
    mutation: str = Field(default="persona")
    evaluation_score: float = Field(default=0.0, ge=0.0, le=1.0)
    attack_success: bool = Field(default=False)
    execution_time: float = Field(default=0.0, ge=0.0)
    cost: float = Field(default=0.0, ge=0.0)
    retry_count: int = Field(default=0, ge=0)
    campaign_id: Optional[str] = Field(default=None)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AttackPlan(BaseModel):
    """
    Adaptive attack plan produced by AdaptivePlanner.
    """
    plan_id: UUID = Field(default_factory=uuid4)
    campaign_id: Optional[str] = Field(default=None)
    target_provider: str = Field(...)
    chosen_family: str = Field(default="persona")
    chosen_mutation: str = Field(default="persona_obfuscation")
    chosen_agents: List[str] = Field(default_factory=lambda: ["jailbreak"])
    estimated_cost: float = Field(default=0.001)
    estimated_success_prob: float = Field(default=0.75, ge=0.0, le=1.0)
    priority_rank: int = Field(default=1)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class GraphNode(BaseModel):
    """Node in the attack execution graph."""
    node_id: str = Field(...)
    node_type: str = Field(...)  # Prompt, Mutation, Provider, Evaluation, LearningState
    label: str = Field(...)
    attributes: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Edge connecting nodes in the attack execution graph."""
    edge_id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str = Field(...)
    target_id: str = Field(...)
    edge_type: str = Field(...)  # success, failure, retry, mutation, branch, provider_switch
    attributes: Dict[str, Any] = Field(default_factory=dict)


class AttackGraphModel(BaseModel):
    """Container representing a directed attack graph."""
    graph_id: UUID = Field(default_factory=uuid4)
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)


class ReplaySessionModel(BaseModel):
    """Replay execution session record."""
    replay_id: UUID = Field(default_factory=uuid4)
    original_campaign_id: str = Field(...)
    reproduced_success: bool = Field(default=True)
    historical_score: float = Field(default=0.0)
    replayed_score: float = Field(default=0.0)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
