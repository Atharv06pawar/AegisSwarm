import pytest
from swarm.retry import RetryPolicy


def test_retry_policy_eligibility_and_backoff():
    """Verify RetryPolicy eligibility checks and exponential backoff calculations."""
    policy = RetryPolicy(max_attempts=3, backoff_factor=2.0, initial_backoff_sec=1.0)
    
    assert policy.is_eligible_for_retry("attack-1", attempt_count=1) is True
    assert policy.is_eligible_for_retry("attack-1", attempt_count=2) is True
    assert policy.is_eligible_for_retry("attack-1", attempt_count=3) is False

    # Refusal detected -> not eligible for un-mutated retry
    assert policy.is_eligible_for_retry("attack-1", attempt_count=1, refusal_detected=True) is False

    assert policy.get_next_backoff_sec(1) == 1.0
    assert policy.get_next_backoff_sec(2) == 2.0
    assert policy.get_next_backoff_sec(3) == 4.0


def test_retry_policy_history():
    """Verify recording retry attempts into history."""
    policy = RetryPolicy()
    policy.record_attempt("attack-100", attempt_num=1, success=False, reason="Rate limit")
    policy.record_attempt("attack-100", attempt_num=2, success=True, reason="Success")

    hist = policy.get_retry_history("attack-100")
    assert len(hist) == 2
    assert hist[0]["attempt"] == 1
    assert hist[1]["success"] is True
