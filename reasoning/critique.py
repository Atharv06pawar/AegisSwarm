"""
CritiqueEngine evaluating novelty, expected success, cost efficiency, risk, and complexity.
"""

from typing import List
from reasoning.models import StrategyCandidate, CritiqueResult
from reasoning.exceptions import CritiqueError


class CritiqueEngine:
    """
    Self-critique evaluator assessing strategy candidates along key operational axes.
    """

    def critique_candidate(self, candidate: StrategyCandidate) -> CritiqueResult:
        """
        Evaluates a single strategy candidate and returns a structured CritiqueResult.
        """
        novelty = 0.85 if candidate.mutation_family in ["tool_injection", "cot_wrapper"] else 0.70
        success_score = candidate.estimated_success
        cost_eff = max(0.1, 1.0 - (candidate.estimated_cost * 100.0))
        risk_score = 0.3 if candidate.estimated_severity in ["Low", "Medium"] else 0.7
        complexity = 0.4 if candidate.attack_family == "direct_injection" else 0.8

        overall = (0.3 * success_score) + (0.25 * novelty) + (0.25 * cost_eff) + (0.2 * (1.0 - risk_score))

        return CritiqueResult(
            candidate_id=candidate.candidate_id,
            novelty_score=round(novelty, 4),
            expected_success_score=round(success_score, 4),
            cost_efficiency_score=round(cost_eff, 4),
            risk_score=round(risk_score, 4),
            complexity_score=round(complexity, 4),
            overall_critique_score=round(overall, 4),
            critique_notes=f"Evaluated {candidate.attack_family}+{candidate.mutation_family}: High expected evasion capability."
        )

    def critique_all(self, candidates: List[StrategyCandidate]) -> List[CritiqueResult]:
        """Evaluates a list of candidates."""
        return [self.critique_candidate(c) for c in candidates]
