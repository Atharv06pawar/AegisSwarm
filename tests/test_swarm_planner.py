import pytest
from tests.test_execution_models import create_sample_attack_record
from swarm.models import SwarmRequest
from swarm.planner import SequentialPlanner, ParallelPlanner
from swarm.exceptions import PlannerError


def test_sequential_planner_allocates_agents():
    """Verify SequentialPlanner maps AttackRecords to agent names based on taxonomy node."""
    record = create_sample_attack_record()
    planner = SequentialPlanner()
    
    req = SwarmRequest(target_provider="openai", attack_records=[record])
    plan = planner.plan(req)

    assert len(plan) == 1
    agent_name, rec = plan[0]
    assert agent_name == "direct_injection"
    assert rec.sample_id == record.sample_id


def test_parallel_planner():
    """Verify ParallelPlanner delegates to sequential allocation."""
    record = create_sample_attack_record()
    planner = ParallelPlanner()
    
    req = SwarmRequest(target_provider="openai", attack_records=[record])
    plan = planner.plan(req)

    assert len(plan) == 1
    assert plan[0][0] == "direct_injection"


def test_planner_empty_records_raises_error():
    """Verify planning with empty attack_records raises PlannerError."""
    planner = SequentialPlanner()
    req = SwarmRequest(target_provider="openai", attack_records=[])

    with pytest.raises(PlannerError, match="zero AttackRecords"):
        planner.plan(req)
