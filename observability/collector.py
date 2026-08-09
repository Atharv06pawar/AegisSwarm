"""
TelemetryCollector module for ingesting EventBus events and routing to metrics & tracing engines.
"""

import logging
from typing import Optional
from observability.models import TelemetryEvent
from observability.events import EventTypes
from observability.event_bus import EventBus
from observability.metrics import TelemetryMetricsCollector
from observability.tracing import Tracer

logger = logging.getLogger(__name__)


class TelemetryCollector:
    """
    Central collector subscribing to EventBus notifications and processing metrics accumulators.
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

        # Subscribe to wildcard event bus stream
        self.event_bus.subscribe("*", self._handle_event)

    def _handle_event(self, event: TelemetryEvent) -> None:
        """Processes an incoming event from the EventBus."""
        self.metrics_collector.increment("requests")

        if event.duration_ms:
            if event.component == "provider":
                self.metrics_collector.observe("provider_latency", event.duration_ms)
            elif event.component in ["execution", "swarm"]:
                self.metrics_collector.observe("attack_latency", event.duration_ms)
            elif event.component == "evaluation":
                self.metrics_collector.observe("evaluation_latency", event.duration_ms)

        if event.event_type == EventTypes.EXECUTION_FINISHED:
            self.metrics_collector.increment("attacks_total")
            if event.payload.get("attack_success"):
                self.metrics_collector.increment("attacks_successful")

        elif event.event_type == EventTypes.EXECUTION_FAILED:
            self.metrics_collector.increment("attacks_total")

        elif event.event_type == EventTypes.PROVIDER_ERROR:
            self.metrics_collector.increment("provider_failures")

        elif event.event_type == EventTypes.REFUSAL_DETECTED:
            self.metrics_collector.increment("refusals_total")

        elif event.event_type == EventTypes.LEAKAGE_DETECTED:
            self.metrics_collector.increment("leakages_total")

        elif event.event_type == EventTypes.JAILBREAK_DETECTED:
            self.metrics_collector.increment("jailbreaks_total")
