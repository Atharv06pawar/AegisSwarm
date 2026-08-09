import pytest
from campaign.models import CampaignBudget
from campaign.budget import CampaignBudgetController
from campaign.exceptions import CampaignBudgetExceeded


def test_budget_controller_cost_calculation():
    """Verify cost calculation per provider."""
    ctrl = CampaignBudgetController()
    cost_openai = ctrl.calculate_cost(1000, provider="openai")
    assert cost_openai == 0.002

    cost_ollama = ctrl.calculate_cost(1000, provider="ollama")
    assert cost_ollama == 0.0


def test_budget_controller_record_spend_and_limit():
    """Verify budget recording and limit exceedance exception."""
    ctrl = CampaignBudgetController()
    budget = CampaignBudget(max_cost_usd=0.01)

    assert ctrl.check_budget_available(budget, estimated_tokens=1000, provider="openai") is True

    # Spend within limit
    ctrl.record_spend(budget, tokens_used=1000, provider="openai")
    assert budget.current_cost_usd == 0.002

    # Exceed limit
    with pytest.raises(CampaignBudgetExceeded, match="Budget limit exceeded"):
        ctrl.record_spend(budget, tokens_used=10000, provider="openai")
