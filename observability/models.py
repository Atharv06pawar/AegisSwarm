"""
Pydantic v2 Data Models for AegisSwarm Telemetry, Monitoring & Observability Platform.
"""

from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class TelemetryEvent(BaseModel):
    """
    Immutable, structured telemetry event model emitted across all AegisSwarm subsystems.
    """
    event_id: UUID = Field(default_factory=uuid4, description="Unique event UUID4.")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp."
    )
    session_id: Optional[str] = Field(default=None, description="Optional ExecutionSession ID.")
    campaign_id: Optional[str] = Field(default=None, description="Optional Campaign ID.")
    execution_id: Optional[str] = Field(default=None, description="Optional Execution ID.")
    component: str = Field(..., description="Subsystem emitting event (e.g. 'campaign', 'execution').")
    event_type: str = Field(..., description="Event classification name (e.g. 'CampaignStarted').")
    severity: str = Field(default="INFO", description="Severity: DEBUG, INFO, WARNING, ERROR, CRITICAL.")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload body.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata attributes.")
    duration_ms: Optional[float] = Field(default=None, ge=0.0, description="Optional operation duration in ms.")
    provider: Optional[str] = Field(default=None, description="Target LLM provider name.")
    model: Optional[str] = Field(default=None, description="Target model name.")
    agent: Optional[str] = Field(default=None, description="Attacker agent name.")
    dataset: Optional[str] = Field(default=None, description="Dataset name.")
    taxonomy_node: Optional[str] = Field(default=None, description="AUAO taxonomy node tag.")


class SpanModel(BaseModel):
    """Distributed tracing span model."""
    span_id: UUID = Field(default_factory=uuid4)
    trace_id: UUID = Field(default_factory=uuid4)
    parent_span_id: Optional[UUID] = Field(default=None)
    name: str = Field(...)
    component: str = Field(...)
    start_time: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    end_time: Optional[str] = Field(default=None)
    duration_ms: Optional[float] = Field(default=None)
    status: str = Field(default="OK")
    attributes: Dict[str, Any] = Field(default_factory=dict)


class TraceModel(BaseModel):
    """Container model representing a complete execution trace graph."""
    trace_id: UUID = Field(default_factory=uuid4)
    root_span_name: str = Field(...)
    spans: List[SpanModel] = Field(default_factory=list)
    total_duration_ms: float = Field(default=0.0)
