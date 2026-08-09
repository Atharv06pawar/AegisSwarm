"""
StrategyManager module maintaining adaptive attack strategy rankings and utility weights.
"""

from typing import Dict, List, Any


class StrategyManager:
    """
    Manager maintaining utility scores and rankings across mutation strategies and agents.
    """

    def __init__(self):
        self._strategy_scores: Dict[str, float] = {
            "persona": 0.8,
            "encoding": 0.7,
            "delimiter": 0.75,
            "roleplay": 0.85,
            "indirect_injection": 0.9,
            "tool_injection": 0.85
        }

    def get_rankings(self) -> List[Dict[str, Any]]:
        """Returns strategy names ranked by historical utility score."""
        sorted_strats = sorted(self._strategy_scores.items(), key=lambda x: x[1], reverse=True)
        return [{"strategy": k, "utility_score": v} for k, v in sorted_strats]

    def update_score(self, strategy: str, reward: float, learning_rate: float = 0.1) -> float:
        """Updates strategy utility score using exponential moving average / Q-update."""
        current = self._strategy_scores.get(strategy, 0.5)
        updated = current + learning_rate * (reward - current)
        self._strategy_scores[strategy] = round(updated, 4)
        return self._strategy_scores[strategy]
