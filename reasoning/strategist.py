"""
AutonomousStrategist high-level facade interface wrapping AutonomousPlanner.
"""

from typing import Optional, List
from reasoning.models import ReasoningRequest, ReasoningResponse, StrategyCandidate, CritiqueResult, ReflectionResult
from reasoning.planner import AutonomousPlanner


class AutonomousStrategist:
    """
    High-level strategic reasoning facade exposing single-point entry methods.
    """

    def __init__(self, planner: Optional[AutonomousPlanner] = None):
        self.planner = planner or AutonomousPlanner()

    def plan(self, request: ReasoningRequest) -> ReasoningResponse:
        """Executes full autonomous reasoning pass."""
        return self.planner.plan_attack(request)

    def reflect(self, campaign_id: Optional[str] = None, attack_id: Optional[str] = None) -> ReflectionResult:
        """Executes post-execution reflection."""
        return self.planner.reflection_engine.reflect(campaign_id=campaign_id, attack_id=attack_id, outcome_success=True)

    def critique(self, candidate: StrategyCandidate) -> CritiqueResult:
        """Executes self-critique evaluation on a candidate strategy."""
        return self.planner.critique_engine.critique_candidate(candidate)

    def rank(self, candidates: List[StrategyCandidate]) -> List[StrategyCandidate]:
        """Ranks strategy candidates in order of multi-attribute utility."""
        return self.planner.ranking_engine.rank_candidates(candidates)
