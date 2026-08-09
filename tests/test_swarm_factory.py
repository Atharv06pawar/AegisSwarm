import pytest
from swarm.factory import SwarmFactory
from swarm.base import BaseSwarmAgent
from swarm.agents.direct_injection import DirectInjectionAgent
from swarm.agents.indirect_injection import IndirectInjectionAgent
from swarm.agents.jailbreak import JailbreakAgent
from swarm.agents.tool_attack import ToolAttackAgent
from swarm.agents.leakage import LeakageAgent
from swarm.agents.roleplay import RoleplayAgent
from swarm.agents.multi_turn import MultiTurnAgent


def test_swarm_factory_creates_agents():
    """Verify SwarmFactory creates instances of all built-in attacker agents."""
    agents = [
        ("direct_injection", DirectInjectionAgent),
        ("indirect_injection", IndirectInjectionAgent),
        ("jailbreak", JailbreakAgent),
        ("tool_attack", ToolAttackAgent),
        ("leakage", LeakageAgent),
        ("roleplay", RoleplayAgent),
        ("multi_turn", MultiTurnAgent)
    ]

    for agent_name, expected_cls in agents:
        instance = SwarmFactory.create(agent_name)
        assert isinstance(instance, expected_cls)
        assert isinstance(instance, BaseSwarmAgent)
        assert instance.name == agent_name
        assert instance.health()["status"] == "ok"
