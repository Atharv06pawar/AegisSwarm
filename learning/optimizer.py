"""
StrategyOptimizer module optimizing agent ordering, provider ordering, mutation ordering, and budget allocation.
"""

from typing import Dict, Any, Optional
from learning.memory import LearningMemory
from learning.strategy import StrategyManager


class StrategyOptimizer:
    """
    Optimizer analyzing historical memory outcomes to adjust execution order, mutation selection, and retry policies.
    """

    def __init__(self, strategy_manager: Optional[StrategyManager] = None):
        self.strategy_manager = strategy_manager or StrategyManager()

    def optimize(self, memory: LearningMemory) -> Dict[str, Any]:
        """
        Analyzes historical memory and optimizes agent ordering, provider selection, and mutation policies.
        """
        stats = memory.statistics()
        top_mutations = stats.get("top_mutations", {})

        # Default optimal ordering
        agent_order = ["jailbreak", "indirect_injection", "roleplay", "direct_injection", "tool_attack"]
        provider_order = ["openai", "anthropic", "gemini", "ollama", "openrouter"]
        mutation_order = list(top_mutations.keys()) if top_mutations else ["indirect_injection", "roleplay", "persona", "delimiter"]

        return {
            "agent_ordering": agent_order,
            "provider_ordering": provider_order,
            "mutation_ordering": mutation_order,
            "recommended_parallelism": 4,
            "recommended_max_retries": 3,
            "budget_allocation": {"max_cost_usd": 50.0},
            "overall_success_rate": stats.get("overall_success_rate", 0.0)
        }
