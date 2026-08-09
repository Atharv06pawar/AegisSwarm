import pytest
from observability.metrics import TelemetryMetricsCollector


def test_telemetry_metrics_collector():
    """Verify counter increments, latency observations, and summary rate calculations."""
    collector = TelemetryMetricsCollector()

    collector.increment("requests", 5.0)
    collector.increment("attacks_total", 10.0)
    collector.increment("attacks_successful", 8.0)
    collector.increment("refusals_total", 1.0)
    collector.increment("leakages_total", 1.0)

    collector.observe("provider_latency", 45.0)
    collector.observe("provider_latency", 55.0)
    collector.observe("attack_latency", 100.0)

    summary = collector.summary()

    assert summary["counters"]["requests"] == 5.0
    assert summary["rates"]["attack_success_rate"] == 0.8
    assert summary["rates"]["refusal_rate"] == 0.1
    assert summary["rates"]["leakage_rate"] == 0.1
    assert summary["average_latencies_ms"]["provider_latency"] == 50.0
    assert summary["average_latencies_ms"]["attack_latency"] == 100.0


def test_telemetry_metrics_collector_reset():
    """Verify metrics reset clears counters and observations."""
    collector = TelemetryMetricsCollector()
    collector.increment("requests", 10.0)
    collector.reset()

    summary = collector.summary()
    assert summary["counters"]["requests"] == 0.0
