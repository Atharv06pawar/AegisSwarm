"""
AegisSwarm Telemetry, Monitoring & Observability Platform package.
"""

from observability.models import TelemetryEvent, SpanModel, TraceModel
from observability.events import EventTypes, create_telemetry_event
from observability.event_bus import EventBus
from observability.logger import StructuredLogger
from observability.metrics import TelemetryMetricsCollector
from observability.tracing import Span, Tracer
from observability.collector import TelemetryCollector
from observability.exporter import TelemetryExporter
from observability.dashboard import TelemetryDashboard
from observability.exceptions import (
    ObservabilityError,
    TelemetryEventError,
    EventBusError,
    TracingError,
    CollectorError
)

__all__ = [
    "TelemetryEvent",
    "SpanModel",
    "TraceModel",
    "EventTypes",
    "create_telemetry_event",
    "EventBus",
    "StructuredLogger",
    "TelemetryMetricsCollector",
    "Span",
    "Tracer",
    "TelemetryCollector",
    "TelemetryExporter",
    "TelemetryDashboard",
    "ObservabilityError",
    "TelemetryEventError",
    "EventBusError",
    "TracingError",
    "CollectorError"
]
