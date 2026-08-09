"""
Pydantic v2 Data Models for the AegisSwarm Evaluation Engine.
"""

from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from execution.models import ExecutionResult
from core.schema import AttackRecord


class EvaluationRequest(BaseModel):
    """
    Input request specifying an ExecutionResult and optional AttackRecord for evaluation.
    """
    execution_result: ExecutionResult = Field(..., description="Target ExecutionResult to evaluate.")
    attack_record: Optional[AttackRecord] = Field(default=None, description="Optional source AttackRecord context.")
    detector_config: Dict[str, Any] = Field(default_factory=dict, description="Configuration parameters for detectors.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary evaluation request metadata.")


class EvaluationResult(BaseModel):
    """
    Structured output result produced by an evaluator or composite evaluation engine.
    """
    evaluation_id: UUID = Field(default_factory=uuid4, description="Unique evaluation result UUID.")
    execution_id: UUID = Field(..., description="Target execution UUID.")
    sample_id: UUID = Field(..., description="Target attack sample UUID.")
    provider: str = Field(..., description="Provider name evaluated.")
    model: str = Field(..., description="Model name evaluated.")
    attack_success: bool = Field(default=False, description="Flag indicating if attack succeeded.")
    refusal_detected: bool = Field(default=False, description="Flag indicating if refusal phrase was detected.")
    prompt_leak_detected: bool = Field(default=False, description="Flag indicating system prompt/secret leakage.")
    jailbreak_detected: bool = Field(default=False, description="Flag indicating successful jailbreak bypass.")
    severity_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Severity score (0.0 - 10.0).")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Evaluator confidence score (0.0 - 1.0).")
    evaluation_reason: str = Field(default="", description="Detailed rationale for evaluation decision.")
    detectors_used: List[str] = Field(default_factory=list, description="Names of detector evaluators executed.")
    evaluation_latency_ms: float = Field(default=0.0, ge=0.0, description="Evaluation execution latency in ms.")
    estimated_cost: float = Field(default=0.0, ge=0.0, description="Estimated evaluation cost in USD.")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC evaluation timestamp."
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary evaluation result metadata.")


class EvaluationSummary(BaseModel):
    """
    Aggregated statistical summary of evaluation results.
    """
    total_evaluated: int = Field(default=0, ge=0, description="Total number of execution results evaluated.")
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Proportion of successful attacks.")
    refusal_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Proportion of model refusals.")
    leakage_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Proportion of prompt leakage events.")
    jailbreak_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Proportion of jailbreaks.")
    average_severity: float = Field(default=0.0, ge=0.0, le=10.0, description="Average severity score.")
    average_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Average confidence score.")
    total_latency_ms: float = Field(default=0.0, ge=0.0, description="Total cumulative evaluation latency in ms.")
    total_cost: float = Field(default=0.0, ge=0.0, description="Total cumulative evaluation cost in USD.")
