import pytest
from observability.models import TelemetryEvent
from observability.event_bus import EventBus
from observability.events import create_telemetry_event, EventTypes
from observability.collector import TelemetryCollector
from observability.exporter import TelemetryExporter
from observability.exceptions import ObservabilityError, TelemetryEventError, EventBusError, TracingError, CollectorError


def test_event_bus_publish_and_subscribe():
    """Verify EventBus publishing, subscription, and callback execution."""
    bus = EventBus()
    received = []

    def on_event(ev: TelemetryEvent):
        received.append(ev)

    bus.subscribe("CampaignStarted", on_event)

    ev = create_telemetry_event(component="campaign", event_type="CampaignStarted")
    bus.publish(ev)

    assert len(received) == 1
    assert received[0].event_type == "CampaignStarted"

    # Test unsubscribe
    bus.unsubscribe("CampaignStarted", on_event)
    bus.publish(ev)
    assert len(received) == 1


def test_event_bus_wildcard_subscriber():
    """Verify wildcard '*' event bus subscriber."""
    bus = EventBus()
    received = []

    cb = lambda ev: received.append(ev)
    bus.subscribe("*", cb)

    bus.publish(create_telemetry_event(component="campaign", event_type="CampaignStarted"))
    bus.publish(create_telemetry_event(component="execution", event_type="ExecutionStarted"))

    assert len(received) == 2

    # Unsubscribe wildcard
    bus.unsubscribe("*", cb)
    bus.publish(create_telemetry_event(component="swarm", event_type="AttackPlanned"))
    assert len(received) == 2


def test_event_bus_replay_and_persist(tmp_path):
    """Verify event replay and disk persistence to events.jsonl."""
    bus = EventBus(base_dir=tmp_path)
    bus.publish(create_telemetry_event(component="campaign", event_type="CampaignStarted"))
    bus.publish(create_telemetry_event(component="swarm", event_type="AttackPlanned"))

    history = bus.replay()
    assert len(history) == 2

    path = bus.persist()
    assert path.exists()
    assert "events.jsonl" in path.name


def test_telemetry_collector_events():
    """Verify TelemetryCollector processes all event types and updates metrics."""
    collector = TelemetryCollector()

    events = [
        create_telemetry_event(component="provider", event_type=EventTypes.PROVIDER_CONNECTED, duration_ms=50.0),
        create_telemetry_event(component="execution", event_type=EventTypes.EXECUTION_FINISHED, duration_ms=100.0, payload={"attack_success": True}),
        create_telemetry_event(component="execution", event_type=EventTypes.EXECUTION_FAILED, duration_ms=120.0),
        create_telemetry_event(component="provider", event_type=EventTypes.PROVIDER_ERROR),
        create_telemetry_event(component="evaluation", event_type=EventTypes.REFUSAL_DETECTED, duration_ms=30.0),
        create_telemetry_event(component="evaluation", event_type=EventTypes.LEAKAGE_DETECTED),
        create_telemetry_event(component="evaluation", event_type=EventTypes.JAILBREAK_DETECTED)
    ]

    for ev in events:
        collector.event_bus.publish(ev)

    summary = collector.metrics_collector.summary()
    assert summary["counters"]["requests"] == 7.0
    assert summary["counters"]["attacks_total"] == 2.0
    assert summary["counters"]["attacks_successful"] == 1.0
    assert summary["counters"]["provider_failures"] == 1.0
    assert summary["counters"]["refusals_total"] == 1.0
    assert summary["counters"]["leakages_total"] == 1.0
    assert summary["counters"]["jailbreaks_total"] == 1.0


def test_telemetry_exporter(tmp_path):
    """Verify TelemetryExporter exports events.jsonl, metrics.json, and traces.jsonl."""
    collector = TelemetryCollector()
    collector.event_bus.publish(create_telemetry_event(component="campaign", event_type="CampaignStarted"))

    exporter = TelemetryExporter(base_dir=tmp_path)
    out_dir = exporter.export_all(collector.event_bus, collector.metrics_collector, collector.tracer)

    assert (out_dir / "events.jsonl").exists()
    assert (out_dir / "metrics.json").exists()
    assert (out_dir / "traces.jsonl").exists()


def test_observability_exceptions():
    """Verify custom exception representations."""
    err1 = ObservabilityError("base err")
    assert "[observability] base err" in str(err1)

    err2 = TelemetryEventError("invalid payload")
    assert "[telemetry]" in str(err2)

    err3 = EventBusError("bus failed")
    assert "[event_bus]" in str(err3)

    err4 = TracingError("span error")
    assert "[tracing]" in str(err4)

    err5 = CollectorError("export error")
    assert "[collector]" in str(err5)
