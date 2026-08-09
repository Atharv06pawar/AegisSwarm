import pytest
from uuid import uuid4
from swarm.metrics import SwarmMetrics
from swarm.models import SwarmAgentResult


def test_swarm_metrics_recording_and_summary():
    """Verify SwarmMetrics accumulates results and computes SwarmSummary."""
    metrics = SwarmMetrics()
    assert metrics.summary().success_rate == 0.0

    res1 = SwarmAgentResult(
        agent_name="jailbreak",
        execution_id=uuid4(),
        evaluation_id=uuid4(),
        attack_success=True,
        confidence=0.9,
        severity=9.0,
        provider="openai",
        model="gpt-4o",
        execution_time_ms=150.0
    )

    res2 = SwarmAgentResult(
        agent_name="direct_injection",
        execution_id=uuid4(),
        evaluation_id=uuid4(),
        attack_success=False,
        confidence=0.9,
        severity=0.0,
        provider="openai",
        model="gpt-4o",
        execution_time_ms=100.0
    )

    metrics.record(res1, cost=0.001)
    metrics.record(res2, cost=0.001)

    summary = metrics.summary()
    assert summary.success_rate == 0.5
    assert summary.failure_rate == 0.5
    assert summary.provider_distribution["openai"] == 2
    assert summary.attack_distribution["jailbreak"] == 1
    assert summary.cost == 0.002
    assert summary.latency == 250.0


def test_swarm_metrics_reset():
    """Verify metrics reset clears accumulated counts."""
    metrics = SwarmMetrics()
    res = SwarmAgentResult(
        agent_name="jailbreak",
        execution_id=uuid4(),
        evaluation_id=uuid4(),
        attack_success=True,
        confidence=0.9,
        severity=9.0,
        provider="openai",
        model="gpt-4o",
        execution_time_ms=100.0
    )
    metrics.record(res)
    assert len(metrics.agent_results) == 1

    metrics.reset()
    assert len(metrics.agent_results) == 0
