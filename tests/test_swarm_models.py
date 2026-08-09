import pytest
from uuid import uuid4
from tests.test_execution_models import create_sample_attack_record
from swarm.models import SwarmRequest, SwarmResult, SwarmAgentResult, SwarmSummary


def test_swarm_request_model():
    """Verify SwarmRequest model structure and defaults."""
    record = create_sample_attack_record()
    req = SwarmRequest(
        target_provider="openai",
        target_model="gpt-4o",
        attack_records=[record]
    )
    assert req.target_provider == "openai"
    assert req.target_model == "gpt-4o"
    assert len(req.attack_records) == 1
    assert req.swarm_id is not None


def test_swarm_agent_result_model():
    """Verify SwarmAgentResult model validation."""
    exec_id = uuid4()
    eval_id = uuid4()

    agent_res = SwarmAgentResult(
        agent_name="jailbreak",
        execution_id=exec_id,
        evaluation_id=eval_id,
        attack_success=True,
        confidence=0.95,
        severity=9.0,
        provider="openai",
        model="gpt-4o",
        execution_time_ms=120.5
    )
    assert agent_res.agent_name == "jailbreak"
    assert agent_res.attack_success is True
    assert agent_res.severity == 9.0


def test_swarm_result_and_summary_models():
    """Verify SwarmResult and SwarmSummary models."""
    swarm_id = uuid4()
    res = SwarmResult(
        swarm_id=swarm_id,
        status="completed",
        total_agents=2,
        completed_agents=2,
        failed_agents=0,
        total_attacks=2,
        successful_attacks=1,
        average_confidence=0.9,
        average_severity=4.5
    )
    assert res.swarm_id == swarm_id
    assert res.status == "completed"

    summary = SwarmSummary(
        success_rate=0.5,
        failure_rate=0.0,
        provider_distribution={"openai": 2},
        attack_distribution={"jailbreak": 1, "direct_injection": 1}
    )
    assert summary.success_rate == 0.5
    assert summary.provider_distribution["openai"] == 2
