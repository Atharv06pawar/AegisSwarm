"""
TelemetryMetricsCollector for tracking system counter metrics and latency observations.
"""

import threading
from typing import Dict, List, Any


class TelemetryMetricsCollector:
    """
    Thread-safe metrics accumulator tracking requests, latencies, failures,
    tokens, costs, retries, refusal rates, leakage rates, and jailbreak rates.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self.reset()

    def reset(self) -> None:
        """Resets all metrics counters and latency lists."""
        with self._lock:
            self._counters: Dict[str, float] = {
                "requests": 0.0,
                "campaign_throughput": 0.0,
                "records_ingested": 0.0,
                "provider_failures": 0.0,
                "token_usage": 0.0,
                "cost_usd": 0.0,
                "retry_count": 0.0,
                "attacks_total": 0.0,
                "attacks_successful": 0.0,
                "refusals_total": 0.0,
                "leakages_total": 0.0,
                "jailbreaks_total": 0.0
            }
            self._observations: Dict[str, List[float]] = {
                "provider_latency": [],
                "attack_latency": [],
                "evaluation_latency": []
            }

    def increment(self, name: str, value: float = 1.0) -> None:
        """Increments a counter metric."""
        with self._lock:
            self._counters[name] = self._counters.get(name, 0.0) + value

    def observe(self, name: str, value: float) -> None:
        """Records a numerical measurement (e.g. latency observation)."""
        with self._lock:
            if name not in self._observations:
                self._observations[name] = []
            self._observations[name].append(value)

    def summary(self) -> Dict[str, Any]:
        """Computes summary rates, averages, and counters snapshot."""
        with self._lock:
            total_attacks = max(self._counters.get("attacks_total", 0.0), 1.0)
            
            success_rate = round(self._counters.get("attacks_successful", 0.0) / total_attacks, 4)
            refusal_rate = round(self._counters.get("refusals_total", 0.0) / total_attacks, 4)
            leakage_rate = round(self._counters.get("leakages_total", 0.0) / total_attacks, 4)
            jailbreak_rate = round(self._counters.get("jailbreaks_total", 0.0) / total_attacks, 4)

            avg_provider_lat = (
                sum(self._observations["provider_latency"]) / max(len(self._observations["provider_latency"]), 1)
            )
            avg_attack_lat = (
                sum(self._observations["attack_latency"]) / max(len(self._observations["attack_latency"]), 1)
            )

            return {
                "counters": dict(self._counters),
                "rates": {
                    "attack_success_rate": success_rate,
                    "refusal_rate": refusal_rate,
                    "leakage_rate": leakage_rate,
                    "jailbreak_rate": jailbreak_rate
                },
                "average_latencies_ms": {
                    "provider_latency": round(avg_provider_lat, 2),
                    "attack_latency": round(avg_attack_lat, 2)
                }
            }
