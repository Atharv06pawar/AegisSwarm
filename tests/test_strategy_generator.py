"""
Unit tests for StrategyGenerator in reasoning package.
"""

from reasoning.generator import StrategyGenerator
from reasoning.models import ReasoningRequest


def test_strategy_generator_min_candidates():
    generator = StrategyGenerator()
    req = ReasoningRequest(objective="Direct injection security audit", target_provider="openai")
    candidates = generator.generate_candidates(req)

    assert len(candidates) >= 5
    for c in candidates:
        assert c.attack_family is not None
        assert c.mutation_family is not None
        assert c.estimated_success >= 0.0
        assert c.rank_score is not None
