import pytest
from observability.event_bus import EventBus
from observability.metrics import TelemetryMetricsCollector
from observability.tracing import Tracer
from observability.dashboard import TelemetryDashboard
from observability.events import create_telemetry_event


def test_telemetry_dashboard_data():
    """Verify TelemetryDashboard aggregates dashboard metrics and recent events."""
    bus = EventBus()
    metrics = TelemetryMetricsCollector()
    tracer = Tracer()

    bus.publish(create_telemetry_event(component="campaign", event_type="CampaignStarted"))
    metrics.increment("requests", 10.0)

    dashboard = TelemetryDashboard(event_bus=bus, metrics_collector=metrics, tracer=tracer)
    data = dashboard.get_dashboard_data()

    assert data["system_status"] == "healthy"
    assert "requests_per_sec" in data
    assert "provider_status" in data
    assert len(data["recent_events"]) >= 1
