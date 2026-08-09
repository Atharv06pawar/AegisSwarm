"""
Unit tests for RankingEngine in reasoning package.
"""

from reasoning.ranking import RankingEngine
from reasoning.generator import StrategyGenerator
from reasoning.critique import CritiqueEngine
from reasoning.models import ReasoningRequest


def test_ranking_engine():
    generator = StrategyGenerator()
    critique_engine = CritiqueEngine()
    ranking_engine = RankingEngine()

    req = ReasoningRequest(objective="Ranking test pass", target_provider="openai")
    candidates = generator.generate_candidates(req)
    critiques = critique_engine.critique_all(candidates)

    ranked = ranking_engine.rank_candidates(candidates=candidates, critiques=critiques)

    assert len(ranked) == len(candidates)
    for i in range(len(ranked) - 1):
        assert (ranked[i].rank_score or 0.0) >= (ranked[i + 1].rank_score or 0.0)
