"""
SwarmMetrics accumulator for tracking swarm campaign performance telemetry.
"""

from typing import Dict, List, Any
from uuid import UUID
from swarm.models import SwarmAgentResult, SwarmSummary


class SwarmMetrics:
    """
    Accumulator computing success rates, failure rates, agent contributions,
    provider usage distributions, latencies, adaptive learning metrics, and costs for a swarm run.
    """

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """Resets all metrics accumulators."""
        self.agent_results: List[SwarmAgentResult] = []
        self.provider_usage: Dict[str, int] = {}
        self.agent_contributions: Dict[str, int] = {}
        self.total_cost: float = 0.0
        self.total_latency_ms: float = 0.0
        
        # Adaptive metric counters
        self.mutated_attempts: int = 0
        self.mutated_successes: int = 0
        self.retried_attempts: int = 0
        self.retried_successes: int = 0
        self.total_attempts: int = 0
        self.baseline_success_rate: float = 0.0
        self.strategies_used: set = set()

    def record(self, result: SwarmAgentResult, cost: float = 0.0, is_mutated: bool = False, is_retry: bool = False, strategy_name: str = "") -> None:
        """
        Accumulates a single SwarmAgentResult item into metrics.
        """
        self.agent_results.append(result)
        self.total_attempts += 1
        
        self.provider_usage[result.provider] = self.provider_usage.get(result.provider, 0) + 1
        self.agent_contributions[result.agent_name] = self.agent_contributions.get(result.agent_name, 0) + 1
        
        self.total_cost += cost
        self.total_latency_ms += result.execution_time_ms

        if is_mutated:
            self.mutated_attempts += 1
            if result.attack_success:
                self.mutated_successes += 1

        if is_retry:
            self.retried_attempts += 1
            if result.attack_success:
                self.retried_successes += 1

        if strategy_name:
            self.strategies_used.add(strategy_name)

    def summary(self) -> SwarmSummary:
        """
        Computes a SwarmSummary data model.
        """
        total = len(self.agent_results)
        if total == 0:
            return SwarmSummary()

        successes = sum(1 for r in self.agent_results if r.attack_success)
        failures = total - successes

        success_rate = successes / total
        mutation_success_rate = (self.mutated_successes / self.mutated_attempts) if self.mutated_attempts > 0 else 0.0
        retry_success_rate = (self.retried_successes / self.retried_attempts) if self.retried_attempts > 0 else 0.0
        learning_gain = max(0.0, success_rate - self.baseline_success_rate)
        average_attempts = round(self.total_attempts / total, 2)
        strategy_diversity = round(len(self.strategies_used) / max(1, total), 2)

        return SwarmSummary(
            success_rate=round(success_rate, 4),
            failure_rate=round(failures / total, 4),
            provider_distribution=dict(self.provider_usage),
            attack_distribution=dict(self.agent_contributions),
            evaluator_distribution={},
            cost=round(self.total_cost, 6),
            latency=round(self.total_latency_ms, 2),
            mutation_success_rate=round(mutation_success_rate, 4),
            retry_success_rate=round(retry_success_rate, 4),
            learning_gain=round(learning_gain, 4),
            average_attempts=average_attempts,
            strategy_diversity=strategy_diversity
        )
