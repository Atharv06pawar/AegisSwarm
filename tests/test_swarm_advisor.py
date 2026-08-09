import pytest
from tests.test_execution_models import create_sample_attack_record
from swarm.memory import SwarmMemory
from swarm.advisor import StrategyAdvisor


def test_strategy_advisor_advise_and_mutate():
    """Verify StrategyAdvisor recommends an agent and mutates AttackRecord based on memory state."""
    record = create_sample_attack_record()
    memory = SwarmMemory()
    memory.append_to_list("failed_attacks", "sample-1")
    memory.append_to_list("failed_attacks", "sample-2")

    advisor = StrategyAdvisor()
    agent_name, mutated_record = advisor.advise_and_mutate(record, memory)

    assert agent_name in ["roleplay", "direct_injection", "jailbreak"]
    assert mutated_record.sample_id != record.sample_id
    assert len(mutated_record.turns) == len(record.turns)
