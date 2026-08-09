"""
RankingEngine ordering candidates based on success prediction, confidence, cost, latency, and critique scores.
"""

from typing import List, Optional, Dict
from uuid import UUID
from reasoning.models import StrategyCandidate, CritiqueResult
from reasoning.exceptions import RankingError


class RankingEngine:
    """
    Ranking engine calculating composite multi-attribute utility scores for candidate strategy ordering.
    """

    def rank_candidates(
        self,
        candidates: List[StrategyCandidate],
        critiques: Optional[List[CritiqueResult]] = None
    ) -> List[StrategyCandidate]:
        """
        Calculates normalized rank scores for all candidates and returns them in descending priority order.
        """
        critique_map: Dict[UUID, CritiqueResult] = {}
        if critiques:
            critique_map = {c.candidate_id: c for c in critiques}

        for cand in candidates:
            c_result = critique_map.get(cand.candidate_id)
            critique_bonus = c_result.overall_critique_score if c_result else 0.8

            success_weight = cand.estimated_success * 0.35
            conf_weight = cand.estimated_confidence * 0.25
            critique_weight = critique_bonus * 0.25
            cost_weight = max(0.0, 1.0 - (cand.estimated_cost * 50.0)) * 0.15

            cand.rank_score = round(success_weight + conf_weight + critique_weight + cost_weight, 4)

        sorted_candidates = sorted(candidates, key=lambda x: x.rank_score or 0.0, reverse=True)
        return sorted_candidates
