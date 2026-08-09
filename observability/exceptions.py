"""
Custom exception hierarchy for the AegisSwarm Telemetry, Monitoring & Observability Subsystem.
"""

class ObservabilityError(Exception):
    """Base exception for all observability platform errors."""
    def __init__(self, message: str, component: str = "observability"):
        self.message = message
        self.component = component
        super().__init__(f"[{component}] {message}")


class TelemetryEventError(ObservabilityError):
    """Raised when telemetry event creation or validation fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Event error: {details}", component="telemetry")


class EventBusError(ObservabilityError):
    """Raised when event publishing, subscription, or replay fails."""
    def __init__(self, details: str):
        super().__init__(message=f"EventBus error: {details}", component="event_bus")


class TracingError(ObservabilityError):
    """Raised when span context or trace collection fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Tracing error: {details}", component="tracing")


class CollectorError(ObservabilityError):
    """Raised when metrics collection or disk telemetry export fails."""
    def __init__(self, details: str):
        super().__init__(message=f"Collector error: {details}", component="collector")
