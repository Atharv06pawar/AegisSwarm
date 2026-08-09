import pytest
from learning.memory import LearningMemory
from learning.planner import AdaptivePlanner


def test_adaptive_planner_create_plan():
    """Verify AdaptivePlanner generates adaptive AttackPlan models."""
    memory = LearningMemory()
    planner = AdaptivePlanner(memory=memory)

    plan = planner.create_plan(target_provider="openai", budget_usd=20.0)
    assert plan.target_provider == "openai"
    assert plan.estimated_cost <= 20.0
    assert plan.estimated_success_prob > 0.0
    assert len(plan.chosen_agents) >= 1
