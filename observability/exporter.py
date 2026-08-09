"""
TelemetryExporter module for writing events.jsonl, metrics.json, and traces.jsonl to outputs/telemetry/.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from observability.event_bus import EventBus
from observability.metrics import TelemetryMetricsCollector
from observability.tracing import Tracer
from observability.exceptions import CollectorError

logger = logging.getLogger(__name__)


class TelemetryExporter:
    """
    Exporter writing events, metrics, and trace models to disk.
    """

    def __init__(self, base_dir: Path = Path("outputs/telemetry")):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def export_all(
        self,
        event_bus: EventBus,
        metrics_collector: TelemetryMetricsCollector,
        tracer: Tracer
    ) -> Path:
        """
        Exports events.jsonl, metrics.json, and traces.jsonl to disk under outputs/telemetry/.
        """
        try:
            # Export events
            event_bus.persist(self.base_dir)

            # Export metrics.json
            metrics_path = self.base_dir / "metrics.json"
            tmp_metrics = self.base_dir / "metrics.json.tmp"
            metrics_data = metrics_collector.summary()
            
            with open(tmp_metrics, "w", encoding="utf-8") as f:
                json.dump(metrics_data, f, indent=2)
            tmp_metrics.replace(metrics_path)

            # Export traces.jsonl
            traces_path = self.base_dir / "traces.jsonl"
            tmp_traces = self.base_dir / "traces.jsonl.tmp"
            traces = tracer.list_traces()

            with open(tmp_traces, "w", encoding="utf-8") as f:
                for tr in traces:
                    f.write(tr.model_dump_json() + "\n")
            tmp_traces.replace(traces_path)

            logger.info(f"Successfully exported telemetry artifacts to {self.base_dir}")
            return self.base_dir

        except Exception as err:
            raise CollectorError(f"Failed to export telemetry: {err}") from err
