import pytest
from uuid import uuid4
from execution.metrics import ExecutionMetrics
from execution.models import ExecutionResult


def test_metrics_record_and_summary():
    """Verify metrics accumulation and summary statistics calculation."""
    metrics = ExecutionMetrics()
    assert metrics.total_executions == 0

    res1 = ExecutionResult(
        session_id=uuid4(),
        attack_id=uuid4(),
        provider="openai",
        model="gpt-4o",
        completion="Result 1",
        latency_ms=100.0,
        duration_ms=120.0,
        prompt_tokens=50,
        completion_tokens=50,
        total_tokens=100,
        estimated_cost=0.001,
        status="completed"
    )

    res2 = ExecutionResult(
        session_id=uuid4(),
        attack_id=uuid4(),
        provider="ollama",
        model="llama3.2",
        completion="Result 2",
        latency_ms=200.0,
        duration_ms=220.0,
        prompt_tokens=40,
        completion_tokens=60,
        total_tokens=100,
        estimated_cost=0.0,
        status="completed"
    )

    metrics.record(res1)
    metrics.record(res2)

    summary = metrics.summary()
    assert summary["total_executions"] == 2
    assert summary["total_successes"] == 2
    assert summary["avg_latency_ms"] == 150.0
    assert summary["avg_duration_ms"] == 170.0
    assert summary["total_tokens"] == 200
    assert summary["total_cost_usd"] == 0.001


def test_metrics_reset():
    """Verify metrics reset clears all accumulated statistics."""
    metrics = ExecutionMetrics()
    res = ExecutionResult(
        session_id=uuid4(),
        attack_id=uuid4(),
        provider="openai",
        model="gpt-4o",
        completion="Result",
        total_tokens=50
    )
    metrics.record(res)
    assert metrics.total_executions == 1

    metrics.reset()
    assert metrics.total_executions == 0
    assert metrics.total_tokens == 0
