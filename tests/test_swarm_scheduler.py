import pytest
from tests.test_execution_models import create_sample_attack_record
from swarm.scheduler import SwarmScheduler
from swarm.exceptions import SchedulerError


def test_swarm_scheduler_queue_building():
    """Verify SwarmScheduler schedules attack queue and allows iteration."""
    record = create_sample_attack_record()
    plan = [("jailbreak", record)]

    scheduler = SwarmScheduler()
    queue = scheduler.schedule(plan)

    assert len(queue) == 1
    assert queue[0][0] == "jailbreak"

    items = list(scheduler.iter_queue())
    assert len(items) == 1
    assert items[0][0] == "jailbreak"


def test_swarm_scheduler_empty_plan_raises_error():
    """Verify scheduling an empty plan raises SchedulerError."""
    scheduler = SwarmScheduler()
    with pytest.raises(SchedulerError, match="empty attack plan"):
        scheduler.schedule([])
