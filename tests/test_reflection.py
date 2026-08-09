"""
Unit tests for ReflectionEngine in reasoning package.
"""

from reasoning.reflection import ReflectionEngine


def test_reflection_engine_outcomes():
    engine = ReflectionEngine()

    success_ref = engine.reflect(campaign_id="cmp-1", attack_id="atk-1", outcome_success=True)
    assert "persona" in success_ref.what_worked.lower() or "framing" in success_ref.what_worked.lower()

    failure_ref = engine.reflect(campaign_id="cmp-1", attack_id="atk-2", outcome_success=False)
    assert "refusal" in failure_ref.what_failed.lower() or "safety" in failure_ref.what_failed.lower()
