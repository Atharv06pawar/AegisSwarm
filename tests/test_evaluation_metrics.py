import pytest
from uuid import uuid4
from evaluation.metrics import EvaluationMetrics
from evaluation.models import EvaluationResult


def test_evaluation_metrics_recording():
    """Verify EvaluationMetrics accumulates stats and calculates rates."""
    metrics = EvaluationMetrics()
    assert metrics.summary().total_evaluated == 0

    res1 = EvaluationResult(
        execution_id=uuid4(),
        sample_id=uuid4(),
        provider="openai",
        model="gpt-4o",
        attack_success=True,
        refusal_detected=False,
        prompt_leak_detected=True,
        jailbreak_detected=True,
        severity_score=9.0,
        confidence=0.95
    )

    res2 = EvaluationResult(
        execution_id=uuid4(),
        sample_id=uuid4(),
        provider="ollama",
        model="llama3.2",
        attack_success=False,
        refusal_detected=True,
        prompt_leak_detected=False,
        jailbreak_detected=False,
        severity_score=0.0,
        confidence=0.95
    )

    metrics.record(res1)
    metrics.record(res2)

    summary = metrics.summary()
    assert summary.total_evaluated == 2
    assert summary.success_rate == 0.5
    assert summary.refusal_rate == 0.5
    assert summary.leakage_rate == 0.5
    assert summary.jailbreak_rate == 0.5
    assert summary.average_severity == 4.5
    assert summary.average_confidence == 0.95


def test_evaluation_metrics_reset():
    """Verify resetting metrics clears all accumulated results."""
    metrics = EvaluationMetrics()
    res = EvaluationResult(
        execution_id=uuid4(),
        sample_id=uuid4(),
        provider="openai",
        model="gpt-4o",
        attack_success=True
    )
    metrics.record(res)
    assert metrics.summary().total_evaluated == 1

    metrics.reset()
    assert metrics.summary().total_evaluated == 0
