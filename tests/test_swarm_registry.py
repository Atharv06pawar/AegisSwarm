import pytest
from swarm.base import BaseSwarmAgent
from swarm.registry import SwarmRegistry
from swarm.exceptions import AgentNotFound
from core.schema import AttackRecord
from execution.models import ExecutionRequest


class MockSwarmAgent(BaseSwarmAgent):
    @property
    def name(self) -> str:
        return "mock_agent"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def supported_attack_types(self) -> list[str]:
        return ["AUAO-PI-*"]

    def health(self) -> dict:
        return {"status": "ok"}

    def prepare(self, record: AttackRecord, context: dict = None) -> ExecutionRequest:
        return ExecutionRequest(attack_record=record, provider="openai")


def test_swarm_registry_register_and_list():
    """Verify manual agent registration and discovery."""
    SwarmRegistry.clear()
    SwarmRegistry.register(MockSwarmAgent, name="mock_agent")

    agents = SwarmRegistry.list_agents()
    assert "mock_agent" in agents

    cls = SwarmRegistry.get_agent("mock_agent")
    assert cls is MockSwarmAgent


def test_swarm_registry_unregister():
    """Verify unregistering an agent."""
    SwarmRegistry.clear()
    SwarmRegistry.register(MockSwarmAgent, name="mock_agent")
    assert "mock_agent" in SwarmRegistry.list_agents()

    SwarmRegistry.unregister("mock_agent")
    assert "mock_agent" not in SwarmRegistry.list_agents()


def test_swarm_registry_not_found():
    """Verify requesting an unregistered agent raises AgentNotFound exception."""
    SwarmRegistry.clear()
    with pytest.raises(AgentNotFound, match="non_existent_agent"):
        SwarmRegistry.get_agent("non_existent_agent")


def test_swarm_registry_discovery():
    """Verify dynamic discovery of built-in agents in swarm/agents/."""
    SwarmRegistry.clear()
    discovered = SwarmRegistry.discover()

    assert "direct_injection" in discovered
    assert "indirect_injection" in discovered
    assert "jailbreak" in discovered
    assert "tool_attack" in discovered
    assert "leakage" in discovered
    assert "roleplay" in discovered
    assert "multi_turn" in discovered
