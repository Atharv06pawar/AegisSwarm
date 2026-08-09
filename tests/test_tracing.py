import pytest
from uuid import uuid4
from observability.tracing import Span, Tracer


def test_span_finish():
    """Verify Span finish calculates duration_ms and sets status."""
    span = Span(name="TestSpan", component="execution")
    assert span.duration_ms is None

    span.finish(status="OK", attributes={"key": "value"})
    assert span.duration_ms is not None
    assert span.status == "OK"
    assert span.attributes["key"] == "value"


def test_tracer_span_hierarchy():
    """Verify Tracer span creation, parent-child hierarchy, and trace retrieval."""
    tracer = Tracer()
    root_span = tracer.start_span(name="Campaign", component="campaign")
    child_span = tracer.start_span(name="Scheduler", component="scheduler", parent_span=root_span)

    tracer.finish_span(child_span, status="OK")
    tracer.finish_span(root_span, status="OK")

    trace = tracer.get_trace(root_span.trace_id)
    assert trace is not None
    assert trace.root_span_name == "Campaign"
    assert len(trace.spans) == 2
    assert trace.spans[1].parent_span_id == root_span.span_id
