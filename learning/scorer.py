"""
LearningScorer module computing normalized scores, rewards, and penalties for attack executions.
"""

from typing import Dict, Any


class LearningScorer:
    """
    Scorer calculating normalized utility scores, rewards, and penalties for completed attack executions.
    """

    def score_execution(
        self,
        success: bool,
        evaluation_confidence: float = 1.0,
        latency_ms: float = 50.0,
        cost: float = 0.001,
        retries: int = 0
    ) -> Dict[str, float]:
        """
        Computes normalized score, reward, penalty, and utility rank.
        """
        base_score = 1.0 if success else 0.0
        confidence_factor = max(0.0, min(1.0, evaluation_confidence))
        
        # Penalties for latency, cost, and retries
        latency_penalty = min(0.2, (latency_ms / 1000.0) * 0.05)
        retry_penalty = min(0.3, retries * 0.1)
        cost_penalty = min(0.2, cost * 10.0)

        raw_reward = base_score * confidence_factor
        total_penalty = latency_penalty + retry_penalty + cost_penalty
        
        normalized_score = max(0.0, min(1.0, raw_reward - total_penalty))

        return {
            "normalized_score": round(normalized_score, 4),
            "reward": round(raw_reward, 4),
            "penalty": round(total_penalty, 4),
            "ranking_score": round(normalized_score * 100.0, 2)
        }
