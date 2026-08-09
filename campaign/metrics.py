"""
CampaignMetricsCollector for computing real-time and aggregate campaign performance telemetry.
"""

import time
import math
from typing import Dict, List, Any, Optional
from campaign.models import CampaignMetrics


class CampaignMetricsCollector:
    """
    Accumulator computing throughput, latency percentiles (P95, P99),
    tokens consumed, USD costs, retries, mutations, and learning gain.
    """

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.start_time: float = time.perf_counter()
        self.total_attacks: int = 0
        self.completed_attacks: int = 0
        self.failed_attacks: int = 0
        self.running_attacks: int = 0
        self.queued_attacks: int = 0
        self.provider_usage: Dict[str, int] = {}
        self.latencies_ms: List[float] = []
        self.total_tokens: int = 0
        self.total_cost_usd: float = 0.0
        self.retry_count: int = 0
        self.mutation_count: int = 0
        self.evaluation_count: int = 0
        self.baseline_success_rate: float = 0.0
        self.current_success_rate: float = 0.0

    def record_attack(
        self,
        provider: str,
        success: bool,
        latency_ms: float,
        tokens: int = 0,
        cost: float = 0.0,
        is_retry: bool = False,
        is_mutated: bool = False
    ) -> None:
        """Accumulates execution and evaluation telemetry."""
        self.completed_attacks += 1
        if not success:
            self.failed_attacks += 1
            
        self.provider_usage[provider] = self.provider_usage.get(provider, 0) + 1
        self.latencies_ms.append(latency_ms)
        self.total_tokens += tokens
        self.total_cost_usd += cost
        self.evaluation_count += 1

        if is_retry:
            self.retry_count += 1

        if is_mutated:
            self.mutation_count += 1

    def compute_metrics(self) -> CampaignMetrics:
        """Computes a CampaignMetrics data model with P95/P99 latency calculations."""
        total = self.completed_attacks
        duration_ms = (time.perf_counter() - self.start_time) * 1000.0
        duration_min = max(duration_ms / 60000.0, 0.001)

        attacks_per_min = round(total / duration_min, 2)
        avg_latency = round(sum(self.latencies_ms) / max(len(self.latencies_ms), 1), 2)

        sorted_latencies = sorted(self.latencies_ms) if self.latencies_ms else [0.0]
        n = len(sorted_latencies)
        p95_idx = min(math.ceil(0.95 * n) - 1, n - 1)
        p99_idx = min(math.ceil(0.99 * n) - 1, n - 1)

        p95_latency = round(sorted_latencies[max(0, p95_idx)], 2)
        p99_latency = round(sorted_latencies[max(0, p99_idx)], 2)

        avg_cost = round(self.total_cost_usd / max(total, 1), 6)
        learning_gain = max(0.0, round(self.current_success_rate - self.baseline_success_rate, 4))

        return CampaignMetrics(
            total_attacks=self.total_attacks,
            completed_attacks=self.completed_attacks,
            failed_attacks=self.failed_attacks,
            running_attacks=self.running_attacks,
            queued_attacks=self.queued_attacks,
            provider_usage=dict(self.provider_usage),
            average_latency=avg_latency,
            p95_latency=p95_latency,
            p99_latency=p99_latency,
            average_cost=avg_cost,
            tokens_consumed=self.total_tokens,
            attacks_per_minute=attacks_per_min,
            campaign_duration_ms=round(duration_ms, 2),
            retry_count=self.retry_count,
            mutation_count=self.mutation_count,
            evaluation_count=self.evaluation_count,
            learning_gain=learning_gain
        )
