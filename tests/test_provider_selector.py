"""
Unit tests for ProviderSelector in reasoning package.
"""

from reasoning.provider_selector import ProviderSelector


def test_provider_selector_recommendation():
    selector = ProviderSelector()
    rec = selector.select_provider(target_provider="anthropic", target_model="claude-3-5-sonnet")

    assert rec.recommended_provider == "anthropic"
    assert rec.recommended_model == "claude-3-5-sonnet"
    assert rec.confidence_score > 0.5
    assert "latency" in rec.rationale.lower() or "throughput" in rec.rationale.lower()
