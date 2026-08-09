"""
Unit tests for ConfidenceEstimator in reasoning package.
"""

from reasoning.confidence import ConfidenceEstimator
from reasoning.models import StrategyCandidate, SimilarityMatch


def test_confidence_estimator():
    estimator = ConfidenceEstimator()
    cand = StrategyCandidate(
        attack_family="jailbreak",
        mutation_family="roleplay",
        provider="openai",
        estimated_confidence=0.88,
        reasoning_text="Confidence test candidate"
    )
    match = SimilarityMatch(
        record_id="rec-1",
        attack_id="atk-1",
        provider="openai",
        model="gpt-4o",
        taxonomy_node="AUAO-1",
        similarity_score=0.9
    )

    conf = estimator.estimate_confidence(candidate=cand, historical_matches=[match])
    assert 0.0 <= conf <= 1.0
    assert conf > 0.70
