import pytest
from tests.test_execution_models import create_sample_attack_record
from swarm.factory import SwarmFactory


def test_swarm_agents_prepare():
    """Verify prepare() method on all 7 built-in agents produces valid ExecutionRequests."""
    record = create_sample_attack_record()
    context = {"target_provider": "openai", "target_model": "gpt-4o", "temperature": 0.7}

    agent_names = [
        "direct_injection",
        "indirect_injection",
        "jailbreak",
        "tool_attack",
        "leakage",
        "roleplay",
        "multi_turn"
    ]

    for name in agent_names:
        agent = SwarmFactory.create(name)
        assert agent.health()["status"] == "ok"
        assert len(agent.supported_attack_types) > 0

        req = agent.prepare(record, context=context)
        assert req.provider == "openai"
        assert req.model == "gpt-4o"
        assert req.metadata["agent_name"] == name
