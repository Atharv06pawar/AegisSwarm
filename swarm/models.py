"""
Pydantic v2 Data Models for the AegisSwarm Swarm Orchestration Engine.
"""

from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from core.schema import AttackRecord


class SwarmRequest(BaseModel):
    """
    Input request container specifying a swarm campaign parameters, target provider,
    and attack record workload.
    """
    swarm_id: UUID = Field(default_factory=uuid4, description="Unique swarm run UUID.")
    target_provider: str = Field(..., description="Target LLM provider identifier.")
    target_model: Optional[str] = Field(default=None, description="Optional target model override.")
    attack_records: List[AttackRecord] = Field(default_factory=list, description="Workload list of canonical AttackRecords.")
    execution_config: Dict[str, Any] = Field(default_factory=dict, description="Configuration for AttackExecutor.")
    planner_config: Dict[str, Any] = Field(default_factory=dict, description="Configuration for SwarmPlanner.")
    evaluation_config: Dict[str, Any] = Field(default_factory=dict, description="Configuration for EvaluationEngine.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary swarm metadata.")


class SwarmAgentResult(BaseModel):
    """
    Output model representing the result of a single swarm agent attack execution and evaluation.
    """
    agent_name: str = Field(..., description="Name of the swarm agent executed.")
    execution_id: UUID = Field(..., description="Execution ID produced by AttackExecutor.")
    evaluation_id: UUID = Field(..., description="Evaluation ID produced by EvaluationEngine.")
    attack_success: bool = Field(default=False, description="Evaluated attack success flag.")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Evaluator confidence.")
    severity: float = Field(default=0.0, ge=0.0, le=10.0, description="Evaluated severity score.")
    provider: str = Field(..., description="Provider name executed.")
    model: str = Field(..., description="Model name executed.")
    execution_time_ms: float = Field(default=0.0, ge=0.0, description="Execution time in ms.")


class SwarmResult(BaseModel):
    """
    Structured output result summarizing the full swarm campaign run.
    """
    swarm_id: UUID = Field(..., description="Swarm UUID.")
    started_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC start timestamp."
    )
    completed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC completion timestamp."
    )
    status: str = Field(default="completed", description="Status: 'completed', 'failed', or 'partially_completed'.")
    total_agents: int = Field(default=0, ge=0, description="Total agents planned.")
    completed_agents: int = Field(default=0, ge=0, description="Agents completed successfully.")
    failed_agents: int = Field(default=0, ge=0, description="Agents failed.")
    total_attacks: int = Field(default=0, ge=0, description="Total attacks executed.")
    successful_attacks: int = Field(default=0, ge=0, description="Successful attacks.")
    execution_ids: List[UUID] = Field(default_factory=list, description="List of generated execution IDs.")
    evaluation_ids: List[UUID] = Field(default_factory=list, description="List of generated evaluation IDs.")
    agent_results: List[SwarmAgentResult] = Field(default_factory=list, description="List of individual agent results.")
    average_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Average evaluation confidence.")
    average_severity: float = Field(default=0.0, ge=0.0, le=10.0, description="Average evaluation severity.")
    total_cost: float = Field(default=0.0, ge=0.0, description="Total USD cost incurred.")
    latency_ms: float = Field(default=0.0, ge=0.0, description="Total campaign duration in ms.")


class SwarmSummary(BaseModel):
    """
    Aggregated statistical summary of swarm executions.
    """
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall attack success rate.")
    failure_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall agent failure rate.")
    provider_distribution: Dict[str, int] = Field(default_factory=dict, description="Counts per provider.")
    attack_distribution: Dict[str, int] = Field(default_factory=dict, description="Counts per attack agent.")
    evaluator_distribution: Dict[str, int] = Field(default_factory=dict, description="Counts per detector.")
    cost: float = Field(default=0.0, ge=0.0, description="Total cost in USD.")
    latency: float = Field(default=0.0, ge=0.0, description="Total latency in ms.")
    mutation_success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Success rate of mutated prompts.")
    retry_success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Success rate of retried attacks.")
    learning_gain: float = Field(default=0.0, ge=0.0, description="Improvement delta in attack success rate.")
    average_attempts: float = Field(default=1.0, ge=1.0, description="Average attempts per attack record.")
    strategy_diversity: float = Field(default=0.0, ge=0.0, le=1.0, description="Entropy/diversity measure of strategies used.")
