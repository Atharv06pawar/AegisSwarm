"""
EvaluationMetrics module for computing aggregated statistics over EvaluationResult instances.
"""

from typing import List
from evaluation.models import EvaluationResult, EvaluationSummary


class EvaluationMetrics:
    """
    Metrics accumulator that processes EvaluationResult objects and computes
    statistical rates, averages, latencies, and costs.
    """

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """Resets metrics accumulator counters."""
        self.results: List[EvaluationResult] = []

    def record(self, result: EvaluationResult) -> None:
        """
        Records an EvaluationResult into the accumulator.
        """
        self.results.append(result)

    def summary(self) -> EvaluationSummary:
        """
        Computes an EvaluationSummary model from recorded results.
        """
        total = len(self.results)
        if total == 0:
            return EvaluationSummary()

        successes = sum(1 for r in self.results if r.attack_success)
        refusals = sum(1 for r in self.results if r.refusal_detected)
        leakages = sum(1 for r in self.results if r.prompt_leak_detected)
        jailbreaks = sum(1 for r in self.results if r.jailbreak_detected)

        avg_severity = sum(r.severity_score for r in self.results) / total
        avg_confidence = sum(r.confidence for r in self.results) / total
        total_latency = sum(r.evaluation_latency_ms for r in self.results)
        total_cost = sum(r.estimated_cost for r in self.results)

        return EvaluationSummary(
            total_evaluated=total,
            success_rate=round(successes / total, 4),
            refusal_rate=round(refusals / total, 4),
            leakage_rate=round(leakages / total, 4),
            jailbreak_rate=round(jailbreaks / total, 4),
            average_severity=round(avg_severity, 2),
            average_confidence=round(avg_confidence, 2),
            total_latency_ms=round(total_latency, 2),
            total_cost=round(total_cost, 6)
        )
