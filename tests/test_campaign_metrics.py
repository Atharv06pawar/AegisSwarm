import pytest
from campaign.metrics import CampaignMetricsCollector


def test_campaign_metrics_collector():
    """Verify CampaignMetricsCollector latency percentile and throughput computations."""
    collector = CampaignMetricsCollector()

    for i in range(1, 101):
        collector.record_attack(
            provider="openai" if i % 2 == 0 else "anthropic",
            success=(i % 3 != 0),
            latency_ms=float(i * 10),
            tokens=100,
            cost=0.0002
        )

    metrics = collector.compute_metrics()
    assert metrics.completed_attacks == 100
    assert metrics.failed_attacks == 33
    assert metrics.tokens_consumed == 10000
    assert metrics.average_cost == 0.0002
    assert metrics.p95_latency > 900.0
    assert metrics.p99_latency >= 990.0
    assert metrics.provider_usage["openai"] == 50
    assert metrics.provider_usage["anthropic"] == 50
