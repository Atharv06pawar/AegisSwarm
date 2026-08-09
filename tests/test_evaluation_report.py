import json
import pytest
from uuid import uuid4
from evaluation.models import EvaluationResult, EvaluationSummary
from evaluation.report import EvaluationReportGenerator


def test_evaluation_report_markdown_and_json():
    """Verify Markdown and JSON report generation formatting."""
    summary = EvaluationSummary(
        total_evaluated=2,
        success_rate=0.5,
        refusal_rate=0.5,
        leakage_rate=0.5,
        jailbreak_rate=0.5,
        average_severity=4.5,
        average_confidence=0.95
    )

    res1 = EvaluationResult(
        execution_id=uuid4(),
        sample_id=uuid4(),
        provider="openai",
        model="gpt-4o",
        attack_success=True,
        detectors_used=["regex", "jailbreak"]
    )

    res2 = EvaluationResult(
        execution_id=uuid4(),
        sample_id=uuid4(),
        provider="ollama",
        model="llama3.2",
        refusal_detected=True,
        detectors_used=["refusal"]
    )

    results = [res1, res2]

    # Markdown Report
    md_report = EvaluationReportGenerator.generate_markdown_report(summary, results)
    assert "# AegisSwarm Evaluation Audit Report" in md_report
    assert "**Total Executions Evaluated**: 2" in md_report
    assert "`regex`: 1 evaluations" in md_report

    # JSON Report
    json_report = EvaluationReportGenerator.generate_json_report(summary, results)
    parsed = json.loads(json_report)
    assert parsed["summary"]["total_evaluated"] == 2
    assert parsed["detector_breakdown"]["regex"] == 1
    assert len(parsed["results"]) == 2
