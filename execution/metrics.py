"""
ExecutionMetrics tracker for AegisSwarm Attack Execution Engine.
"""

from typing import Dict, Any
from execution.models import ExecutionResult


class ExecutionMetrics:
    """
    In-memory metrics accumulator for attack executions.
    Tracks latency, duration, token usage, estimated cost, provider retries, timeouts, and execution counts.
    """

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """Resets all metrics counters to zero."""
        self.total_executions: int = 0
        self.total_successes: int = 0
        self.total_failures: int = 0
        self.total_timeouts: int = 0
        self.total_retries: int = 0
        
        self.total_latency_ms: float = 0.0
        self.total_duration_ms: float = 0.0
        
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_tokens: int = 0
        self.total_cost: float = 0.0

    def record(self, result: ExecutionResult) -> None:
        """
        Accumulates metrics from a finished ExecutionResult.
        
        Args:
            result (ExecutionResult): Execution result payload.
        """
        self.total_executions += 1
        
        if result.status == "completed":
            self.total_successes += 1
        elif result.status == "timed_out":
            self.total_timeouts += 1
            self.total_failures += 1
        else:
            self.total_failures += 1

        self.total_retries += result.retry_count
        self.total_latency_ms += result.latency_ms
        self.total_duration_ms += result.duration_ms
        
        self.total_prompt_tokens += result.prompt_tokens
        self.total_completion_tokens += result.completion_tokens
        self.total_tokens += result.total_tokens
        self.total_cost += result.estimated_cost

    def summary(self) -> Dict[str, Any]:
        """
        Computes summary statistics.
        
        Returns:
            Dict[str, Any]: Summary dictionary with averages and totals.
        """
        avg_latency_ms = (self.total_latency_ms / self.total_executions) if self.total_executions > 0 else 0.0
        avg_duration_ms = (self.total_duration_ms / self.total_executions) if self.total_executions > 0 else 0.0

        return {
            "total_executions": self.total_executions,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "total_timeouts": self.total_timeouts,
            "total_retries": self.total_retries,
            "avg_latency_ms": round(avg_latency_ms, 2),
            "avg_duration_ms": round(avg_duration_ms, 2),
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 6)
        }
