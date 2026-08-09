"""
Distributed Tracing module providing Span, Trace, and Tracer context management across all execution stages.
"""

import time
import threading
import logging
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import List, Dict, Optional, Any

from observability.models import SpanModel, TraceModel

logger = logging.getLogger(__name__)


class Span:
    """
    Tracing span measuring execution duration, status, parent-child relationships, and attributes.
    """

    def __init__(
        self,
        name: str,
        component: str,
        trace_id: Optional[UUID] = None,
        parent_span_id: Optional[UUID] = None
    ):
        self.span_id = uuid4()
        self.trace_id = trace_id or uuid4()
        self.parent_span_id = parent_span_id
        self.name = name
        self.component = component
        self.start_wall = datetime.now(timezone.utc).isoformat()
        self.start_perf = time.perf_counter()
        self.end_wall: Optional[str] = None
        self.duration_ms: Optional[float] = None
        self.status: str = "OK"
        self.attributes: Dict[str, Any] = {}

    def finish(self, status: str = "OK", attributes: Optional[Dict[str, Any]] = None) -> "Span":
        """
        Finishes span duration measurement and updates status.
        """
        self.end_wall = datetime.now(timezone.utc).isoformat()
        self.duration_ms = round((time.perf_counter() - self.start_perf) * 1000.0, 2)
        self.status = status
        if attributes:
            self.attributes.update(attributes)
        return self

    def to_model(self) -> SpanModel:
        """Converts to Pydantic SpanModel."""
        return SpanModel(
            span_id=self.span_id,
            trace_id=self.trace_id,
            parent_span_id=self.parent_span_id,
            name=self.name,
            component=self.component,
            start_time=self.start_wall,
            end_time=self.end_wall,
            duration_ms=self.duration_ms,
            status=self.status,
            attributes=self.attributes
        )


class Tracer:
    """
    Tracer engine managing active traces and hierarchy across Campaign, Scheduler,
    Dispatcher, Worker, Execution Engine, Provider, Evaluation, Swarm, and Persistence.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._traces: Dict[UUID, List[Span]] = {}

    def start_span(
        self,
        name: str,
        component: str,
        parent_span: Optional[Span] = None,
        trace_id: Optional[UUID] = None
    ) -> Span:
        """
        Starts a new span and registers it under trace hierarchy.
        """
        with self._lock:
            tid = parent_span.trace_id if parent_span else (trace_id or uuid4())
            pid = parent_span.span_id if parent_span else None

            span = Span(name=name, component=component, trace_id=tid, parent_span_id=pid)
            
            if tid not in self._traces:
                self._traces[tid] = []
            self._traces[tid].append(span)

            return span

    def finish_span(self, span: Span, status: str = "OK", attributes: Optional[Dict[str, Any]] = None) -> None:
        """
        Finishes an active span.
        """
        span.finish(status=status, attributes=attributes)

    def get_trace(self, trace_id: UUID) -> Optional[TraceModel]:
        """
        Retrieves a completed TraceModel by trace_id.
        """
        with self._lock:
            spans = self._traces.get(trace_id, [])
            if not spans:
                return None

            span_models = [s.to_model() for s in spans]
            total_duration = sum(s.duration_ms or 0.0 for s in spans)
            root_name = spans[0].name

            return TraceModel(
                trace_id=trace_id,
                root_span_name=root_name,
                spans=span_models,
                total_duration_ms=round(total_duration, 2)
            )

    def list_traces(self) -> List[TraceModel]:
        """
        Lists all recorded traces.
        """
        with self._lock:
            models: List[TraceModel] = []
            for tid in self._traces:
                tr = self.get_trace(tid)
                if tr:
                    models.append(tr)
            return models
