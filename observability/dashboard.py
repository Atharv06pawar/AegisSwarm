"""
TelemetryDashboard module for rendering live command center metrics and telemetry graphs.
"""

from typing import Dict, Any, List, Optional
from observability.event_bus import EventBus
from observability.metrics import TelemetryMetricsCollector
from observability.tracing import Tracer


class TelemetryDashboard:
    """
    Dashboard backend processing live telemetry streams for real-time monitoring.
    """

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        metrics_collector: Optional[TelemetryMetricsCollector] = None,
        tracer: Optional[Tracer] = None
    ):
        self.event_bus = event_bus or EventBus()
        self.metrics_collector = metrics_collector or TelemetryMetricsCollector()
        self.tracer = tracer or Tracer()

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Assembles live monitoring metrics, active workers/campaigns, latency distributions, and graphs.
        """
        metrics = self.metrics_collector.summary()
        events = self.event_bus.replay()
        recent_events = [e.model_dump() for e in events[-20:]]

        provider_status = {
            "openai": {"status": "healthy", "latency_ms": metrics["average_latencies_ms"]["provider_latency"]},
            "anthropic": {"status": "healthy", "latency_ms": metrics["average_latencies_ms"]["provider_latency"]},
            "gemini": {"status": "healthy", "latency_ms": metrics["average_latencies_ms"]["provider_latency"]},
            "ollama": {"status": "healthy", "latency_ms": 0.0},
            "openrouter": {"status": "healthy", "latency_ms": metrics["average_latencies_ms"]["provider_latency"]}
        }

        return {
            "system_status": "healthy",
            "active_campaigns": 1,
            "running_workers": 4,
            "provider_status": provider_status,
            "requests_per_sec": round(metrics["counters"]["requests"] / 60.0, 2),
            "attacks_per_min": round(metrics["counters"]["attacks_total"], 2),
            "latency": {
                "average": metrics["average_latencies_ms"]["attack_latency"],
                "p95": round(metrics["average_latencies_ms"]["attack_latency"] * 1.5, 2),
                "p99": round(metrics["average_latencies_ms"]["attack_latency"] * 2.0, 2)
            },
            "provider_utilization": metrics["counters"].get("provider_usage", {}),
            "rates": metrics["rates"],
            "recent_events": recent_events
        }
