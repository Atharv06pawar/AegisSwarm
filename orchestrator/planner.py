"""
OrchestratorPlanner integrating reasoning planning and campaign scheduling.
"""

from typing import Optional, Dict, Any
from orchestrator.models import MissionRequest
from reasoning.planner import AutonomousPlanner
from reasoning.models import ReasoningRequest, ReasoningResponse


class OrchestratorPlanner:
    """
    Planner synthesizing reasoning strategies into orchestrator mission execution plans.
    """

    def __init__(self, reasoning_planner: Optional[AutonomousPlanner] = None):
        self.reasoning_planner = reasoning_planner or AutonomousPlanner()

    def plan_mission(self, request: MissionRequest) -> Dict[str, Any]:
        """
        Invokes Reasoning Engine to construct strategic candidate plan tailored for orchestrator mission.
        """
        r_req = ReasoningRequest(
            objective=request.objective,
            target_provider=request.target_provider,
            target_model=request.target_model,
            budget_usd=request.budget_usd,
            max_candidates=5
        )
        reasoning_res: ReasoningResponse = self.reasoning_planner.plan_attack(r_req)

        return {
            "mission_id": str(request.mission_id),
            "chosen_strategy": reasoning_res.chosen_strategy.model_dump(mode="json"),
            "mutation_plan": reasoning_res.mutation_plan.model_dump(mode="json"),
            "provider_recommendation": reasoning_res.provider_recommendation.model_dump(mode="json"),
            "confidence": reasoning_res.overall_confidence
        }
