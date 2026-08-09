"""
CampaignBudgetController module for AegisSwarm Distributed Campaign Engine.
Enforces cost and token spending limits with provider-specific pricing.
"""

import logging
from typing import Dict, Optional
from campaign.models import CampaignBudget
from campaign.exceptions import CampaignBudgetExceeded

logger = logging.getLogger(__name__)


class CampaignBudgetController:
    """
    Budget enforcement controller tracking token usage, USD expenditures, daily limits,
    and provider-specific cost calculations.
    """

    DEFAULT_PRICING_PER_1K_TOKENS: Dict[str, float] = {
        "openai": 0.002,
        "anthropic": 0.003,
        "gemini": 0.0015,
        "ollama": 0.0,
        "openrouter": 0.002
    }

    def __init__(self, custom_pricing: Optional[Dict[str, float]] = None):
        self.pricing = dict(self.DEFAULT_PRICING_PER_1K_TOKENS)
        if custom_pricing:
            self.pricing.update(custom_pricing)

    def calculate_cost(self, tokens: int, provider: str = "openai") -> float:
        """
        Computes USD cost for a token expenditure given a target provider.
        """
        rate = self.pricing.get(provider.lower(), 0.002)
        return round((tokens / 1000.0) * rate, 6)

    def check_budget_available(self, budget: CampaignBudget, estimated_tokens: int = 500, provider: str = "openai") -> bool:
        """
        Checks whether sufficient budget remains to execute an attack batch.
        """
        estimated_cost = self.calculate_cost(estimated_tokens, provider)
        if budget.current_cost_usd + estimated_cost > budget.max_cost_usd:
            return False
        if budget.current_tokens + estimated_tokens > budget.max_tokens:
            return False
        return True

    def record_spend(
        self,
        budget: CampaignBudget,
        tokens_used: int,
        provider: str = "openai",
        custom_cost: Optional[float] = None
    ) -> CampaignBudget:
        """
        Deducts spend from campaign budget and checks for limit exceedance.
        
        Args:
            budget (CampaignBudget): Current budget model.
            tokens_used (int): Tokens consumed.
            provider (str): Provider name.
            custom_cost (Optional[float]): Optional override cost.
            
        Returns:
            CampaignBudget: Updated budget model.
            
        Raises:
            CampaignBudgetExceeded: If budget ceiling is breached.
        """
        cost = custom_cost if custom_cost is not None else self.calculate_cost(tokens_used, provider)
        
        budget.current_cost_usd = round(budget.current_cost_usd + cost, 6)
        budget.current_tokens += tokens_used

        logger.info(
            f"Recorded spend: ${cost:.6f} ({tokens_used} tokens for '{provider}'). "
            f"Total spend: ${budget.current_cost_usd:.4f} / ${budget.max_cost_usd:.2f}"
        )

        if budget.current_cost_usd > budget.max_cost_usd:
            raise CampaignBudgetExceeded("unknown", budget.current_cost_usd, budget.max_cost_usd)

        return budget

    def is_budget_exceeded(self, budget: CampaignBudget) -> bool:
        """
        Checks if budget limit has been reached.
        """
        return budget.current_cost_usd >= budget.max_cost_usd or budget.current_tokens >= budget.max_tokens

    def get_remaining_budget_usd(self, budget: CampaignBudget) -> float:
        """
        Returns remaining USD budget balance.
        """
        return max(0.0, round(budget.max_cost_usd - budget.current_cost_usd, 4))
