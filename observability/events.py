"""
Standard Event Classification Definitions for AegisSwarm Telemetry.
"""

from typing import Dict, Any, Optional
from observability.models import TelemetryEvent


class EventTypes:
    # Campaign Events
    CAMPAIGN_CREATED = "CampaignCreated"
    CAMPAIGN_STARTED = "CampaignStarted"
    CAMPAIGN_PAUSED = "CampaignPaused"
    CAMPAIGN_FINISHED = "CampaignFinished"

    # Swarm Events
    ATTACK_PLANNED = "AttackPlanned"
    MUTATION_CREATED = "MutationCreated"
    RETRY_SCHEDULED = "RetryScheduled"
    LEARNING_UPDATED = "LearningUpdated"

    # Execution Events
    EXECUTION_STARTED = "ExecutionStarted"
    EXECUTION_FINISHED = "ExecutionFinished"
    EXECUTION_FAILED = "ExecutionFailed"

    # Provider Events
    PROVIDER_CONNECTED = "ProviderConnected"
    PROVIDER_TIMEOUT = "ProviderTimeout"
    PROVIDER_ERROR = "ProviderError"

    # Evaluation Events
    LEAKAGE_DETECTED = "LeakageDetected"
    REFUSAL_DETECTED = "RefusalDetected"
    JAILBREAK_DETECTED = "JailbreakDetected"
    EVALUATION_FINISHED = "EvaluationFinished"

    # Corpus & Ingestion Events
    DATASET_LOADED = "DatasetLoaded"
    INGESTION_FINISHED = "IngestionFinished"
    REPORT_GENERATED = "ReportGenerated"


def create_telemetry_event(
    component: str,
    event_type: str,
    severity: str = "INFO",
    payload: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    execution_id: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    agent: Optional[str] = None,
    duration_ms: Optional[float] = None
) -> TelemetryEvent:
    """
    Factory helper function creating a validated TelemetryEvent model.
    """
    return TelemetryEvent(
        component=component,
        event_type=event_type,
        severity=severity,
        payload=payload or {},
        session_id=session_id,
        campaign_id=campaign_id,
        execution_id=execution_id,
        provider=provider,
        model=model,
        agent=agent,
        duration_ms=duration_ms
    )
