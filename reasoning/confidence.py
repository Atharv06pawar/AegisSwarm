"""
ConfidenceEstimator calculating normalized multi-factor confidence estimates in [0.0, 1.0].
"""

from typing import List, Optional
from reasoning.models import StrategyCandidate, SimilarityMatch


class ConfidenceEstimator:
    """
    Confidence estimator combining provider reliability, mutation confidence, and historical similarity matches.
    """

    def estimate_confidence(
        self,
        candidate: StrategyCandidate,
        historical_matches: Optional[List[SimilarityMatch]] = None
    ) -> float:
        """
        Calculates normalized confidence score based on candidate parameters and historical match scores.
        """
        prov_conf = 0.90 if candidate.provider in ["openai", "anthropic"] else 0.80
        mut_conf = candidate.estimated_confidence

        hist_conf = 0.75
        if historical_matches and len(historical_matches) > 0:
            hist_conf = sum(m.similarity_score for m in historical_matches) / len(historical_matches)

        overall = (0.4 * mut_conf) + (0.35 * prov_conf) + (0.25 * hist_conf)
        return round(min(1.0, max(0.0, overall)), 4)
