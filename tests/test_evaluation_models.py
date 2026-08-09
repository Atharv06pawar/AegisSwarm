import pytest
from uuid import uuid4
from execution.models import ExecutionResult
from evaluation.models import EvaluationRequest, EvaluationResult, EvaluationSummary


def create_sample_execution_result() -> ExecutionResult:
    """Helper creating a sample ExecutionResult model for unit testing."""
    return ExecutionResult(
        session_id=uuid4(),
        attack_id=uuid4(),
        provider="openai",
        model="gpt-4o",
        completion="Sample completion text",
        total_tokens=100
    )


def test_evaluation_request_model():
    """Verify EvaluationRequest model structure and defaults."""
    exec_res = create_sample_execution_result()
    req = EvaluationRequest(execution_result=exec_res, detector_config={"threshold": 0.8})
    assert req.execution_result.provider == "openai"
    assert req.detector_config["threshold"] == 0.8


def test_evaluation_result_model():
    """Verify EvaluationResult model structure and validation."""
    exec_res = create_sample_execution_result()
    res = EvaluationResult(
        execution_id=exec_res.execution_id,
        sample_id=exec_res.attack_id,
        provider=exec_res.provider,
        model=exec_res.model,
        attack_success=True,
        refusal_detected=False,
        prompt_leak_detected=True,
        jailbreak_detected=True,
        severity_score=9.5,
        confidence=0.98,
        evaluation_reason="Leakage and jailbreak verified.",
        detectors_used=["regex", "jailbreak"]
    )
    assert res.attack_success is True
    assert res.severity_score == 9.5
    assert res.confidence == 0.98
    assert "regex" in res.detectors_used


def test_evaluation_summary_model():
    """Verify EvaluationSummary default fields."""
    summary = EvaluationSummary(
        total_evaluated=10,
        success_rate=0.5,
        refusal_rate=0.2,
        leakage_rate=0.1,
        jailbreak_rate=0.4,
        average_severity=6.5,
        average_confidence=0.9
    )
    assert summary.total_evaluated == 10
    assert summary.success_rate == 0.5
    assert summary.average_severity == 6.5
