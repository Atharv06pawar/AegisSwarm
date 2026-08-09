"""
Unit tests for CritiqueEngine in reasoning package.
"""

from reasoning.critique import CritiqueEngine
from reasoning.models import StrategyCandidate


def test_critique_engine_evaluation():
    engine = CritiqueEngine()
    cand = StrategyCandidate(
        attack_family="indirect_injection",
        mutation_family="tool_injection",
        provider="anthropic",
        estimated_success=0.9,
        estimated_cost=0.001,
        reasoning_text="Critique test candidate"
    )

    critique = engine.critique_candidate(cand)
    assert critique.candidate_id == cand.candidate_id
    assert 0.0 <= critique.overall_critique_score <= 1.0
    assert critique.novelty_score > 0.5
