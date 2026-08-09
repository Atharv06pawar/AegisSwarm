import pytest
from cluster.models import ClusterTask
from cluster.retry import DistributedRetryCoordinator


def test_retry_coordinator():
    """Verify DistributedRetryCoordinator attempt tracking and backoff calculation."""
    retry_coord = DistributedRetryCoordinator()
    task = ClusterTask(attack_record_id="r1", provider="openai", model="gpt-4o", max_retries=2)

    assert retry_coord.should_retry(task, RuntimeError("error 1")) is True

    retry_coord.record_attempt(task)
    assert task.retry_count == 1
    assert retry_coord.get_retry_delay(task) > 0.0

    retry_coord.record_attempt(task)
    assert task.retry_count == 2
    assert retry_coord.should_retry(task, RuntimeError("error 2")) is False
