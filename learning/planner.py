"""
AdaptivePlanner module generating feedback-driven AttackPlan models based on LearningMemory.
"""

from typing import Optional, Dict, Any, List

from learning.models import AttackPlan
from learning.memory import LearningMemory
from learning.optimizer import StrategyOptimizer
from learning.exceptions import PlannerError


class AdaptivePlanner:
    """
    Adaptive attack strategy planner producing ranked AttackPlan models using memory statistics and optimization.
    """

    def __init__(
        self,
        memory: Optional[LearningMemory] = None,
        optimizer: Optional[StrategyOptimizer] = None
    ):
        self.memory = memory or LearningMemory()
        self.optimizer = optimizer or StrategyOptimizer()

    def create_plan(
        self,
        target_provider: str = "openai",
        campaign_id: Optional[str] = None,
        objective_name: Optional[str] = None,
        budget_usd: float = 10.0
    ) -> AttackPlan:
        """
        Generates an adaptive AttackPlan model based on historical outcomes and provider capabilities.
        """
        opt_params = self.optimizer.optimize(self.memory)
        mutation_order = opt_params["mutation_ordering"]
        agent_order = opt_params["agent_ordering"]

        chosen_family = mutation_order[0] if mutation_order else "persona"
        chosen_agents = agent_order[:2] if agent_order else ["jailbreak"]

        return AttackPlan(
            campaign_id=campaign_id,
            target_provider=target_provider,
            chosen_family=chosen_family,
            chosen_mutation=f"{chosen_family}_obfuscation",
            chosen_agents=chosen_agents,
            estimated_cost=round(min(0.005, budget_usd * 0.01), 4),
            estimated_success_prob=0.82,
            priority_rank=1
        )
