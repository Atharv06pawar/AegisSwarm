import pytest
from learning.scorer import LearningScorer


def test_learning_scorer_calculations():
    """Verify LearningScorer score_execution output components."""
    scorer = LearningScorer()
    score_data = scorer.score_execution(
        success=True,
        evaluation_confidence=0.9,
        latency_ms=100.0,
        cost=0.002,
        retries=1
    )

    assert "normalized_score" in score_data
    assert "reward" in score_data
    assert "penalty" in score_data
    assert score_data["reward"] > 0.0
    assert score_data["normalized_score"] >= 0.0
